"""Ennovera Premier League & Fantasy Premier League FastAPI Serving Layer.
Authoritative production entry point for match intelligence and autonomous FPL management.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pl as pl_router
from app.routers import fpl as fpl_router
from app.services.pl_service import pl_service
from app.services.fpl_service import fpl_service
from app.schemas.pl import PLHealthResponse

app = FastAPI(
    title="Ennovera Premier League & FPL API",
    description="Authoritative match intelligence (Production V2 + Shadow V5.1) and autonomous FPL decision management (FPL-03)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aifootballp.com",
        "https://innovera-wc2026-frontend.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(pl_router.router)
app.include_router(fpl_router.router)


@app.get("/health", response_model=PLHealthResponse, tags=["Health"])
def health_check():
    """Returns engine health status and verifies that inference models are loaded."""
    return {
        "status": "ok",
        "service": "ennovera-pl",
        "version": "1.0.0",
        "production_model_loaded": pl_service.is_loaded,
        "shadow_model_loaded": bool(pl_service._v5_art is not None),
        "season": "2026-27"
    }


@app.get("/", tags=["Health"])
def root_check():
    return {
        "service": "Ennovera Premier League & FPL Intelligence Service",
        "status": "operational",
        "version": "1.0.0",
        "season": "2026-27",
        "health": "/health",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=False)
