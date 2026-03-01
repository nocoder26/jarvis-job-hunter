import httpx
from typing import Dict, Any

from app.config import get_settings


async def get_linkedin_profile(linkedin_url: str) -> Dict[str, Any]:
    """
    Fetch LinkedIn profile data using Proxycurl API.
    Returns structured profile information.
    """
    settings = get_settings()

    if not settings.proxycurl_api_key:
        return {"error": "Proxycurl API key not configured"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://nubela.co/proxycurl/api/v2/linkedin",
            headers={
                "Authorization": f"Bearer {settings.proxycurl_api_key}",
            },
            params={
                "linkedin_profile_url": linkedin_url,
                "fallback_to_cache": "on-error",
                "use_cache": "if-present",
                "skills": "include",
                "inferred_salary": "include",
                "personal_email": "include",
                "personal_contact_number": "include",
            },
        )

        if response.status_code != 200:
            return {
                "error": f"API error: {response.status_code}",
                "message": response.text
            }

        data = response.json()

        # Extract relevant fields
        return {
            "full_name": data.get("full_name"),
            "headline": data.get("headline"),
            "summary": data.get("summary"),
            "country": data.get("country_full_name"),
            "city": data.get("city"),
            "skills": data.get("skills", []),
            "experiences": [
                {
                    "title": exp.get("title"),
                    "company": exp.get("company"),
                    "starts_at": exp.get("starts_at"),
                    "ends_at": exp.get("ends_at"),
                    "description": exp.get("description"),
                }
                for exp in data.get("experiences", [])
            ],
            "education": [
                {
                    "school": edu.get("school"),
                    "degree_name": edu.get("degree_name"),
                    "field_of_study": edu.get("field_of_study"),
                    "starts_at": edu.get("starts_at"),
                    "ends_at": edu.get("ends_at"),
                }
                for edu in data.get("education", [])
            ],
            "languages": data.get("languages", []),
            "certifications": data.get("certifications", []),
        }
