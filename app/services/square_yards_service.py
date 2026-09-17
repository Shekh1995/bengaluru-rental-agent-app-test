import json
import os
from typing import Any, Dict, List, Optional

import httpx

from app.database import repository
from app.models import PropertyListing
from app.services.listing_sync import ListingSyncError


MCP_URL = "https://sy-mcp.squareyards.com/mcp/external"


def _json_from_mcp_response(response: httpx.Response) -> Dict[str, Any]:
    if response.headers.get("content-type", "").startswith("text/event-stream"):
        data_lines = [line[5:].strip() for line in response.text.splitlines() if line.startswith("data:")]
        if not data_lines:
            raise ListingSyncError("Square Yards MCP returned an empty event stream")
        return json.loads(data_lines[-1])
    return response.json()


def _rpc_call(client: httpx.Client, method: str, params: Dict[str, Any], request_id: int, session_id: Optional[str] = None) -> tuple[Dict[str, Any], Optional[str]]:
    headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    response = client.post(MCP_URL, headers=headers, json={"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
    response.raise_for_status()
    return _json_from_mcp_response(response), response.headers.get("Mcp-Session-Id") or session_id


def _call_search_properties(client: httpx.Client, arguments: Dict[str, Any]) -> Dict[str, Any]:
    initialized, session_id = _rpc_call(client, "initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "bengaluru-rental-agent", "version": "1.0.0"}}, 1)
    if "error" in initialized:
        raise ListingSyncError(f"Square Yards MCP initialization failed: {initialized['error']}")
    headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    client.post(MCP_URL, headers=headers, json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}).raise_for_status()
    result, _ = _rpc_call(client, "tools/call", {"name": "search_properties", "arguments": arguments}, 2, session_id)
    if "error" in result:
        raise ListingSyncError(f"Square Yards search failed: {result['error']}")
    tool_result = result.get("result", {})
    if tool_result.get("isError"):
        raise ListingSyncError("Square Yards returned a tool error")
    if isinstance(tool_result.get("structuredContent"), dict):
        return tool_result["structuredContent"]
    for content in tool_result.get("content", []):
        if content.get("type") == "text":
            return json.loads(content["text"])
    raise ListingSyncError("Square Yards MCP returned no structured search result")


def _map_listing(item: Dict[str, Any]) -> PropertyListing:
    rent = item.get("price")
    if not item.get("id") or not item.get("bhk") or not rent:
        raise ValueError("listing is missing id, bhk, or price")
    area = item.get("locality") or item.get("city") or "Bengaluru"
    furnishing = (item.get("furnishing") or "Not specified").replace("-", " ").title()
    return PropertyListing(
        id=f"square-yards-{item['id']}",
        title=item.get("title") or f"{item['bhk']} BHK home in {area}",
        area=area,
        bhk=int(str(item["bhk"]).split()[0]),
        property_type=item.get("propertyTypeName") or "Apartment",
        rent_monthly=round(float(rent)),
        deposit=round(float(rent) * 4),
        maintenance=0,
        furnishing=furnishing,
        built_up_sqft=round(float(item.get("areaSqft") or 0)),
        floor=str(item.get("floor") or "Not specified"),
        parking=str(item.get("parking") or "Not specified"),
        availability="Check source listing",
        nearest_metro="Not provided by source",
        metro_distance_km=0,
        work_commutes=[],
        area_character=item.get("summary") or "See the Square Yards listing for more details.",
        nearby_essentials=[],
        verification_flags=["Square Yards verified"] if item.get("isVerified") else [],
        google_maps_url=item.get("url") or item.get("sourceUrl") or "https://www.squareyards.com",
        listing_source="Square Yards",
        locality_metrics={"water_score": 3.0, "noise_level": "Unknown", "green_cover": "Unknown", "metro_proximity_km": 0},
    )


def sync_square_yards_listings() -> int:
    arguments: Dict[str, Any] = {
        "listingType": "Rent",
        "location": os.getenv("SQUARE_YARDS_LOCATION", "Bengaluru"),
        "size": min(int(os.getenv("SQUARE_YARDS_SIZE", "50")), 50),
        "page": int(os.getenv("SQUARE_YARDS_PAGE", "1")),
    }
    for env_name, argument_name in (("SQUARE_YARDS_BEDROOMS", "bedrooms"), ("SQUARE_YARDS_MAX_PRICE", "maxPrice"), ("SQUARE_YARDS_MIN_PRICE", "minPrice")):
        value = os.getenv(env_name)
        if value:
            arguments[argument_name] = value if argument_name == "bedrooms" else int(value)
    try:
        listings = []
        max_pages = max(1, int(os.getenv("SQUARE_YARDS_MAX_PAGES", "100")))
        with httpx.Client(timeout=30.0) as client:
            for page in range(arguments["page"], arguments["page"] + max_pages):
                arguments["page"] = page
                payload = _call_search_properties(client, arguments)
                listings.extend(_map_listing(item) for item in payload.get("listings", []))
                total_pages = int(payload.get("totalPages") or page)
                if page >= total_pages or not payload.get("listings"):
                    break
    except (httpx.HTTPError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ListingSyncError(f"Could not import Square Yards listings: {error}") from error
    if not listings:
        raise ListingSyncError("Square Yards returned no rental listings; existing active data was kept")
    repository.replace_active(listings)
    return len(listings)
