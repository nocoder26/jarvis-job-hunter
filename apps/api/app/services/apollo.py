import httpx
from typing import List, Dict, Any

from app.config import get_settings


async def find_company_contacts(domain: str) -> List[Dict[str, Any]]:
    """
    Find contacts at a company using Apollo.io API.
    Targets decision makers (engineering managers, CTOs, hiring managers).
    """
    settings = get_settings()

    if not settings.apollo_api_key:
        return []

    async with httpx.AsyncClient() as client:
        # Search for people at the company
        response = await client.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
            json={
                "api_key": settings.apollo_api_key,
                "q_organization_domains": domain,
                "page": 1,
                "per_page": 10,
                "person_titles": [
                    "CTO",
                    "VP Engineering",
                    "Engineering Manager",
                    "Head of Engineering",
                    "Technical Lead",
                    "Hiring Manager",
                    "Talent Acquisition",
                    "Recruiter",
                    "HR Manager",
                ],
            },
        )

        if response.status_code != 200:
            return []

        data = response.json()
        people = data.get("people", [])

        contacts = []
        for person in people:
            if person.get("email"):
                contacts.append({
                    "email": person["email"],
                    "name": person.get("name"),
                    "title": person.get("title"),
                    "linkedin_url": person.get("linkedin_url"),
                })

        return contacts
