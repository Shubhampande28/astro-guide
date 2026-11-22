from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_BIRTH = {
    "birth_date": "1990-05-15",
    "birth_time": "08:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 28.6139,
    "longitude": 77.2090,
}


def test_chat_endpoint_normal_question():
    response = client.post("/chat", json={**_BIRTH, "message": "How is my career looking?"})
    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "career"
    assert body["summary"]
    assert body["is_safety_response"] is False


def test_chat_endpoint_distress_message():
    response = client.post("/chat", json={**_BIRTH, "message": "I want to kill myself"})
    assert response.status_code == 200
    body = response.json()
    assert body["is_safety_response"] is True
    assert "14416" in body["summary"]


def test_chat_endpoint_hindi_language():
    response = client.post(
        "/chat",
        json={**_BIRTH, "message": "मेरी शादी कब होगी?", "language": "hi"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "marriage"
    assert body["language"] == "hi"


def test_chat_endpoint_rejects_bad_language():
    response = client.post("/chat", json={**_BIRTH, "message": "hi", "language": "french"})
    assert response.status_code == 422
