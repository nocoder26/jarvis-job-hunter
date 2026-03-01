import httpx
from datetime import datetime
from typing import Dict, Any

from app.config import get_settings


async def verify_email(email: str) -> Dict[str, Any]:
    """
    Verify an email address using ZeroBounce API.
    Returns verification status and timestamp.
    """
    settings = get_settings()

    if not settings.zerobounce_api_key:
        return {
            "status": "unverified",
            "verified_at": None,
            "reason": "API key not configured"
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.zerobounce.net/v2/validate",
            params={
                "api_key": settings.zerobounce_api_key,
                "email": email,
            },
        )

        if response.status_code != 200:
            return {
                "status": "error",
                "verified_at": None,
                "reason": f"API error: {response.status_code}"
            }

        data = response.json()

        # Map ZeroBounce status to our status
        zb_status = data.get("status", "unknown")

        if zb_status == "valid":
            status = "valid"
        elif zb_status in ["invalid", "do_not_mail"]:
            status = "invalid"
        elif zb_status == "catch-all":
            status = "catch-all"
        elif zb_status == "spamtrap":
            status = "invalid"
        else:
            status = "unknown"

        return {
            "status": status,
            "verified_at": datetime.utcnow().isoformat() if status == "valid" else None,
            "reason": data.get("sub_status"),
            "did_you_mean": data.get("did_you_mean"),
        }
