"""Pydantic Schema Definitions for Premier League Endpoints."""
from typing import Optional, Literal
from pydantic import BaseModel, Field

class PLFixturePrediction(BaseModel):
    fixture_id: str = Field(..., description="Unique fixture identifier")
    season: str = Field(..., description="Season calendar (e.g. 2025-26, 2026-27)")
    gameweek: int = Field(..., ge=1, le=38, description="Premier League Gameweek number")
    home_team: str = Field(..., description="Home club name")
    away_team: str = Field(..., description="Away club name")
    kickoff: str = Field(..., description="ISO 8601 Kickoff timestamp")
    home_prob: float = Field(..., ge=0.0, le=1.0, description="Home win probability")
    draw_prob: float = Field(..., ge=0.0, le=1.0, description="Draw probability")
    away_prob: float = Field(..., ge=0.0, le=1.0, description="Away win probability")
    predicted_outcome: Literal["H", "D", "A"] = Field(..., description="Predicted match outcome")
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="Confidence rating based on maximum probability")
    strong_pick: bool = Field(..., description="True if top probability >= 0.60")
    model_version: str = Field(..., description="Inference model version")
    generated_at: str = Field(..., description="Timestamp of inference generation")
    data_cutoff: str = Field(..., description="Information cutoff timestamp/rule")

class PLHealthResponse(BaseModel):
    status: str
    pl_model_loaded: bool
    fpl_model_loaded: bool
    version: str
    model_architecture: str

