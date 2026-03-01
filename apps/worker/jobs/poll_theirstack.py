"""
Poll TheirStack API for tech jobs in Spain.
"""

import os
import httpx
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def get_supabase():
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))


def get_theirstack_key():
    return os.getenv("THEIRSTACK_API_KEY")


def poll_theirstack() -> int:
    """
    Poll TheirStack for new tech jobs in Spain.
    Returns the number of new jobs found.
    """
    api_key = get_theirstack_key()
    if not api_key:
        return 0

    supabase = get_supabase()
    new_jobs_count = 0

    # TheirStack API endpoint for job search
    # Searching for tech roles in Spain
    search_params = {
        "job_country_code_or": ["ES"],  # Spain
        "job_title_or": [
            "Software Engineer",
            "Backend Engineer",
            "Frontend Engineer",
            "Full Stack Engineer",
            "Data Engineer",
            "Machine Learning Engineer",
            "DevOps Engineer",
            "Site Reliability Engineer",
            "Engineering Manager",
            "Tech Lead",
            "CTO",
            "VP Engineering",
        ],
        "posted_at_max_age_days": 7,  # Last 7 days
        "page": 1,
        "limit": 50,
    }

    try:
        with httpx.Client() as client:
            response = client.post(
                "https://api.theirstack.com/v1/jobs/search",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=search_params,
                timeout=30,
            )

            if response.status_code != 200:
                log_poll("theirstack", "jobs/search", response.status_code, 0)
                return 0

            data = response.json()
            jobs = data.get("data", [])

            for job in jobs:
                external_id = f"theirstack_{job.get('id')}"

                # Check if job already exists
                existing = supabase.table("jobs").select("id").eq(
                    "external_id", external_id
                ).execute()

                if existing.data:
                    continue

                # Get or create company (company is a string in TheirStack API)
                company_id = None
                company_name = job.get("company")
                if company_name:
                    company_id = upsert_company_by_name(supabase, company_name)

                # Insert job (TheirStack uses job_title, date_posted, final_url)
                job_data = {
                    "external_id": external_id,
                    "source": "theirstack",
                    "company_id": company_id,
                    "title": job.get("job_title") or job.get("title"),
                    "description": job.get("description"),
                    "location": job.get("location"),
                    "application_url": job.get("final_url") or job.get("url"),
                    "posted_at": job.get("date_posted"),
                    "status": "new",
                }

                supabase.table("jobs").insert(job_data).execute()
                new_jobs_count += 1

            log_poll("theirstack", "jobs/search", 200, new_jobs_count)

    except Exception as e:
        print(f"TheirStack polling error: {e}")
        log_poll("theirstack", "jobs/search", 500, 0)

    return new_jobs_count


def upsert_company_by_name(supabase, company_name: str) -> str:
    """Create or get existing company by name, return company ID."""
    existing = supabase.table("companies").select("id").eq(
        "name", company_name
    ).execute()

    if existing.data:
        return existing.data[0]["id"]

    # Insert new company
    new_company = {
        "name": company_name,
    }

    result = supabase.table("companies").insert(new_company).execute()
    return result.data[0]["id"] if result.data else None


def log_poll(source: str, endpoint: str, status_code: int, jobs_found: int):
    """Log the polling attempt."""
    try:
        supabase = get_supabase()
        supabase.table("polling_logs").insert({
            "source": source,
            "endpoint": endpoint,
            "status_code": status_code,
            "jobs_found": jobs_found,
        }).execute()
    except Exception as e:
        print(f"Failed to log poll: {e}")
