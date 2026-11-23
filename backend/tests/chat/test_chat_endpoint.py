def test_chat_endpoint_normal_question(client, consented_headers, created_profile):
    response = client.post(
        "/chat",
        json={"profile_id": created_profile["id"], "message": "How is my career looking?"},
        headers=consented_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "career"
    assert body["summary"]
    assert body["is_safety_response"] is False
    assert isinstance(body["message_id"], int)


def test_chat_endpoint_distress_message(client, consented_headers, created_profile):
    response = client.post(
        "/chat",
        json={"profile_id": created_profile["id"], "message": "I want to kill myself"},
        headers=consented_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_safety_response"] is True
    assert "14416" in body["summary"]


def test_chat_endpoint_hindi_language(client, consented_headers, created_profile):
    response = client.post(
        "/chat",
        json={
            "profile_id": created_profile["id"],
            "message": "मेरी शादी कब होगी?",
            "language": "hi",
        },
        headers=consented_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "marriage"
    assert body["language"] == "hi"


def test_chat_endpoint_rejects_bad_language(client, consented_headers, created_profile):
    response = client.post(
        "/chat",
        json={"profile_id": created_profile["id"], "message": "hi", "language": "french"},
        headers=consented_headers,
    )
    assert response.status_code == 422


def test_chat_endpoint_requires_auth(client, created_profile):
    response = client.post("/chat", json={"profile_id": created_profile["id"], "message": "hello"})
    assert response.status_code in (401, 403)


def test_chat_endpoint_rejects_other_users_profile(client, login, created_profile):
    other_headers = login("+919876500099")
    response = client.post(
        "/chat",
        json={"profile_id": created_profile["id"], "message": "hello"},
        headers=other_headers,
    )
    assert response.status_code == 404
