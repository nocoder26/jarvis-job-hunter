"""
Poll SerpApi (Google Jobs) for tech jobs in Spain.
"""

import os
import httpx
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def poll_serpapi() -> int:
    """
    Poll SerpApi Google Jobs for new tech jobs in Spain.
    Returns the number of new jobs found.
    """
    if not SERPAPI_API_KEY:
        return 0

    supabase = get_supabase()
    new_jobs_count = 0

    # Job searches to perform
    searches = [
        "Software Engineer Spain",
        "Backend Developer Spain",
        "Full Stack Developer Spain",
        "Machine Learning Engineer Spain",
        "Data Engineer Spain",
        "DevOps Engineer Spain",
    ]

    for search_query in searches:
        try:
            jobs_found = search_google_jobs(supabase, search_query)
            new_jobs_count += jobs_found
        except Exception as e:
            print(f"SerpApi search error for '{search_query}': {e}")

    return new_jobs_count


def search_google_jobs(supabase, query: str) -> int:
    """Search Google Jobs via SerpApi and store results."""
    new_jobs = 0

    with httpx.Client() as client:
        response = client.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_jobs",
                "q": query,
                "location": "Spain",
                "hl": "en",
                "api_key": SERPAPI_API_KEY,
            },
            timeout=30,
        )

        if response.status_code != 200:
            log_poll("serpapi", query, response.status_code, 0)
            return 0

        data = response.json()
        jobs = data.get("jobs_results", [])

        for job in jobs:
            # Create unique external ID from job title + company
            job_id = f"{job.get('title', '')}_{job.get('company_name', '')}".replace(" ", "_")[:100]
            external_id = f"serpapi_{hash(job_id)}"

            # Check if job already exists
            existing = supabase.table("jobs").select("id").eq(
                "external_id", external_id
            ).execute()

            if existing.data:
                continue

            # Get or create company
            company_id = None
            company_name = job.get("company_name")
            if company_name:
                company_id = upsert_company(supabase, company_name)

            # Get application URL from extensions
            application_url = None
            for extension in job.get("extensions", []):
                if extension.get("apply_options"):
                    for option in extension["apply_options"]:
                        if option.get("link"):
                            application_url = option["link"]
                            break

            # If no specific URL, use the share link
            if not application_url:
                application_url = job.get("share_link")

            # Insert job
            job_data = {
                "external_id": external_id,
                "source": "serpapi_google_jobs",
                "company_id": company_id,
                "title": job.get("title"),
                "description": job.get("description"),
                "location": job.get("location"),
                "application_url": application_url,
                "status": "new",
            }

            supabase.table("jobs").insert(job_data).execute()
            new_jobs += 1

        log_poll("serpapi", query, 200, new_jobs)

    return new_jobs


def upsert_company(supabase, company_name: str) -> str:
    """Create or get existing company by name, return company ID."""
    # Simple lookup by name
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
