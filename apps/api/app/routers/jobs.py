from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from uuid import UUID

from app.services.supabase import get_supabase_client
from app.models.schemas import JobResponse, JobAnalysisResponse, JobListResponse

router = APIRouter()


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum fit score"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all jobs with optional filters."""
    supabase = get_supabase_client()

    query = supabase.table("jobs").select(
        "*, companies(*), job_analysis(*)"
    )

    if status:
        query = query.eq("status", status)

    query = query.order("discovered_at", desc=True).range(offset, offset + limit - 1)

    result = query.execute()

    # Filter by score if specified (done in Python since it's a joined table)
    jobs = result.data
    if min_score is not None:
        jobs = [
            j for j in jobs
            if j.get("job_analysis") and j["job_analysis"].get("fit_score", 0) >= min_score
        ]

    return {"jobs": jobs, "total": len(jobs)}


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID):
    """Get a specific job by ID."""
    supabase = get_supabase_client()

    result = supabase.table("jobs").select(
        "*, companies(*), job_analysis(*)"
    ).eq("id", str(job_id)).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    return result.data


@router.post("/{job_id}/analyze", response_model=JobAnalysisResponse)
async def analyze_job(job_id: UUID):
    """Trigger AI analysis for a specific job."""
    from app.services.gemini import analyze_job_fit

    supabase = get_supabase_client()

    # Get job details
    job_result = supabase.table("jobs").select("*").eq("id", str(job_id)).single().execute()

    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_result.data

    # Get candidate profile
    profile_result = supabase.table("candidate_profiles").select("*").limit(1).execute()

    if not profile_result.data:
        raise HTTPException(status_code=400, detail="No candidate profile found. Please upload resume first.")

    profile = profile_result.data[0]

    # Run analysis
    analysis = await analyze_job_fit(job, profile)

    # Store analysis
    analysis_data = {
        "job_id": str(job_id),
        **analysis
    }

    supabase.table("job_analysis").upsert(analysis_data, on_conflict="job_id").execute()

    # Update job status
    supabase.table("jobs").update({"status": "analyzed"}).eq("id", str(job_id)).execute()

    return analysis


@router.patch("/{job_id}/status")
async def update_job_status(job_id: UUID, status: str):
    """Update job status."""
    valid_statuses = ["new", "analyzed", "applied", "interviewing", "rejected", "archived"]

    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    supabase = get_supabase_client()

    result = supabase.table("jobs").update({"status": status}).eq("id", str(job_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"message": "Status updated", "status": status}
