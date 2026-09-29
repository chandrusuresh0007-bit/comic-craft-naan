import os

os.environ["DATABASE_URL"] = "sqlite:///./test_pocketsmart.db"
os.environ["SESSION_SECRET"] = "test-session-secret"
os.environ["JWT_SECRET"] = "test-jwt-secret"
os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app,
    raise_server_exceptions=True,
)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_home_page():

    response = client.get("/")

    assert response.status_code == 200

    assert "PocketSmart AI" in response.text


def test_register_and_login():

    email = "test@example.com"

    register_response = client.post(
        "/api/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "password123",
        },
    )

    assert register_response.status_code in {
        200,
        409,
    }

    if register_response.status_code == 409:

        login_response = client.post(
            "/api/login",
            json={
                "email": email,
                "password": "password123",
            },
        )

        assert login_response.status_code == 200


def test_home_recommendation():

    email = "home-test@example.com"

    client.post(
        "/api/register",
        json={
            "name": "Home Tester",
            "email": email,
            "password": "password123",
        },
    )

    response = client.post(
        "/api/generate-home",
        json={
            "budget": 50000,
            "rooms": [
                "living room"
            ],
            "style": "modern",
            "priorities": [
                "storage"
            ],
            "notes": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["planner"] == "home"
    assert data["budget"] == 50000
    assert len(data["items"]) > 0


def test_party_recommendation():

    email = "party-test@example.com"

    client.post(
        "/api/register",
        json={
            "name": "Party Tester",
            "email": email,
            "password": "password123",
        },
    )

    response = client.post(
        "/api/generate-party",
        json={
            "budget": 75000,
            "guests": 50,
            "event_type": "birthday",
            "venue": "hotel",
            "city": "Chennai",
            "food_preference": "mixed",
            "notes": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["planner"] == "party"
    assert len(data["items"]) > 0
