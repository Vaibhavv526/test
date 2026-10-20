"""
API routes for Compatibility Rankings.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db, ProfileDB, DateSimulationDB
from app.models import RankedMatch, ProfileResponse, ProfileAnalysis
from app.api.profiles import _db_to_response

logger = logging.getLogger("agentic_dating.api.rankings")
router = APIRouter(prefix="/api/rankings", tags=["Rankings"])


def _calculate_trait_compatibility(analysis_a: ProfileAnalysis, analysis_b: ProfileAnalysis) -> dict:
    """
    Computes a deterministic baseline compatibility assessment between two profiles
    based on values, needs, communication style, and dealbreakers.
    """
    # 1. Values alignment
    a_vals = set(v.lower().strip() for v in analysis_a.values)
    b_vals = set(v.lower().strip() for v in analysis_b.values)
    shared_values = a_vals & b_vals
    shared_val_count = len(shared_values)

    # 2. Hobbies & Interests affinity
    a_interests = set(i.lower().strip() for i in (analysis_a.hobbies + analysis_a.interests))
    b_interests = set(i.lower().strip() for i in (analysis_b.hobbies + analysis_b.interests))
    shared_interests = a_interests & b_interests

    # 3. Dealbreaker check
    dealbreaker_penalty = 0
    dealbreaker_frictions = []
    for d in analysis_a.dealbreakers:
        d_clean = d.lower()
        if any(d_clean in i.lower() for i in (analysis_b.hobbies + [analysis_b.communication_style])):
            dealbreaker_penalty += 20
            dealbreaker_frictions.append(f"Potential friction around: {d}")
    for d in analysis_b.dealbreakers:
        d_clean = d.lower()
        if any(d_clean in i.lower() for i in (analysis_a.hobbies + [analysis_a.communication_style])):
            dealbreaker_penalty += 20
            dealbreaker_frictions.append(f"Potential friction around: {d}")

    # Base baseline score
    base_score = 68
    score = base_score + (shared_val_count * 8) + (len(shared_interests) * 4) - dealbreaker_penalty
    score = max(35, min(97, score))

    shared_strengths = []
    if shared_values:
        shared_strengths.append(f"Shared core values: {', '.join(list(shared_values)[:2]).title()}")
    else:
        shared_strengths.append("Complementary life perspectives and mutual curiosity")

    if shared_interests:
        shared_strengths.append(f"Common pursuits: {', '.join(list(shared_interests)[:2]).title()}")
    else:
        shared_strengths.append("Engaging contrast in everyday interests")

    frictions = dealbreaker_frictions
    if not frictions:
        if score >= 80:
            frictions.append("High shared drive; will need dedicated time for quiet presence")
        else:
            frictions.append("Differing energy tempos and conversation rhythms")

    if score >= 85:
        rec = "Strong Match"
        rationale = f"Exceptional mutual resonance in values and communication harmony."
    elif score >= 72:
        rec = "Promising Spark"
        rationale = f"Solid foundation with shared curiosity and complementary strengths."
    elif score >= 55:
        rec = "Better as Friends"
        rationale = f"Great conversational chemistry, but differs on core daily needs or pace."
    else:
        rec = "Mismatched"
        rationale = f"Distinct lifestyle priorities and contrasting dealbreakers."

    return {
        "score": score,
        "rationale": rationale,
        "shared_strengths": shared_strengths,
        "frictions": frictions,
        "recommendation": rec
    }


def rank_matches(person_id: int, db: Session, limit: int = 50) -> List[RankedMatch]:
    """
    Ranks all other profiles in the database for the given person_id.
    Uses stored DateSimulation if present; otherwise computes baseline trait compatibility.
    """
    target_person = db.query(ProfileDB).filter(ProfileDB.id == person_id).first()
    if not target_person:
        raise HTTPException(status_code=404, detail="Target person not found.")

    target_analysis = ProfileAnalysis(**target_person.get_analysis_dict())

    # Get all other profiles
    other_profiles = db.query(ProfileDB).filter(ProfileDB.id != person_id).all()

    # Pre-fetch all date simulations involving target_person
    simulations = db.query(DateSimulationDB).filter(
        or_(
            DateSimulationDB.profile_a_id == person_id,
            DateSimulationDB.profile_b_id == person_id
        )
    ).all()

    sim_map = {}
    for s in simulations:
        other_id = s.profile_b_id if s.profile_a_id == person_id else s.profile_a_id
        sim_map[other_id] = s

    ranked_results: List[RankedMatch] = []

    for other in other_profiles:
        other_analysis = ProfileAnalysis(**other.get_analysis_dict())
        sim = sim_map.get(other.id)

        if sim:
            # Use data from actual simulated date
            transcript_dict = sim.get_transcript_dict()
            score = sim.compatibility_score
            rationale = sim.summary_rationale
            shared = transcript_dict.get("shared_strengths", [])
            frictions = transcript_dict.get("potential_friction_points", [])
            rec = transcript_dict.get("recommendation", "Strong Match" if score >= 80 else "Promising Spark")
            sim_id = sim.id
            has_run = True
        else:
            # Baseline compatibility prediction
            calc = _calculate_trait_compatibility(target_analysis, other_analysis)
            score = calc["score"]
            rationale = calc["rationale"]
            shared = calc["shared_strengths"]
            frictions = calc["frictions"]
            rec = calc["recommendation"]
            sim_id = None
            has_run = False

        ranked_results.append(
            RankedMatch(
                target_person_id=person_id,
                match_profile=_db_to_response(other),
                compatibility_score=score,
                summary_rationale=rationale,
                shared_strengths=shared,
                potential_friction_points=frictions,
                recommendation=rec,
                date_simulation_id=sim_id,
                has_date_run=has_run
            )
        )

    # Sort descending by compatibility score
    ranked_results.sort(key=lambda x: x.compatibility_score, reverse=True)
    return ranked_results[:limit]


@router.get("/{person_id}", response_model=List[RankedMatch])
def get_ranked_matches(
    person_id: int,
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Returns a sorted list of best fits for a given person, each with compatibility score and rationale.
    """
    return rank_matches(person_id=person_id, db=db, limit=limit)
