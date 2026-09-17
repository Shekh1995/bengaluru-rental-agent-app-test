import os
from typing import Any, Dict, List

import httpx

from app.database import repository
from app.models import PropertyListing


class ListingSyncError(RuntimeError):
    pass


def _source_records(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("listings"), list):
        return payload["listings"]
    raise ListingSyncError("Source response must be a list or an object with a listings array")


def sync_live_listings() -> int:
    if os.getenv("LISTINGS_PROVIDER", "generic").lower() == "square_yards":
        from app.services.square_yards_service import sync_square_yards_listings
        return sync_square_yards_listings()
    source_url = os.getenv("LISTINGS_API_URL")
    if not source_url:
        raise ListingSyncError("LISTINGS_API_URL is not configured")

    headers = {}
    token = os.getenv("LISTINGS_API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = httpx.get(source_url, headers=headers, timeout=20.0)
        response.raise_for_status()
        listings = [PropertyListing.model_validate(item) for item in _source_records(response.json())]
    except (httpx.HTTPError, ValueError) as error:
        raise ListingSyncError(f"Could not import listings: {error}") from error

    if not listings:
        raise ListingSyncError("Source returned no listings; existing active data was kept")
    repository.replace_active(listings)
    return len(listings)
