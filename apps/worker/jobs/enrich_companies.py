"""
Enrich companies with additional data:
- Check for ENISA certification (Spanish Startup Law)
- Extract funding information
- Determine visa eligibility
"""

import os
import httpx
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def enrich_companies() -> int:
    """
    Enrich companies that haven't been enriched yet.
    Returns the number of companies enriched.
    """
    supabase = get_supabase()
    enriched_count = 0

    # Get companies without enrichment
    result = supabase.table("companies").select("*").is_(
        "enriched_at", "null"
    ).limit(10).execute()

    companies = result.data or []

    for company in companies:
        try:
            enriched = enrich_single_company(company)
            if enriched:
                supabase.table("companies").update({
                    "is_enisa_certified": enriched.get("is_enisa_certified", False),
                    "is_startup_law": enriched.get("is_startup_law", False),
                    "funding_stage": enriched.get("funding_stage"),
                    "enriched_at": datetime.utcnow().isoformat(),
                }).eq("id", company["id"]).execute()

                enriched_count += 1
        except Exception as e:
            print(f"Error enriching company {company.get('name')}: {e}")

    return enriched_count


def enrich_single_company(company: dict) -> dict:
    """
    Enrich a single company with additional data.
    """
    enriched = {
        "is_enisa_certified": False,
        "is_startup_law": False,
        "funding_stage": company.get("funding_stage"),
    }

    domain = company.get("domain")
    website_url = company.get("website_url")

    if not domain and not website_url:
        return enriched

    # Check ENISA certification (Spanish Startup Law registry)
    # Note: In production, this would scrape the actual ENISA registry
    # For now, we'll check for common indicators
    enriched["is_startup_law"] = check_startup_law_indicators(company)

    # Check if company website mentions ENISA/Startup Law certification
    if website_url:
        try:
            enriched["is_enisa_certified"] = check_website_for_enisa(website_url)
        except Exception:
            pass

    return enriched


def check_startup_law_indicators(company: dict) -> bool:
    """
    Check if company shows indicators of Spanish Startup Law eligibility.
    This is a heuristic check - production would use actual registry.
    """
    # Keywords that indicate startup status
    startup_keywords = [
        "startup",
        "innovative",
        "technology",
        "tech",
        "saas",
        "fintech",
        "healthtech",
        "edtech",
        "ai",
        "machine learning",
        "blockchain",
    ]

    company_name = (company.get("name") or "").lower()
    domain = (company.get("domain") or "").lower()

    # Check if company name or domain contains startup indicators
    for keyword in startup_keywords:
        if keyword in company_name or keyword in domain:
            return True

    # Check funding stage - seed/series A/B companies are likely eligible
    funding = (company.get("funding_stage") or "").lower()
    if funding in ["seed", "series a", "series b", "pre-seed"]:
        return True

    return False


def check_website_for_enisa(website_url: str) -> bool:
    """
    Check company website for ENISA/Startup Law certification mentions.
    """
    try:
        with httpx.Client() as client:
            response = client.get(
                website_url,
                timeout=10,
                follow_redirects=True,
            )

            if response.status_code != 200:
                return False

            content = response.text.lower()

            # Check for ENISA or Startup Law mentions
            enisa_indicators = [
                "enisa",
                "empresa emergente",
                "startup law",
                "ley de startups",
                "certificada como startup",
            ]

            for indicator in enisa_indicators:
                if indicator in content:
                    return True

            return False

    except Exception:
        return False


def get_company_domain(website_url: str) -> str:
    """Extract domain from website URL."""
    from urllib.parse import urlparse

    try:
        parsed = urlparse(website_url)
        domain = parsed.netloc or parsed.path
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return None
