"""
Pydantic models and schemas for Agentic Dating Demo.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Profile Analysis Models
# ============================================================================

class ProfileAnalysis(BaseModel):
    """
    Structured extraction of a person's dating traits extracted from raw bio text.
    """
    name: str = Field(description="Name of the person")
    age: Optional[int] = Field(default=None, description="Age or estimated age, or None if unspecified")
    occupation: Optional[str] = Field(default=None, description="Occupation, career focus, or creative role")
    location: Optional[str] = Field(default=None, description="City, region, or travel lifestyle")
    tagline: Optional[str] = Field(default=None, description="A punchy 1-sentence vibe summary")
    needs: List[str] = Field(default_factory=list, description="Core relationship and emotional needs (e.g. intellectual sparring, emotional safety, spontaneity)")
    hobbies: List[str] = Field(default_factory=list, description="Activities and hobbies they actively enjoy")
    interests: List[str] = Field(default_factory=list, description="Broader interests, subjects, passions, or curiosities")
    values: List[str] = Field(default_factory=list, description="Core life and moral values (e.g. honesty, ambition, empathy, growth mindset)")
    communication_style: str = Field(description="Style of communication (e.g. 'Direct and witty', 'Reflective and deep', 'Playful and spontaneous')")
    dealbreakers: List[str] = Field(default_factory=list, description="Absolute red flags or incompatibilities")
    dating_intentions: Optional[str] = Field(default=None, description="Intentions (e.g. 'Long-term committed partner', 'Exploring meaningful connection')")
    personality_type_hint: Optional[str] = Field(default=None, description="Optional MBTI or personality archetype vibe")


# ============================================================================
# Simulated Date Transcript Models
# ============================================================================

class DateTurn(BaseModel):
    """
    A single turn in the simulated conversation between two agents.
    """
    speaker_name: str = Field(description="Name of the speaker")
    speaker_id: int = Field(description="Profile ID of the speaker")
    stage: str = Field(default="dialogue", description="Stage of date: Icebreaker, Values & Lifestyle, Dealbreakers & Humor, Closing")
    message: str = Field(description="The spoken dialogue out loud")
    inner_thought: Optional[str] = Field(default=None, description="Agent's private thoughts assessing compatibility during this turn")


class DateTranscript(BaseModel):
    """
    Complete simulated date transcript and final compatibility evaluation.
    """
    profile_a_id: int
    profile_b_id: int
    profile_a_name: str
    profile_b_name: str
    turns: List[DateTurn] = Field(default_factory=list, description="Chronological dialog turns between the two AI agents")
    compatibility_score: int = Field(ge=0, le=100, description="Compatibility score from 0 to 100")
    summary_rationale: str = Field(description="A concise 1-3 sentence summary of why they do or do not fit")
    shared_strengths: List[str] = Field(default_factory=list, description="Key points of shared interest, energy, or mutual values")
    potential_friction_points: List[str] = Field(default_factory=list, description="Potential areas of tension, differing pace, or lifestyle clash")
    recommendation: str = Field(default="Promising Spark", description="Recommendation: 'Strong Match', 'Promising Spark', 'Better as Friends', or 'Mismatched'")


# ============================================================================
# API Request / Response DTOs
# ============================================================================

class ProfileCreateRequest(BaseModel):
    """Intake form request payload"""
    name: Optional[str] = Field(default=None, description="Optional explicit name, otherwise extracted from text")
    raw_input: str = Field(min_length=15, description="Self-reported bio text (LinkedIn about, IG bio, dating prompt, etc.)")
    source: str = Field(default="self-reported", description="'self-reported' or 'synthetic'")


class SyntheticGenerationRequest(BaseModel):
    """Request to batch generate synthetic fictional profiles"""
    count: int = Field(default=5, ge=1, le=30, description="Number of synthetic profiles to generate")


class ProfileResponse(BaseModel):
    """Profile returned to frontend"""
    id: int
    name: str
    age: Optional[int] = None
    source: str
    raw_input: str
    avatar_url: Optional[str] = None
    analysis: ProfileAnalysis
    created_at: datetime

    class Config:
        from_attributes = True


class RankedMatch(BaseModel):
    """Compatibility ranking item for a person"""
    target_person_id: int
    match_profile: ProfileResponse
    compatibility_score: int
    summary_rationale: str
    shared_strengths: List[str] = Field(default_factory=list)
    potential_friction_points: List[str] = Field(default_factory=list)
    recommendation: str
    date_simulation_id: Optional[int] = None
    has_date_run: bool = False


class SimulateDateRequest(BaseModel):
    """Trigger date simulation between two profiles"""
    profile_a_id: int
    profile_b_id: int
    force_fresh: bool = Field(default=False, description="Whether to re-simulate if already exists")


class DateSimulationResponse(BaseModel):
    id: int
    profile_a_id: int
    profile_b_id: int
    compatibility_score: int
    summary_rationale: str
    transcript: DateTranscript
    created_at: datetime

    class Config:
        from_attributes = True
