from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    """Restore the in-memory activities state before each test."""
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Create a FastAPI test client for the app."""
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert "description" in response.json()[expected_activity]


def test_successful_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "teststudent@mergington.edu"
    request_params = {"email": new_email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=request_params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    request_params = {"email": existing_email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=request_params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    request_params = {"email": email_to_remove}

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params=request_params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email_to_remove} from {activity_name}"}
    assert email_to_remove not in activities[activity_name]["participants"]
