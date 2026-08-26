"""FastAPI Router for Premier League Endpoints in ennovera-pl."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.services.pl_service import pl_service
from app.schemas.pl import (
    PLFixturePrediction,
    PLTableResponse,
    PLModelsResponse,
    PLHealthResponse
)

router = APIRouter(prefix="/api/v1/pl", tags=["Premier League"])


@router.get("/fixtures", response_model=List[PLFixturePrediction])
def get_fixtures(
    gw: int = Query(1, ge=1, le=38, description="Premier League Gameweek (1-38)"),
    season: str = Query("2026-27", description="Season calendar")
):
    """Retrieve canonical match predictions and outcome probabilities for a specific gameweek."""
    return pl_service.get_gameweek_fixtures(season=season, gw=gw)


@router.get("/predict", response_model=PLFixturePrediction)
def predict_fixture(
    home: str = Query(..., description="Home club name"),
    away: str = Query(..., description="Away club name"),
    gw: Optional[int] = Query(None, ge=1, le=38, description="Gameweek number"),
    season: str = Query("2026-27", description="Season calendar")
):
    """Generate real-time V2 production match prediction for any club pairing."""
    if not home or not away or home.strip().lower() == away.strip().lower():
        raise HTTPException(status_code=400, detail="Home and away teams must be distinct clubs.")
    return pl_service.predict_match(home, away, season=season, gw=gw)


@router.get("/table", response_model=PLTableResponse)
def get_league_table(
    season: str = Query("2026-27", description="Season calendar")
):
    """Retrieve Premier League standings with 10,000 Monte Carlo simulation title/top4/relegation probabilities."""
    return pl_service.get_league_table(season=season)


@router.get("/models", response_model=PLModelsResponse)
def get_models_metadata():
    """Retrieve clean public metadata for active production and shadow models."""
    return pl_service.get_models_metadata()
