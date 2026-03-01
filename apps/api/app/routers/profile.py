from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional

from app.services.supabase import get_supabase_client
from app.models.schemas import CandidateProfile, ProfileResponse

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def get_profile():
    """Get the current candidate profile."""
    supabase = get_supabase_client()

    result = supabase.table("candidate_profiles").select("*").limit(1).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="No profile found. Please upload a resume.")

    return result.data[0]


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse a resume to create/update candidate profile."""
    import pdfplumber
    import io
    from app.services.gemini import extract_profile_from_resume

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read PDF content
    content = await file.read()

    # Extract text from PDF
    text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Use AI to structure the resume
    profile_json = await extract_profile_from_resume(text)

    # Store in Supabase
    supabase = get_supabase_client()

    # Upload PDF to storage
    storage_path = f"resumes/{file.filename}"
    supabase.storage.from_("resumes").upload(storage_path, content, {"content-type": "application/pdf"})

    resume_url = supabase.storage.from_("resumes").get_public_url(storage_path)

    # Upsert profile (replace existing)
    profile_data = {
        "profile_json": profile_json,
        "resume_url": resume_url,
    }

    # Delete existing profile and insert new one
    supabase.table("candidate_profiles").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    result = supabase.table("candidate_profiles").insert(profile_data).execute()

    return {
        "message": "Resume uploaded and parsed successfully",
        "profile": result.data[0] if result.data else None
    }


@router.put("/")
async def update_profile(profile: CandidateProfile):
    """Manually update candidate profile."""
    supabase = get_supabase_client()

    # Get existing profile
    existing = supabase.table("candidate_profiles").select("id").limit(1).execute()

    if not existing.data:
        # Create new profile
        result = supabase.table("candidate_profiles").insert({
            "profile_json": profile.model_dump(),
        }).execute()
    else:
        # Update existing
        result = supabase.table("candidate_profiles").update({
            "profile_json": profile.model_dump(),
        }).eq("id", existing.data[0]["id"]).execute()

    return {"message": "Profile updated", "profile": result.data[0] if result.data else None}


from pydantic import BaseModel

class LinkedInRequest(BaseModel):
    linkedin_url: str

@router.post("/enrich-linkedin")
async def enrich_from_linkedin(request: LinkedInRequest):
    """Enrich profile with LinkedIn data using Proxycurl."""
    from app.services.proxycurl import get_linkedin_profile
    linkedin_url = request.linkedin_url

    supabase = get_supabase_client()

    # Get existing profile
    existing = supabase.table("candidate_profiles").select("*").limit(1).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="No profile found. Please upload a resume first.")

    # Fetch LinkedIn data
    linkedin_data = await get_linkedin_profile(linkedin_url)

    # Merge with existing profile
    current_profile = existing.data[0]["profile_json"]
    enriched_profile = {**current_profile, "linkedin_data": linkedin_data}

    # Update profile
    result = supabase.table("candidate_profiles").update({
        "profile_json": enriched_profile,
        "linkedin_url": linkedin_url,
    }).eq("id", existing.data[0]["id"]).execute()

    return {"message": "Profile enriched with LinkedIn data", "profile": result.data[0] if result.data else None}
