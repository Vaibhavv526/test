"""
API routes for Simulated Agent Dates and Transcript Playback.
"""
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db, ProfileDB, DateSimulationDB
from app.models import (
    SimulateDateRequest,
    DateSimulationResponse,
    DateTranscript,
    ProfileAnalysis
)
from app.agent import agent_date

logger = logging.getLogger("agentic_dating.api.dates")
router = APIRouter(prefix="/api/dates", tags=["Simulated Dates"])


def _db_to_simulation_response(sim: DateSimulationDB) -> DateSimulationResponse:
    transcript_dict = sim.get_transcript_dict()
    transcript = DateTranscript(**transcript_dict)
    return DateSimulationResponse(
        id=sim.id,
        profile_a_id=sim.profile_a_id,
        profile_b_id=sim.profile_b_id,
        compatibility_score=sim.compatibility_score,
        summary_rationale=sim.summary_rationale,
        transcript=transcript,
        created_at=sim.created_at
    )


@router.post("/simulate", response_model=DateSimulationResponse)
def simulate_date(req: SimulateDateRequest, db: Session = Depends(get_db)):
    """
    Simulates a high-fidelity first date conversation between the AI agents of Person A and Person B.
    Evaluates compatibility score (0-100) and rationale.
    """
    if req.profile_a_id == req.profile_b_id:
        raise HTTPException(status_code=400, detail="Cannot simulate a date with oneself.")

    profile_a = db.query(ProfileDB).filter(ProfileDB.id == req.profile_a_id).first()
    profile_b = db.query(ProfileDB).filter(ProfileDB.id == req.profile_b_id).first()

    if not profile_a:
        raise HTTPException(status_code=404, detail=f"Profile A (ID {req.profile_a_id}) not found.")
    if not profile_b:
        raise HTTPException(status_code=404, detail=f"Profile B (ID {req.profile_b_id}) not found.")

    # Check for existing simulation unless force_fresh is requested
    if not req.force_fresh:
        existing = db.query(DateSimulationDB).filter(
            or_(
                and_(DateSimulationDB.profile_a_id == req.profile_a_id, DateSimulationDB.profile_b_id == req.profile_b_id),
                and_(DateSimulationDB.profile_a_id == req.profile_b_id, DateSimulationDB.profile_b_id == req.profile_a_id)
            )
        ).first()
        if existing:
            return _db_to_simulation_response(existing)

    # Perform agent date simulation via agent.py
    analysis_a = ProfileAnalysis(**profile_a.get_analysis_dict())
    analysis_b = ProfileAnalysis(**profile_b.get_analysis_dict())

    try:
        transcript = agent_date(
            profile_a=analysis_a,
            profile_b=analysis_b,
            profile_a_id=profile_a.id,
            profile_b_id=profile_b.id
        )
    except Exception as e:
        logger.error(f"Error during agent date simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Date simulation failed: {str(e)}")

    # Store simulation in DB
    simulation_db = DateSimulationDB(
        profile_a_id=profile_a.id,
        profile_b_id=profile_b.id,
        compatibility_score=transcript.compatibility_score,
        summary_rationale=transcript.summary_rationale,
        transcript_json=json.dumps(transcript.model_dump())
    )
    db.add(simulation_db)
    db.commit()
    db.refresh(simulation_db)

    return _db_to_simulation_response(simulation_db)


@router.get("/between/{profile_a_id}/{profile_b_id}", response_model=Optional[DateSimulationResponse])
def get_simulation_between(profile_a_id: int, profile_b_id: int, db: Session = Depends(get_db)):
    """Retrieve existing simulation between two specific profiles if it exists."""
    sim = db.query(DateSimulationDB).filter(
        or_(
            and_(DateSimulationDB.profile_a_id == profile_a_id, DateSimulationDB.profile_b_id == profile_b_id),
            and_(DateSimulationDB.profile_a_id == profile_b_id, DateSimulationDB.profile_b_id == profile_a_id)
        )
    ).first()
    if not sim:
        return None
    return _db_to_simulation_response(sim)


@router.get("/{sim_id}", response_model=DateSimulationResponse)
def get_simulation(sim_id: int, db: Session = Depends(get_db)):
    """Get simulation transcript by ID."""
    sim = db.query(DateSimulationDB).filter(DateSimulationDB.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Date simulation not found.")
    return _db_to_simulation_response(sim)


@router.get("", response_model=List[DateSimulationResponse])
def list_simulations(limit: int = 20, db: Session = Depends(get_db)):
    """List recent simulated dates across all profiles."""
    sims = db.query(DateSimulationDB).order_by(DateSimulationDB.created_at.desc()).limit(limit).all()
    return [_db_to_simulation_response(s) for s in sims]
