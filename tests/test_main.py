from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_request():
    response = client.post(
        "/requests",
        json={
            "title": "Laptop issue",
            "description": "The laptop shuts down unexpectedly.",
            "priority": "High",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Laptop issue"
    assert data["description"] == "The laptop shuts down unexpectedly."
    assert data["priority"] == "High"
    assert data["status"] == "Open"
    assert isinstance(data["id"], int)
    assert "created_at" in data


def test_create_request_with_default_priority():
    response = client.post(
        "/requests",
        json={
            "title": "Keyboard issue",
            "description": "Some keys are not responding.",
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "Medium"


def test_create_request_with_invalid_title():
    response = client.post(
        "/requests",
        json={
            "title": "PC",
            "description": "The computer is not working.",
            "priority": "High",
        },
    )

    assert response.status_code == 422


def test_create_request_with_invalid_priority():
    response = client.post(
        "/requests",
        json={
            "title": "Laptop issue",
            "description": "The laptop shuts down unexpectedly.",
            "priority": "Urgent",
        },
    )

    assert response.status_code == 422


def test_list_requests():
    create_response = client.post(
        "/requests",
        json={
            "title": "Monitor issue",
            "description": "The monitor screen is blank.",
            "priority": "Medium",
        },
    )

    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    response = client.get("/requests")

    assert response.status_code == 200
    assert any(item["id"] == request_id for item in response.json())


def test_get_specific_request():
    create_response = client.post(
        "/requests",
        json={
            "title": "Network issue",
            "description": "The computer cannot connect to Wi-Fi.",
            "priority": "High",
        },
    )

    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    response = client.get(f"/requests/{request_id}")

    assert response.status_code == 200
    assert response.json()["id"] == request_id
    assert response.json()["title"] == "Network issue"


def test_get_nonexistent_request():
    response = client.get("/requests/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Service request not found"


def test_update_request_status():
    create_response = client.post(
        "/requests",
        json={
            "title": "Printer issue",
            "description": "The printer is not printing documents.",
            "priority": "Medium",
        },
    )

    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    response = client.patch(
        f"/requests/{request_id}/status",
        params={"new_status": "In Progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
    assert response.json()["id"] == request_id


def test_update_nonexistent_request():
    response = client.patch(
        "/requests/999999/status",
        params={"new_status": "In Progress"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Service request not found"


def test_delete_request():
    create_response = client.post(
        "/requests",
        json={
            "title": "Mouse issue",
            "description": "The mouse is not responding.",
            "priority": "Low",
        },
    )

    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    delete_response = client.delete(f"/requests/{request_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/requests/{request_id}")

    assert get_response.status_code == 404


def test_delete_nonexistent_request():
    response = client.delete("/requests/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Service request not found"