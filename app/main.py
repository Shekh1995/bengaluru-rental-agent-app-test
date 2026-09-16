import os
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    PropertyListing,
    CostBreakdownRequest,
    CostBreakdownResponse,
    SearchFilter,
)
from app.services.property_service import PropertyService
from app.services.calculator_service import RentalCalculatorService

app = FastAPI(
    title="Bengaluru Rental Property AI Agent API",
    description="Cloud-native, pipeline-deployable microservice for Bengaluru rental research and financial intelligence",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & Readiness endpoints for Kubernetes / Pipeline verification
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "bengaluru-rental-agent", "version": "1.0.0"}


@app.get("/ready", tags=["System"])
def readiness_check():
    return {"status": "ready", "database": "connected", "dependencies": "ok"}


# Property API Endpoints
@app.get("/api/properties", response_model=List[PropertyListing], tags=["Properties"])
def search_properties(
    min_rent: int = Query(0, ge=0),
    max_rent: int = Query(100000, ge=0),
    bhk: Optional[int] = Query(None),
    area: Optional[str] = Query(None),
    furnishing: Optional[str] = Query(None),
    work_location: Optional[str] = Query(None),
    max_commute_mins: Optional[int] = Query(None)
):
    filters = SearchFilter(
        min_rent=min_rent,
        max_rent=max_rent,
        bhk=bhk,
        area=area,
        furnishing=furnishing,
        work_location=work_location,
        max_commute_mins=max_commute_mins
    )
    return PropertyService.filter_properties(filters)


@app.get("/api/properties/{property_id}", response_model=PropertyListing, tags=["Properties"])
def get_property(property_id: str):
    all_props = PropertyService.get_all_properties()
    prop = next((p for p in all_props if p.id == property_id), None)
    if not prop:
        raise HTTPException(status_code=404, detail="Property listing not found")
    return prop


@app.post("/api/calculate", response_model=CostBreakdownResponse, tags=["Financial Calculator"])
def calculate_costs(req: CostBreakdownRequest):
    return RentalCalculatorService.calculate_deal(req)


@app.get("/api/areas", tags=["Locality Insights"])
def get_area_insights():
    return [
        {
            "name": "Banashankari 3rd Stage",
            "rent_index": "Low-Moderate (₹22k-₹26k)",
            "water_reliability": "5/5 (Cauvery Municipal)",
            "metro_line": "Green Line",
            "greenery": "High",
            "best_for": "Serenity, Budget & CBD Commuters"
        },
        {
            "name": "Sahakara Nagar",
            "rent_index": "Moderate (₹25k-₹30k)",
            "water_reliability": "4.8/5 (Cauvery)",
            "metro_line": "Airport Blue Line (Upcoming)",
            "greenery": "Very High",
            "best_for": "Manyata Tech Park, Airport & Family Living"
        },
        {
            "name": "Whitefield (Borewell Rd)",
            "rent_index": "Moderate (₹27k-₹33k)",
            "water_reliability": "4.1/5 (Mixed)",
            "metro_line": "Purple Line",
            "greenery": "Moderate",
            "best_for": "ITPL, Whitefield & Metro Commuters"
        },
        {
            "name": "HSR Layout (Sector 2)",
            "rent_index": "High (₹32k-₹40k)",
            "water_reliability": "4.4/5 (Mixed)",
            "metro_line": "Yellow Line Interchange",
            "greenery": "High",
            "best_for": "Bellandur / EcoSpace ORR & Social Life"
        }
    ]


# Mount static assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_spa():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Bengaluru Rental AI Agent API is Running. Visit /docs for OpenAPI specifications."}
