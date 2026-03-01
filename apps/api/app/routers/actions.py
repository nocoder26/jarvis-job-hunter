from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import Optional

from app.services.supabase import get_supabase_client
from app.models.schemas import DraftEmailRequest, DraftEmailResponse

router = APIRouter()


@router.post("/jobs/{job_id}/apply")
async def auto_apply(job_id: UUID):
    """
    Trigger auto-apply for a job.
    This will use Playwright to fill out the application form.
    """
    supabase = get_supabase_client()

    # Get job details
    job_result = supabase.table("jobs").select("*, companies(*)").eq("id", str(job_id)).single().execute()

    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_result.data

    if not job.get("application_url"):
        raise HTTPException(status_code=400, detail="No application URL available for this job")

    # Get candidate profile
    profile_result = supabase.table("candidate_profiles").select("*").limit(1).execute()

    if not profile_result.data:
        raise HTTPException(status_code=400, detail="No candidate profile found")

    # TODO: Implement Playwright auto-apply logic
    # For now, we'll just record the application attempt

    application_data = {
        "job_id": str(job_id),
        "method": "auto",
        "status": "pending",
        "notes": f"Auto-apply queued for {job.get('application_url')}",
    }

    result = supabase.table("applications").insert(application_data).execute()

    # Update job status
    supabase.table("jobs").update({"status": "applied"}).eq("id", str(job_id)).execute()

    return {
        "message": "Application queued",
        "application_id": result.data[0]["id"] if result.data else None,
        "status": "pending"
    }


@router.post("/jobs/{job_id}/draft-email", response_model=DraftEmailResponse)
async def draft_email(job_id: UUID, request: Optional[DraftEmailRequest] = None):
    """
    Generate a cold outreach email draft for a job.
    Can optionally specify a contact to address.
    """
    from app.services.gemini import generate_cold_email

    supabase = get_supabase_client()

    # Get job and company details
    job_result = supabase.table("jobs").select(
        "*, companies(*), job_analysis(*)"
    ).eq("id", str(job_id)).single().execute()

    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_result.data
    company = job.get("companies")
    analysis = job.get("job_analysis")

    # Get candidate profile
    profile_result = supabase.table("candidate_profiles").select("*").limit(1).execute()

    if not profile_result.data:
        raise HTTPException(status_code=400, detail="No candidate profile found")

    profile = profile_result.data[0]

    # Get contact if specified
    contact = None
    if request and request.contact_id:
        contact_result = supabase.table("contacts").select("*").eq("id", str(request.contact_id)).single().execute()
        contact = contact_result.data
    elif company:
        # Try to find a contact for this company
        contact_result = supabase.table("contacts").select("*").eq("company_id", company["id"]).limit(1).execute()
        if contact_result.data:
            contact = contact_result.data[0]

    # Generate email using AI
    email = await generate_cold_email(job, company, profile, analysis, contact)

    # Store the draft
    outreach_data = {
        "job_id": str(job_id),
        "contact_id": contact["id"] if contact else None,
        "subject": email["subject"],
        "body": email["body"],
        "status": "drafted",
    }

    result = supabase.table("email_outreach").insert(outreach_data).execute()

    return {
        "id": result.data[0]["id"] if result.data else None,
        "subject": email["subject"],
        "body": email["body"],
        "contact": contact,
    }


@router.post("/contacts/discover")
async def discover_contacts(company_id: UUID):
    """
    Discover contacts at a company using Apollo.io.
    """
    from app.services.apollo import find_company_contacts
    from app.services.zerobounce import verify_email

    supabase = get_supabase_client()

    # Get company details
    company_result = supabase.table("companies").select("*").eq("id", str(company_id)).single().execute()

    if not company_result.data:
        raise HTTPException(status_code=404, detail="Company not found")

    company = company_result.data

    if not company.get("domain"):
        raise HTTPException(status_code=400, detail="Company domain not available")

    # Find contacts using Apollo
    contacts = await find_company_contacts(company["domain"])

    # Verify and store contacts
    stored_contacts = []
    for contact in contacts:
        # Verify email
        verification = await verify_email(contact["email"])

        contact_data = {
            "company_id": str(company_id),
            "email": contact["email"],
            "name": contact.get("name"),
            "title": contact.get("title"),
            "linkedin_url": contact.get("linkedin_url"),
            "verification_status": verification["status"],
            "verified_at": verification["verified_at"] if verification["status"] == "valid" else None,
            "source": "apollo",
        }

        result = supabase.table("contacts").upsert(
            contact_data,
            on_conflict="email"
        ).execute()

        if result.data:
            stored_contacts.append(result.data[0])

    return {
        "message": f"Discovered {len(stored_contacts)} contacts",
        "contacts": stored_contacts
    }


@router.get("/applications")
async def list_applications(
    status: Optional[str] = None,
    limit: int = 50,
):
    """List all applications."""
    supabase = get_supabase_client()

    query = supabase.table("applications").select("*, jobs(*, companies(*))")

    if status:
        query = query.eq("status", status)

    result = query.order("applied_at", desc=True).limit(limit).execute()

    return {"applications": result.data}
