# tests/test_app.py
"""
PyTest test suite for the Flask CRUD application.

We create an application with a separate (in-memory) SQLite database so that
tests do not depend on a real SQL Server instance.
"""

import json
import pytest

from app import create_app, db, Bank


@pytest.fixture
def app():
    """
    Test fixture that creates and configures a new app instance for each test.

    We use SQLite in memory so tests are isolated and fast.
    """
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config)

    # Create all tables in the SQLite test database
    with app.app_context():
        db.create_all()

    yield app

    # Teardown: drop all tables after tests finish
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client fixture."""
    return app.test_client()


def test_api_create_bank(client):
    """Test the API endpoint that creates a new bank."""
    payload = {"name": "Test Bank", "location": "Test City"}
    response = client.post(
        "/api/banks", data=json.dumps(payload), content_type="application/json"
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Bank"
    assert data["location"] == "Test City"
    assert "id" in data


def test_api_get_banks(client):
    """Test retrieving all banks via the API."""
    # First create a bank to ensure there is data
    client.post(
        "/api/banks",
        data=json.dumps({"name": "Bank A", "location": "City A"}),
        content_type="application/json",
    )
    client.post(
        "/api/banks",
        data=json.dumps({"name": "Bank B", "location": "City B"}),
        content_type="application/json",
    )

    response = client.get("/api/banks")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_api_get_single_bank(client):
    """Test retrieving a single bank via the API."""
    # Create a bank first
    create_response = client.post(
        "/api/banks",
        data=json.dumps({"name": "Single Bank", "location": "Single City"}),
        content_type="application/json",
    )
    bank_id = create_response.get_json()["id"]

    # Retrieve the same bank
    response = client.get(f"/api/banks/{bank_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == bank_id
    assert data["name"] == "Single Bank"


def test_api_update_bank(client):
    """Test updating a bank via the API."""
    # Create a bank
    create_response = client.post(
        "/api/banks",
        data=json.dumps({"name": "Old Name", "location": "Old City"}),
        content_type="application/json",
    )
    bank_id = create_response.get_json()["id"]

    # Update only the location
    update_payload = {"location": "New City"}
    response = client.put(
        f"/api/banks/{bank_id}",
        data=json.dumps(update_payload),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["location"] == "New City"
    assert data["name"] == "Old Name"  # Name should be unchanged


def test_api_delete_bank(client):
    """Test deleting a bank via the API."""
    # Create a bank
    create_response = client.post(
        "/api/banks",
        data=json.dumps({"name": "Delete Me", "location": "Somewhere"}),
        content_type="application/json",
    )
    bank_id = create_response.get_json()["id"]

    # Delete the bank
    delete_response = client.delete(f"/api/banks/{bank_id}")
    assert delete_response.status_code == 200

    # Ensure the bank no longer exists
    get_response = client.get(f"/api/banks/{bank_id}")
    assert get_response.status_code == 404
