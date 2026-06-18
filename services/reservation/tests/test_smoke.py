def test_smoke():
    """Basic smoke test — ensures test framework is working."""
    assert 1 + 1 == 2

def test_healthz(client):
    """Test healthz endpoint returns 200."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "reservation"

def test_create_reservation_success(client):
    """Test creating a valid reservation."""
    payload = {
        "store_id": "store_001",
        "customer_id": "cust_001",
        "date": "2026-06-20",
        "time_slot": "12:00-13:00",
        "guest_count": 4,
        "table_type": "standard",
    }
    response = client.post("/api/reservations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["store_id"] == "store_001"
    assert data["customer_id"] == "cust_001"
    assert data["status"] == "PENDING"
    assert "id" in data

def test_create_reservation_missing_fields(client):
    """Test validation: missing required fields returns 422."""
    response = client.post("/api/reservations", json={})
    assert response.status_code == 422

def test_create_reservation_invalid_guest_count(client):
    """Test validation: guest_count out of range."""
    payload = {
        "store_id": "store_001",
        "customer_id": "cust_001",
        "date": "2026-06-20",
        "time_slot": "12:00-13:00",
        "guest_count": 50,
    }
    response = client.post("/api/reservations", json=payload)
    assert response.status_code == 422

def test_get_reservation_not_found(client):
    """Test getting non-existent reservation returns 404."""
    response = client.get("/api/reservations/non-existent")
    assert response.status_code == 404

def test_cancel_reservation(client):
    """Test cancelling a reservation."""
    response = client.delete("/api/reservations/res_12345678")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CANCELLED"

def test_list_reservations_empty(client):
    """Test listing reservations with default params."""
    response = client.get("/api/reservations")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["page"] == 1

def test_get_available_slots(client):
    """Test getting available time slots."""
    response = client.get("/api/stores/store_001/slots?date=2026-06-20")
    assert response.status_code == 200
    data = response.json()
    assert data["store_id"] == "store_001"
    assert len(data["slots"]) == 4
    for slot in data["slots"]:
        assert "time" in slot
        assert "available" in slot
        assert "total" in slot
