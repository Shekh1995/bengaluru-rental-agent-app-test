from typing import List, Optional
from app.models import PropertyListing, CommuteInfo, LocalityMetrics, SearchFilter
from app.database import repository


SAMPLE_PROPERTIES: List[PropertyListing] = [
    PropertyListing(
        id="blr-bsk-01",
        title="Green Haven Builder Floor",
        area="Banashankari 3rd Stage",
        bhk=2,
        property_type="Builder Floor",
        rent_monthly=24500,
        deposit=120000,
        maintenance=1500,
        furnishing="Semi-Furnished",
        built_up_sqft=1050,
        floor="2nd Floor (with Lift)",
        parking="1 Covered Car + 1 Bike",
        availability="Immediate",
        nearest_metro="Banashankari Metro (Green Line)",
        metro_distance_km=2.2,
        work_commutes=[
            CommuteInfo(destination="CBD / MG Road", travel_time_mins=28, mode="Metro + Auto"),
            CommuteInfo(destination="Manyata Tech Park", travel_time_mins=50, mode="Cab/Bike"),
            CommuteInfo(destination="Bellandur ORR", travel_time_mins=45, mode="NICE Rd/ORR"),
            CommuteInfo(destination="Electronic City", travel_time_mins=35, mode="NICE Road")
        ],
        area_character="Peaceful established BDA layout, tree-lined cross roads, low ambient noise, pristine residential character.",
        nearby_essentials=["Star Supermarket (400m)", "Motherhood Hospital (1.5km)", "Kathreguppe BDA Complex", "Mini Forest Park"],
        verification_flags=["Direct Owner Listing", "Cauvery Municipal Water Grid Verified"],
        google_maps_url="https://maps.google.com/?q=Banashankari+3rd+Stage+Bengaluru",
        listing_source="NoBroker Verified Direct Owner",
        locality_metrics=LocalityMetrics(water_score=4.9, noise_level="Low", green_cover="High", metro_proximity_km=2.2)
    ),
    PropertyListing(
        id="blr-shk-02",
        title="Tree-Lined Residential Flat",
        area="Sahakara Nagar",
        bhk=2,
        property_type="Apartment",
        rent_monthly=27000,
        deposit=130000,
        maintenance=2000,
        furnishing="Semi-Furnished",
        built_up_sqft=1120,
        floor="1st Floor",
        parking="1 Covered Car Parking",
        availability="Immediate / 1st of next month",
        nearest_metro="Kodigehalli Station / Upcoming Airport Blue Line",
        metro_distance_km=1.2,
        work_commutes=[
            CommuteInfo(destination="Manyata Tech Park", travel_time_mins=15, mode="Bike/Cab (Signal-free)"),
            CommuteInfo(destination="Hebbal / Kirloskar Tech Park", travel_time_mins=12, mode="Bike/Car"),
            CommuteInfo(destination="CBD / MG Road", travel_time_mins=35, mode="Ballari Road Elevated"),
            CommuteInfo(destination="Kempegowda Airport", travel_time_mins=30, mode="Airport Highway")
        ],
        area_character="Master-planned residential township layout, 60ft wide tree-lined avenues, large parks, zero freight traffic.",
        nearby_essentials=["Nilgiris & Nature's Basket (600m)", "Aster CMI Hospital (2.5km)", "Cult.fit & Snap Fitness (1km)"],
        verification_flags=["100% Power Backup Verified", "Zero Brokerage"],
        google_maps_url="https://maps.google.com/?q=Sahakara+Nagar+Bengaluru",
        listing_source="Housing.com Verified",
        locality_metrics=LocalityMetrics(water_score=4.8, noise_level="Low", green_cover="High", metro_proximity_km=1.2)
    ),
    PropertyListing(
        id="blr-wfd-03",
        title="Serene Enclave Apartment",
        area="Whitefield (Borewell Road)",
        bhk=2,
        property_type="Apartment",
        rent_monthly=29000,
        deposit=120000,
        maintenance=2500,
        furnishing="Semi-Furnished",
        built_up_sqft=1100,
        floor="3rd Floor (Lift & DG Backup)",
        parking="1 Dedicated Covered Parking",
        availability="Immediate",
        nearest_metro="Hopefarm Channasandra / Kadugodi Metro (Purple Line)",
        metro_distance_km=2.4,
        work_commutes=[
            CommuteInfo(destination="ITPL / Whitefield Tech Corridor", travel_time_mins=12, mode="Metro/Bike"),
            CommuteInfo(destination="Indiranagar / MG Road", travel_time_mins=38, mode="Purple Line Metro Direct"),
            CommuteInfo(destination="Bellandur ORR", travel_time_mins=35, mode="Bypass Road"),
            CommuteInfo(destination="Bagmane Tech Park", travel_time_mins=32, mode="Purple Line + Feeder")
        ],
        area_character="Quiet interior lane set back 200m from main highway; balanced greenery with swift access to tech parks.",
        nearby_essentials=["Reliance Fresh (500m)", "Manipal Hospital (1.8km)", "Nexus Shantiniketan Mall (3.2km)"],
        verification_flags=["Purple Line Metro Connected", "Gated Community Security"],
        google_maps_url="https://maps.google.com/?q=Borewell+Road+Whitefield+Bengaluru",
        listing_source="NoBroker Direct Owner",
        locality_metrics=LocalityMetrics(water_score=4.1, noise_level="Moderate-Low", green_cover="Moderate", metro_proximity_km=2.4)
    ),
    PropertyListing(
        id="blr-hsr-04",
        title="Standalone Sector Floor",
        area="HSR Layout (Sector 2)",
        bhk=2,
        property_type="Builder Floor",
        rent_monthly=33000,
        deposit=150000,
        maintenance=2000,
        furnishing="Semi-Furnished",
        built_up_sqft=1050,
        floor="2nd Floor",
        parking="1 Stilt Car + Bike Parking",
        availability="Immediate",
        nearest_metro="Silk Board / HSR Metro Interchange",
        metro_distance_km=2.0,
        work_commutes=[
            CommuteInfo(destination="Bellandur / EcoSpace ORR", travel_time_mins=18, mode="Agara Road"),
            CommuteInfo(destination="Koramangala", travel_time_mins=12, mode="Direct Road"),
            CommuteInfo(destination="Electronic City", travel_time_mins=25, mode="Elevated Expressway"),
            CommuteInfo(destination="CBD / MG Road", travel_time_mins=30, mode="Hosur Main Road")
        ],
        area_character="Cosmopolitan, tree-lined residential layout with excellent walkability, cafes, high street within 5 mins.",
        nearby_essentials=["MK Ahmed Supermarket (300m)", "Narayana Multispeciality Hospital (1.2km)", "HSR Sector 2 Park"],
        verification_flags=["Direct Owner", "Solar Water Heater Installed"],
        google_maps_url="https://maps.google.com/?q=HSR+Layout+Sector+2+Bengaluru",
        listing_source="99acres Verified Owner",
        locality_metrics=LocalityMetrics(water_score=4.4, noise_level="Low", green_cover="High", metro_proximity_km=2.0)
    ),
    PropertyListing(
        id="blr-jpn-05",
        title="Lush Greens Independent Floor",
        area="JP Nagar (Phase 6)",
        bhk=3,
        property_type="Independent House",
        rent_monthly=36000,
        deposit=180000,
        maintenance=1500,
        furnishing="Semi-Furnished",
        built_up_sqft=1400,
        floor="1st Floor",
        parking="1 Covered Car Parking",
        availability="Immediate",
        nearest_metro="JP Nagar Metro (Green Line) / Yelachenahalli",
        metro_distance_km=1.5,
        work_commutes=[
            CommuteInfo(destination="CBD / MG Road", travel_time_mins=28, mode="Green Line Metro"),
            CommuteInfo(destination="Electronic City", travel_time_mins=30, mode="NICE Road / Bannerghatta"),
            CommuteInfo(destination="Koramangala", travel_time_mins=25, mode="Dairy Circle Route")
        ],
        area_character="Serene, upscale residential setting with massive foliage canopy, cultural venues (Ranga Shankara), high privacy.",
        nearby_essentials=["Ranga Shankara Theatre (800m)", "Fortis Hospital (2km)", "MK Retail", "Sarakki Lake Park"],
        verification_flags=["Independent Entrance", "100% Cauvery Water"],
        google_maps_url="https://maps.google.com/?q=JP+Nagar+6th+Phase+Bengaluru",
        listing_source="NoBroker Verified",
        locality_metrics=LocalityMetrics(water_score=5.0, noise_level="Low", green_cover="High", metro_proximity_km=1.5)
    )
]


class PropertyService:
    @staticmethod
    def get_all_properties() -> List[PropertyListing]:
        stored = repository.get_all()
        return stored if stored is not None else SAMPLE_PROPERTIES

    @staticmethod
    def filter_properties(filters: SearchFilter) -> List[PropertyListing]:
        results = []
        for prop in PropertyService.get_all_properties():
            if filters.min_rent is not None and prop.rent_monthly < filters.min_rent:
                continue
            if filters.max_rent is not None and prop.rent_monthly > filters.max_rent:
                continue
            if filters.bhk and prop.bhk != filters.bhk:
                continue
            if filters.area and filters.area.lower() not in prop.area.lower():
                continue
            if filters.furnishing and filters.furnishing.lower() not in prop.furnishing.lower():
                continue
            if filters.work_location:
                matching_commute = next(
                    (c for c in prop.work_commutes if filters.work_location.lower() in c.destination.lower()),
                    None
                )
                if matching_commute is None:
                    continue
                if (
                    filters.max_commute_mins is not None
                    and matching_commute.travel_time_mins > filters.max_commute_mins
                ):
                    continue
            results.append(prop)
        return sorted(results, key=lambda prop: (-prop.priority_score, prop.rent_monthly))
