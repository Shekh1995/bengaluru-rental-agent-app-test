from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Bengaluru Rental Property Agent" in response.text


def test_get_properties():
    response = client.get("/api/properties")
    assert response.status_code == 200
    properties = response.json()
    assert isinstance(properties, list)
    assert len(properties) >= 4


def test_filter_properties_by_bhk():
    response = client.get("/api/properties?bhk=2")
    assert response.status_code == 200
    properties = response.json()
    for prop in properties:
        assert prop["bhk"] == 2


def test_calculate_endpoint():
    payload = {
        "rent_monthly": 28000,
        "deposit": 120000,
        "maintenance": 2000,
        "brokerage": 0,
        "agreement_charges": 1500
    }
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_monthly_burn"] == 30000
    assert data["total_initial_move_in_cost"] == 151500


def test_get_areas():
    response = client.get("/api/areas")
    assert response.status_code == 200
    areas = response.json()
    assert len(areas) >= 4
