"""
API routes for Profile Intake and Exploration.
"""
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db, ProfileDB
from app.models import ProfileCreateRequest, ProfileResponse, ProfileAnalysis, SyntheticGenerationRequest
from app.agent import analyze_profile, generate_synthetic_profiles

logger = logging.getLogger("agentic_dating.api.profiles")
router = APIRouter(prefix="/api/profiles", tags=["Profiles"])


def _db_to_response(profile_db: ProfileDB) -> ProfileResponse:
    analysis_data = profile_db.get_analysis_dict()
    analysis = ProfileAnalysis(**analysis_data) if analysis_data else ProfileAnalysis(
        name=profile_db.name,
        age=profile_db.age,
        occupation=profile_db.occupation,
        location=profile_db.location,
        tagline=None,
        needs=[],
        hobbies=[],
        interests=[],
        values=[],
        communication_style="Direct",
        dealbreakers=[]
    )
    return ProfileResponse(
        id=profile_db.id,
        name=profile_db.name,
        age=profile_db.age,
        source=profile_db.source,
        raw_input=profile_db.raw_input,
        avatar_url=profile_db.avatar_url or f"https://api.dicebear.com/7.x/notionists/svg?seed={profile_db.name.replace(' ', '')}",
        analysis=analysis,
        created_at=profile_db.created_at
    )


@router.post("/intake", response_model=ProfileResponse)
def intake_profile(req: ProfileCreateRequest, db: Session = Depends(get_db)):
    """
    Intake a self-reported participant bio text.
    Calls analyze_profile to extract rich structured traits via Claude.
    """
    if not req.raw_input or len(req.raw_input.strip()) < 10:
        raise HTTPException(status_code=400, detail="Bio text must be at least 10 characters.")

    try:
        analysis = analyze_profile(req.raw_input, fallback_name=req.name)
    except Exception as e:
        logger.error(f"Error analyzing profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze profile: {str(e)}")

    name = req.name or analysis.name or "Anonymous"
    avatar_url = f"https://api.dicebear.com/7.x/notionists/svg?seed={name.replace(' ', '')}"

    profile_db = ProfileDB(
        name=name,
        age=analysis.age,
        occupation=analysis.occupation,
        location=analysis.location,
        source=req.source or "self-reported",
        raw_input=req.raw_input,
        avatar_url=avatar_url,
        analysis_json=json.dumps(analysis.model_dump())
    )
    db.add(profile_db)
    db.commit()
    db.refresh(profile_db)

    return _db_to_response(profile_db)


@router.post("/generate-synthetic", response_model=List[ProfileResponse])
def generate_synthetic(req: SyntheticGenerationRequest, db: Session = Depends(get_db)):
    """
    Batch generate synthetic fictional profiles using Claude (or curated archetypes).
    Ensures zero real personal data needed to demo.
    """
    count = req.count
    candidates = generate_synthetic_profiles(count)
    created_profiles = []

    for item in candidates:
        name = item.get("name", "Synthetic Candidate")
        raw_input = item.get("raw_input")
        if not raw_input:
            raw_input = f"I am {name}, working in {item.get('occupation', 'Tech')}. Passionate about {', '.join(item.get('interests', ['art', 'science']))}."

        analysis = ProfileAnalysis(
            name=name,
            age=item.get("age"),
            occupation=item.get("occupation"),
            location=item.get("location"),
            tagline=item.get("tagline"),
            needs=item.get("needs", []),
            hobbies=item.get("hobbies", []),
            interests=item.get("interests", []),
            values=item.get("values", []),
            communication_style=item.get("communication_style", "Warm and engaging"),
            dealbreakers=item.get("dealbreakers", []),
            dating_intentions=item.get("dating_intentions"),
            personality_type_hint=item.get("personality_type_hint")
        )

        avatar_url = f"https://api.dicebear.com/7.x/notionists/svg?seed={name.replace(' ', '')}"
        profile_db = ProfileDB(
            name=name,
            age=item.get("age"),
            occupation=item.get("occupation"),
            location=item.get("location"),
            source="synthetic",
            raw_input=raw_input,
            avatar_url=avatar_url,
            analysis_json=json.dumps(analysis.model_dump())
        )
        db.add(profile_db)
        created_profiles.append(profile_db)

    db.commit()
    for p in created_profiles:
        db.refresh(p)

    return [_db_to_response(p) for p in created_profiles]


@router.get("", response_model=List[ProfileResponse])
def list_profiles(
    source: Optional[str] = Query(None, description="Filter by 'self-reported' or 'synthetic'"),
    search: Optional[str] = Query(None, description="Search by name or occupation"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all profiles with optional search and source filtering."""
    query = db.query(ProfileDB)
    if source:
        query = query.filter(ProfileDB.source == source)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter((ProfileDB.name.ilike(search_fmt)) | (ProfileDB.occupation.ilike(search_fmt)))

    profiles = query.order_by(ProfileDB.created_at.desc()).limit(limit).all()
    return [_db_to_response(p) for p in profiles]


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Retrieve full profile details with structured traits."""
    profile_db = db.query(ProfileDB).filter(ProfileDB.id == profile_id).first()
    if not profile_db:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _db_to_response(profile_db)


@router.delete("/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Delete a profile and its associated date simulations."""
    profile_db = db.query(ProfileDB).filter(ProfileDB.id == profile_id).first()
    if not profile_db:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile_db)
    db.commit()
    return {"status": "success", "message": f"Profile {profile_id} deleted."}
