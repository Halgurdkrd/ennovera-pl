"""Pydantic Schema Definitions for Premier League Endpoints."""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class PLFixturePrediction(BaseModel):
    fixture_id: str = Field(..., description="Unique fixture identifier")
    competition: str = Field("PL2026-27", description="Competition tag")
    season: str = Field("2026-27", description="Season calendar")
    gameweek: int = Field(..., ge=1, le=38, description="Premier League Gameweek number")
    home_team: str = Field(..., description="Canonical Home club name")
    away_team: str = Field(..., description="Canonical Away club name")
    kickoff: str = Field(..., description="ISO 8601 Kickoff timestamp")
    home_prob: float = Field(..., ge=0.0, le=1.0, description="Home win probability")
    draw_prob: float = Field(..., ge=0.0, le=1.0, description="Draw probability")
    away_prob: float = Field(..., ge=0.0, le=1.0, description="Away win probability")
    predicted_outcome: Literal["H", "D", "A"] = Field(..., description="Predicted match outcome")
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="Confidence rating")
    strong_pick: bool = Field(False, description="True if top probability >= 0.60")
    model_public_version: str = Field("ennovera-pl-v1.0", description="Public model version")
    model_internal_version: str = Field("pl_v2_final", description="Internal provenance version")
    generated_at: str = Field(..., description="Timestamp of inference generation")
    data_cutoff: str = Field(..., description="Data cutoff boundary")
    prediction_state: str = Field("PREMATCH", description="Prediction state")


class PLTeamStanding(BaseModel):
    position: int = Field(..., ge=1, le=20, description="Projected league rank")
    team_name: str = Field(..., description="Canonical team name")
    expected_points: float = Field(..., description="Projected average season points")
    expected_position: float = Field(..., description="Projected average league position")
    champion_pct: float = Field(..., ge=0.0, le=100.0, description="Title win probability percentage")
    top4_pct: float = Field(..., ge=0.0, le=100.0, description="Top-4 finish probability percentage")
    top6_pct: float = Field(..., ge=0.0, le=100.0, description="Top-6 finish probability percentage")
    relegation_pct: float = Field(..., ge=0.0, le=100.0, description="Relegation probability percentage")


class PLTableResponse(BaseModel):
    competition: str = "PL2026-27"
    season: str = "2026-27"
    simulation_runs: int = 10000
    model_version: str = "ennovera-pl-v1.0"
    generated_at: str
    standings: List[PLTeamStanding]


class PLModelInfo(BaseModel):
    model_name: str
    public_version: str
    role: Literal["PRODUCTION", "SHADOW", "LEGACY"]
    description: str
    features: List[str]
    holdout_accuracy: Optional[float] = None
    log_loss: Optional[float] = None


class PLModelsResponse(BaseModel):
    production_model: PLModelInfo
    shadow_model: PLModelInfo
    legacy_models: List[PLModelInfo]


class PLHealthResponse(BaseModel):
    status: str
    service: str = "ennovera-pl"
    version: str = "1.0.0"
    production_model_loaded: bool
    shadow_model_loaded: bool
    season: str = "2026-27"
