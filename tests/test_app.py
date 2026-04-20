import copy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module
from src.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state after each test."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


# --- GET /activities ---

def test_get_activities_returns_all():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert len(response.json()) > 0


def test_get_activities_structure():
    # Act
    response = client.get("/activities")

    # Assert
    for name, details in response.json().items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_activity_not_found():
    # Arrange
    email = "student@mergington.edu"
    activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_raises_400():
    # Arrange
    email = "duplicate@mergington.edu"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


# --- DELETE /activities/{activity_name}/signup ---

def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    email = "student@mergington.edu"
    activity = "Nonexistent Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_signed_up():
    # Arrange
    email = "notregistered@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]
