"""
Scene Analyzer Backend - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Scene Analyzer API",
    description="API for screenplay scene analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://localhost:3000"],  # Astro dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "not_implemented",  # TODO: Add DB check
            "redis": "not_implemented",  # TODO: Add Redis check
        },
    }


@app.get("/")
async def root():
    """Root endpoint - redirects to docs."""
    return {
        "message": "Scene Analyzer API",
        "docs": "/api/docs",
        "version": "1.0.0",
    }


# TODO: Import und registrieren der API-Router
# from app.api import scripts
# app.include_router(scripts.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
