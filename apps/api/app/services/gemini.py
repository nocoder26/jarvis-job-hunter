import google.generativeai as genai
import json
from typing import Dict, Any, Optional

from app.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)


async def extract_profile_from_resume(resume_text: str) -> Dict[str, Any]:
    """Extract structured profile data from resume text using Gemini."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Extract structured information from this resume text and return it as JSON.

    Resume:
    {resume_text}

    Return a JSON object with the following structure:
    {{
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "phone number",
        "location": "City, Country",
        "summary": "Professional summary",
        "skills": ["skill1", "skill2", ...],
        "experience": [
            {{
                "title": "Job Title",
                "company": "Company Name",
                "location": "Location",
                "start_date": "YYYY-MM",
                "end_date": "YYYY-MM or Present",
                "description": "Role description",
                "achievements": ["achievement1", "achievement2"]
            }}
        ],
        "education": [
            {{
                "degree": "Degree Name",
                "institution": "Institution Name",
                "graduation_year": "YYYY",
                "field": "Field of Study"
            }}
        ],
        "languages": ["language1", "language2"],
        "certifications": ["cert1", "cert2"]
    }}

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


async def analyze_job_fit(job: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze how well a candidate fits a job using Gemini."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    profile_json = profile.get("profile_json", {})

    prompt = f"""
    Analyze how well this candidate matches this job posting.

    JOB POSTING:
    Title: {job.get('title', 'Unknown')}
    Description: {job.get('description', 'No description')}
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


async def generate_cold_email(
    job: Dict[str, Any],
    company: Optional[Dict[str, Any]],
    profile: Dict[str, Any],
    analysis: Optional[Dict[str, Any]],
    contact: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """Generate a personalized cold outreach email using Gemini."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    profile_json = profile.get("profile_json", {})
    contact_name = contact.get("name", "Hiring Manager") if contact else "Hiring Manager"
    company_name = company.get("name", "your company") if company else "your company"

    prompt = f"""
    Write a concise, personalized cold outreach email for this job opportunity.

    JOB DETAILS:
    Title: {job.get('title', 'Unknown')}
    Company: {company_name}
    Description snippet: {job.get('description', '')[:500]}

    CANDIDATE HIGHLIGHTS:
    Name: {profile_json.get('name', 'Candidate')}
    Key Skills: {', '.join(profile_json.get('skills', [])[:10])}
    Summary: {profile_json.get('summary', '')}

    FIT ANALYSIS:
    {json.dumps(analysis, indent=2) if analysis else 'Not analyzed yet'}

    RECIPIENT: {contact_name}

    Write an email that:
    1. Is under 150 words
    2. Opens with a specific hook about the company or role
    3. Highlights 2-3 relevant achievements
    4. Shows genuine interest without being generic
    5. Has a clear call to action
    6. Is professional but personable

    Return a JSON object:
    {{
        "subject": "Email subject line",
        "body": "Full email body"
    }}

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
