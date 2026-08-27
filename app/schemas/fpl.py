"""Pydantic Schema Definitions for Fantasy Premier League Endpoints."""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class FPLPlayer(BaseModel):
    player_id: int = Field(..., description="Unique FPL player ID")
    name: str = Field(..., description="Full player name")
    web_name: Optional[str] = Field(None, description="Short web display name")
    club: str = Field(..., description="Canonical Premier League club")
    position: Literal["GK", "DEF", "MID", "FWD"] = Field(..., description="Official FPL position")
    price: float = Field(..., description="Current purchase price in £m")
    expected_points: float = Field(..., description="Projected expected points (xP)")
    expected_minutes: float = Field(..., description="Projected minutes on pitch")
    starting_prob: float = Field(..., ge=0.0, le=1.0, description="Probability of starting match")
    haul_prob: float = Field(..., ge=0.0, le=1.0, description="Calibrated probability of scoring >= 10 points")
    is_starting: bool = Field(..., description="True if selected in Starting XI")
    is_captain: bool = Field(False, description="True if selected as primary captain")
    is_vice_captain: bool = Field(False, description="True if selected as vice captain")
    bench_order: Optional[int] = Field(None, description="Bench priority order (1-4)")


class FPLTransferRecommendation(BaseModel):
    player_out: str = Field(..., description="Player recommended to sell")
    player_in: str = Field(..., description="Player recommended to buy")
    expected_gain: float = Field(..., description="Multi-GW net expected points gain")
    free_transfers_used: int = Field(..., description="Free transfers consumed (1 or 2)")
    hit_points: int = Field(0, description="Points deduction incurred for extra transfer (-4 per hit)")
    bank_after: float = Field(..., description="Remaining cash in bank (£m)")
    reason: str = Field(..., description="Tactical/fixture rationale for transfer")


class FPLChipRecommendation(BaseModel):
    action: Literal["USE", "SAVE", "USED", "LOCKED", "EXPIRED"] = Field(..., description="Recommended chip decision")
    chip_name: Optional[str] = Field(None, description="Chip to activate if action == USE")
    expected_incremental_gain: float = Field(0.0, description="Projected incremental points gain over inherited squad")
    reason: str = Field(..., description="Reservation value / option policy rationale")


class FPLGameweekPlan(BaseModel):
    season: str = Field("2026-27", description="FPL Season")
    gameweek: int = Field(..., ge=1, le=38, description="Gameweek number")
    deadline: str = Field(..., description="Official deadline ISO timestamp")
    model_version: str = Field("ennovera-fpl-v1.0", description="Public model identifier")
    data_cutoff: str = Field("Official FPL Gameweek Deadline", description="Point-in-time information cutoff")
    generated_at: str = Field(..., description="Plan generation ISO timestamp")
    expected_total_points: float = Field(..., description="Projected team score including captain bonus")
    formation: str = Field(..., description="Selected starting formation (e.g. 3-5-2, 4-3-3)")
    starting_xi: List[FPLPlayer] = Field(..., description="11 Starting players")
    bench: List[FPLPlayer] = Field(..., description="4 Bench players (1 GK, 3 Outfield)")
    captain: Dict[str, Any] = Field(..., description="Captain asset details")
    vice_captain: Dict[str, Any] = Field(..., description="Vice-captain asset details")
    recommended_transfers: List[FPLTransferRecommendation] = Field(default_factory=list, description="Recommended transfers")
    chip_recommendation: FPLChipRecommendation = Field(..., description="Active chip guidance")
    available_chips: List[str] = Field(default_factory=list, description="List of currently available legal chips")
    bank: float = Field(0.5, description="Available bank balance (£m)")
    free_transfers: int = Field(1, description="Available free transfers count")
    warnings: List[str] = Field(default_factory=list, description="Health or freshness alerts")


class FPLSquadResponse(BaseModel):
    season: str = "2026-27"
    gameweek: int
    formation: str
    total_cost: float
    bank: float
    free_transfers: int
    squad: List[FPLPlayer]


class FPLCaptainResponse(BaseModel):
    season: str = "2026-27"
    gameweek: int
    captain: Dict[str, Any]
    vice_captain: Dict[str, Any]
    alternatives: List[Dict[str, Any]]
    selection_rationale: str


class FPLChipStatusItem(BaseModel):
    chip_id: str
    name: str
    available: bool
    used: bool
    status: Literal["AVAILABLE", "USED", "LOCKED", "EXPIRED"]
    target_gw: Optional[int] = None
    expected_incremental_value: float = 0.0
    reservation_value: float = 0.0
    reason: str


class FPLRulesResponse(BaseModel):
    season: str = "2026-27"
    budget_starting: float = 100.0
    squad_size: int = 15
    position_limits: Dict[str, int]
    max_players_per_club: int = 3
    starting_xi_size: int = 11
    formation_min_rules: Dict[str, int]
    captain_multiplier: int = 2
    triple_captain_multiplier: int = 3
    free_transfers_per_gw: int = 1
    max_banked_transfers: int = 5
    transfer_hit_cost: int = 4
    chips_available: List[str]


class FPLWeeklyPerformance(BaseModel):
    gameweek: int
    score: int
    raw_xi_pts: int
    captain_name: str
    captain_pts: int
    transfers_made: int
    hit_cost: int
    chip_used: str
    bench_pts: int


class FPLPerformanceResponse(BaseModel):
    season: str = "2026-27"
    completed_gameweeks: int
    total_points: int
    average_points: float
    captain_points: int
    transfer_costs: int
    chip_points: int
    bench_points_missed: int
    history: List[FPLWeeklyPerformance]
