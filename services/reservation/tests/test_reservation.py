def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "reservation"

def test_create_reservation_success(client):
    payload = {
        "store_id": "store_001",
        "customer_id": "cust_001",
        "date": "2026-06-20",
        "time_slot": "12:00-13:00",
        "guest_count": 4,
    }
    response = client.post("/api/reservations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["store_id"] == "store_001"
    assert data["status"] == "PENDING"
    assert "id" in data

def test_create_reservation_missing_fields(client):
    response = client.post("/api/reservations", json={})
    assert response.status_code == 422

def test_create_reservation_invalid_guest_count(client):
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
    response = client.get("/api/reservations/non-existent")
    assert response.status_code == 404

def test_cancel_reservation(client):
    response = client.delete("/api/reservations/res_12345678")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"

def test_list_reservations_empty(client):
    response = client.get("/api/reservations")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["total"] == 0

def test_get_available_slots(client):
    response = client.get("/api/stores/store_001/slots?date=2026-06-20")
    assert response.status_code == 200
    data = response.json()
    assert len(data["slots"]) == 4
