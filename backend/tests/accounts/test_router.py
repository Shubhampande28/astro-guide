def test_otp_verify_wrong_code_fails(client, monkeypatch):
    from app.accounts import otp

    monkeypatch.setattr(otp, "send_otp", lambda phone, code: None)
    client.post("/auth/otp/request", json={"phone_number": "+919876500001"})
    response = client.post(
        "/auth/otp/verify", json={"phone_number": "+919876500001", "code": "000000"}
    )
    assert response.status_code == 400


def test_otp_verify_without_request_fails(client):
    response = client.post(
        "/auth/otp/verify", json={"phone_number": "+919876500002", "code": "123456"}
    )
    assert response.status_code == 400


def test_guest_login_requires_no_phone_number(client):
    response = client.post("/auth/guest")
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_guest_token_works_like_a_real_login(client):
    token = client.post("/auth/guest").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/profiles", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    consent_response = client.post("/me/consent", headers=headers)
    assert consent_response.status_code == 204


def test_each_guest_login_is_a_separate_account(client):
    token_a = client.post("/auth/guest").json()["access_token"]
    token_b = client.post("/auth/guest").json()["access_token"]
    assert token_a != token_b


def test_login_returns_working_token(client, auth_headers):
    response = client.get("/profiles", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_unauthenticated_request_rejected(client):
    response = client.get("/profiles")
    assert response.status_code in (401, 403)


def test_create_profile_requires_consent(client, auth_headers, profile_payload):
    response = client.post("/profiles", json=profile_payload, headers=auth_headers)
    assert response.status_code == 403


def test_create_profile_succeeds_after_consent(created_profile, profile_payload):
    assert created_profile["name"] == profile_payload["name"]
    assert created_profile["birth_date"] == profile_payload["birth_date"]
    assert created_profile["birth_time"] == profile_payload["birth_time"]
    assert created_profile["latitude"] == profile_payload["latitude"]


def test_max_five_profiles_per_account(client, consented_headers, profile_payload):
    for i in range(5):
        payload = {**profile_payload, "name": f"Profile {i}"}
        response = client.post("/profiles", json=payload, headers=consented_headers)
        assert response.status_code == 201

    response = client.post(
        "/profiles", json={**profile_payload, "name": "One too many"}, headers=consented_headers
    )
    assert response.status_code == 400


def test_get_and_update_profile(client, consented_headers, created_profile):
    profile_id = created_profile["id"]

    response = client.get(f"/profiles/{profile_id}", headers=consented_headers)
    assert response.status_code == 200

    response = client.patch(
        f"/profiles/{profile_id}", json={"name": "New Name"}, headers=consented_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_cannot_access_another_users_profile(client, login, created_profile):
    other_headers = login("+919876500003")
    response = client.get(f"/profiles/{created_profile['id']}", headers=other_headers)
    assert response.status_code == 404


def test_delete_profile(client, consented_headers, created_profile):
    profile_id = created_profile["id"]
    response = client.delete(f"/profiles/{profile_id}", headers=consented_headers)
    assert response.status_code == 204

    response = client.get(f"/profiles/{profile_id}", headers=consented_headers)
    assert response.status_code == 404


def test_history_and_feedback_flow(client, consented_headers, created_profile):
    profile_id = created_profile["id"]

    chat_response = client.post(
        "/chat",
        json={"profile_id": profile_id, "message": "How is my career looking?"},
        headers=consented_headers,
    )
    assert chat_response.status_code == 200
    message_id = chat_response.json()["message_id"]

    history_response = client.get(f"/profiles/{profile_id}/history", headers=consented_headers)
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["id"] == message_id
    assert history[0]["topic"] == "career"
    assert history[0]["is_accurate"] is None

    feedback_response = client.post(
        f"/profiles/{profile_id}/history/{message_id}/feedback",
        json={"is_accurate": True},
        headers=consented_headers,
    )
    assert feedback_response.status_code == 204

    history_response = client.get(f"/profiles/{profile_id}/history", headers=consented_headers)
    assert history_response.json()[0]["is_accurate"] is True


def test_delete_my_data_removes_everything(client, consented_headers, created_profile):
    profile_id = created_profile["id"]
    client.post(
        "/chat",
        json={"profile_id": profile_id, "message": "How is my career looking?"},
        headers=consented_headers,
    )

    response = client.delete("/me", headers=consented_headers)
    assert response.status_code == 204

    response = client.get("/profiles", headers=consented_headers)
    assert response.status_code == 401
