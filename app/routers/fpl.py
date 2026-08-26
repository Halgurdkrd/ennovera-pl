"""FastAPI Router for Fantasy Premier League Endpoints in ennovera-pl."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.services.fpl_service import fpl_service
from app.schemas.fpl import FPLGameweekPlan, FPLTransferRecommendation, FPLCaptainResponse, FPLChipStatusItem

router = APIRouter(prefix="/api/v1/fpl", tags=["Fantasy Premier League"])

@router.get("/gameweek/plan", response_model=FPLGameweekPlan)
def get_gameweek_plan(
    gw: int = Query(1, ge=1, le=38, description="Gameweek (1-38)"),
    season: str = Query("2025-26", description="Season calendar")
):
    """Retrieve full master Gameweek Plan (Starting XI, Bench, Captain, Transfers, and Chip Guidance)."""
    return fpl_service.get_gameweek_plan(season=season, gw=gw)

@router.get("/squad/current")
def get_current_squad(
    gw: int = Query(1, ge=1, le=38, description="Gameweek"),
    season: str = Query("2025-26", description="Season calendar")
):
    """Retrieve Ennovera's recommended 15-player squad and starting lineup for the gameweek."""
    plan = fpl_service.get_gameweek_plan(season=season, gw=gw)
    return {
        "season": season,
        "gameweek": gw,
        "model_version": plan["model_version"],
        "formation": plan["formation"],
        "starting_xi": plan["starting_xi"],
        "bench": plan["bench"],
        "captain": plan["captain"],
        "vice_captain": plan["vice_captain"]
    }

@router.get("/transfers/recommended", response_model=List[FPLTransferRecommendation])
def get_recommended_transfers(
    gw: int = Query(1, ge=1, le=38, description="Target Gameweek"),
    season: str = Query("2025-26", description="Season calendar")
):
    """Retrieve optimal transfer recommendations derived from the multi-player opportunity scanner."""
    plan = fpl_service.get_gameweek_plan(season=season, gw=gw)
    return plan["recommended_transfers"]

@router.get("/captain/recommended", response_model=FPLCaptainResponse)
def get_captain_recommendation(
    gw: int = Query(1, ge=1, le=38, description="Target Gameweek"),
    season: str = Query("2025-26", description="Season calendar")
):
    """Retrieve the specialized captain and vice-captain recommendation with top alternatives."""
    return fpl_service.get_captain_recommendation(season=season, gw=gw)

@router.get("/chips/status", response_model=List[FPLChipStatusItem])
def get_chips_status(
    current_gw: int = Query(1, ge=1, le=38, description="Current Gameweek"),
    season: str = Query("2025-26", description="Season calendar")
):
    """Retrieve season-legal chip inventory, availability, and reservation recommendations."""
    return fpl_service.get_chips_status(season=season, current_gw=current_gw)

@router.get("/rules/current")
def get_season_rules(
    season: str = Query("2025-26", description="Season calendar")
):
    """Retrieve official season regulations and chip inventories."""
    return fpl_service.get_season_rules(season=season)

