from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import jobs, profile, actions
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Jarvis Job Hunter API",
    description="Automated job sourcing and application engine",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(actions.router, prefix="/api/actions", tags=["Actions"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "jarvis-api"}


@app.get("/")
async def root():
    return {
        "message": "Jarvis Job Hunter API",
        "docs": "/docs",
        "health": "/health",
    }
