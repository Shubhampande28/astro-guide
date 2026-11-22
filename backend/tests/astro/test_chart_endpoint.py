from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chart_endpoint_returns_full_kundli() -> None:
    response = client.post(
        "/chart",
        json={
            "birth_date": "1990-05-15",
            "birth_time": "08:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "as_of": "1990-05-15T12:00:00Z",
        },
    )
    assert response.status_code == 200
    body = response.json()

    assert "lagna" in body
    assert 0.0 <= body["lagna"]["sidereal_longitude_deg"] < 360.0

    grahas = {g["graha"]: g for g in body["grahas"]}
    assert set(grahas) == {
        "Sun",
        "Moon",
        "Mars",
        "Mercury",
        "Jupiter",
        "Venus",
        "Saturn",
        "Rahu",
        "Ketu",
    }
    for g in grahas.values():
        assert 1 <= g["house"] <= 12
        assert 0.0 <= g["degree_in_sign"] < 30.0

    # Ketu is always exactly 180 degrees from Rahu.
    ketu_lon = grahas["Ketu"]["sidereal_longitude_deg"]
    rahu_lon = grahas["Rahu"]["sidereal_longitude_deg"]
    diff = (ketu_lon - rahu_lon) % 360
    assert abs(diff - 180.0) < 1e-6

    assert len(body["vimshottari"]) == 9
    assert body["current_maha_dasha"] is not None


def test_chart_endpoint_rejects_bad_latitude() -> None:
    response = client.post(
        "/chart",
        json={
            "birth_date": "1990-05-15",
            "birth_time": "08:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 200.0,
            "longitude": 77.2090,
        },
    )
    assert response.status_code == 422
