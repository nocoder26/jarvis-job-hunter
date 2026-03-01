"""
Run AI analysis on new jobs to determine fit scores.
"""

import os
import json
import google.generativeai as genai
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def analyze_new_jobs() -> int:
    """
    Analyze jobs that haven't been analyzed yet.
    Returns the number of jobs analyzed.
    """
    if not GEMINI_API_KEY:
        return 0

    supabase = get_supabase()
    analyzed_count = 0

    # Get candidate profile first
    profile_result = supabase.table("candidate_profiles").select("*").limit(1).execute()

    if not profile_result.data:
        print("No candidate profile found - skipping analysis")
        return 0

    profile = profile_result.data[0]

    # Get jobs without analysis (status = 'new')
    jobs_result = supabase.table("jobs").select(
        "*, companies(*)"
    ).eq("status", "new").limit(5).execute()

    jobs = jobs_result.data or []

    for job in jobs:
        try:
            analysis = analyze_single_job(job, profile)

            if analysis:
                # Store analysis
                analysis_data = {
                    "job_id": job["id"],
                    "fit_score": analysis.get("fit_score", 0),
                    "spanish_required": analysis.get("spanish_required", False),
                    "visa_status": analysis.get("visa_status", "unclear"),
                    "fit_summary": analysis.get("fit_summary", ""),
                    "skills_matched": analysis.get("skills_matched", []),
                    "skills_missing": analysis.get("skills_missing", []),
                }

                supabase.table("job_analysis").upsert(
                    analysis_data, on_conflict="job_id"
                ).execute()

                # Update job status
                supabase.table("jobs").update({
                    "status": "analyzed"
                }).eq("id", job["id"]).execute()

                analyzed_count += 1
                print(f"Analyzed job: {job.get('title')} - Score: {analysis.get('fit_score')}")

        except Exception as e:
            print(f"Error analyzing job {job.get('title')}: {e}")

    return analyzed_count


def analyze_single_job(job: dict, profile: dict) -> dict:
    """
    Analyze a single job against the candidate profile using Gemini.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    profile_json = profile.get("profile_json", {})
    company = job.get("companies", {})

    prompt = f"""
    Analyze how well this candidate matches this job posting.

    JOB POSTING:
    Title: {job.get('title', 'Unknown')}
    Company: {company.get('name', 'Unknown') if company else 'Unknown'}
    Description: {job.get('description', 'No description')[:2000]}
    Location: {job.get('location', 'Unknown')}

    CANDIDATE PROFILE:
    {json.dumps(profile_json, indent=2)}

    Return a JSON object with this exact structure:
    {{
        "fit_score": <integer 0-100>,
        "spanish_required": <boolean - true if job requires Spanish language>,
        "visa_status": "<one of: 'hqp_eligible', 'startup_law_eligible', 'standard_visa', 'unclear'>",
        "fit_summary": "<2-3 sentence summary of fit>",
        "skills_matched": ["skill1", "skill2", ...],
        "skills_missing": ["skill1", "skill2", ...]
    }}

    Scoring guidelines:
    - 90-100: Excellent fit, meets all requirements
    - 70-89: Good fit, meets most requirements
    - 50-69: Moderate fit, meets some requirements
    - Below 50: Poor fit, missing critical requirements

    For visa_status, consider:
    - hqp_eligible: Company seems tech/startup focused, likely qualifies for HQP visa
    - startup_law_eligible: Company is a registered startup under Spanish Startup Law
    - standard_visa: Regular work visa process
    - unclear: Cannot determine from job posting

    Only return valid JSON, no markdown or explanation.
    """

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Clean up response if wrapped in markdown
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)
