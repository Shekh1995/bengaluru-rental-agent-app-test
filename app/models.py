from typing import List, Optional
from pydantic import BaseModel, Field


class CommuteInfo(BaseModel):
    destination: str
    travel_time_mins: int
    mode: str
    estimate_type: str = "Typical peak estimate"


class LocalityMetrics(BaseModel):
    water_score: float = Field(..., ge=1, le=5, description="1 to 5 scale based on Cauvery/Borewell reliability")
    noise_level: str = "Low"  # Low, Moderate, High
    green_cover: str = "High" # High, Moderate, Low
    metro_proximity_km: float


class PropertyListing(BaseModel):
    id: str
    title: str
    area: str
    bhk: int
    property_type: str  # Builder Floor, Apartment, Independent House
    rent_monthly: int
    deposit: int
    maintenance: int
    furnishing: str     # Unfurnished, Semi-Furnished, Fully Furnished
    built_up_sqft: int
    floor: str
    parking: str
    availability: str
    nearest_metro: str
    metro_distance_km: float
    work_commutes: List[CommuteInfo]
    area_character: str
    nearby_essentials: List[str]
    verification_flags: List[str] = Field(default_factory=list)
    google_maps_url: str
    listing_source: str
    locality_metrics: LocalityMetrics


class CostBreakdownRequest(BaseModel):
    rent_monthly: int = Field(..., ge=0)
    deposit: int = Field(..., ge=0)
    maintenance: int = Field(..., ge=0)
    brokerage: int = Field(0, ge=0)
    agreement_charges: int = Field(1500, ge=0)
    other_charges: int = Field(0, ge=0)


class CostBreakdownResponse(BaseModel):
    total_monthly_burn: int
    total_initial_move_in_cost: int
    deposit_to_rent_ratio: float
    annual_cost_projection: int
    is_deposit_high: bool
    savings_vs_market_avg: int


class SearchFilter(BaseModel):
    min_rent: Optional[int] = Field(0, ge=0)
    max_rent: Optional[int] = Field(100000, ge=0)
    bhk: Optional[int] = Field(None, ge=1)
    area: Optional[str] = None
    furnishing: Optional[str] = None
    work_location: Optional[str] = None
    max_commute_mins: Optional[int] = Field(None, ge=0)
