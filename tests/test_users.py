import pytest  # noqa: F401
import io
from werkzeug.datastructures import FileStorage


def test_create_user(test_client, db_session):
    """Test creating a new user without an avatar."""
    unique_email = "user_test_create@example.com"
    response = test_client.post(
        "/users/",
        data={
            "name": "John Doe",
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}"
    )
    assert response.json["name"] == "John Doe"
    assert response.json["email"] == unique_email
    assert response.json["avatar"] is None


def test_create_user_with_avatar(test_client, db_session):
    """Test creating a new user with an avatar."""
    unique_email = "user_with_avatar@example.com"
    avatar_content = b"fake image data"
    avatar_file = FileStorage(
        stream=io.BytesIO(avatar_content),
        filename="avatar.jpg",
        content_type="image/jpeg",
    )
    response = test_client.post(
        "/users/",
        data={
            "name": "Avatar User",
            "email": unique_email,
            "avatar": avatar_file,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}"
    )
    assert response.json["name"] == "Avatar User"
    assert response.json["email"] == unique_email
    assert response.json["avatar"].startswith("https://")


def test_create_user_duplicate_email(test_client, db_session):
    """Test creating a user with a duplicate email."""
    unique_email = "duplicate@example.com"
    response = test_client.post(
        "/users/",
        data={
            "name": "First User",
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    response = test_client.post(
        "/users/",
        data={
            "name": "Second User",
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 409, (
        f"Expected 409, got {response.status_code}"
    )
    assert response.json["detail"] == "Email already exists"


def test_create_user_invalid_data(test_client, db_session):
    """Test creating a user with invalid data (name with numbers)."""
    response = test_client.post(
        "/users/",
        data={
            "name": "test1234",
            "email": "test@mail.com",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 422, (
        f"Expected 422, got {response.status_code}"
    )
    assert "detail" in response.json


def test_get_users(test_client, db_session):
    """Test retrieving all users."""
    response = test_client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_user(test_client, db_session):
    """Test retrieving a user by ID."""
    unique_email = "user_test_get@example.com"
    response = test_client.post(
        "/users/",
        data={
            "name": "Alice",
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}"
    )
    user_id = response.json["id"]
    response = test_client.get(f"/users/{user_id}/")
    assert response.status_code == 200
    assert response.json["name"] == "Alice"
    assert response.json["email"] == unique_email


def test_get_user_not_found(test_client, db_session):
    """Test retrieving a non-existent user."""
    response = test_client.get("/users/999/")
    assert response.status_code == 404
    assert response.json["detail"] == "User not found"


def test_update_user(test_client, db_session):
    """Test updating an existing user without changing the avatar."""
    unique_email = "user_test_update@example.com"
    response = test_client.post(
        "/users/",
        data={
            "name": "Bob",
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}"
    )
    user_id = response.json["id"]

    updated_name = "Bobby"
    response = test_client.put(
        f"/users/{user_id}/",
        data={
            "name": updated_name,
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.json["name"] == updated_name
    assert response.json["email"] == unique_email


def test_update_user_with_avatar(test_client, db_session):
    """Test updating an existing user with a new avatar."""
    unique_email = "user_update_avatar@example.com"
    response = test_client.post(
        "/users/",
        data={
            "name": "Charlie",
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    user_id = response.json["id"]

    avatar_content = b"new fake image data"
    avatar_file = FileStorage(
        stream=io.BytesIO(avatar_content),
        filename="new_avatar.jpg",
        content_type="image/jpeg",
    )
    response = test_client.put(
        f"/users/{user_id}/",
        data={
            "name": "Charlie Updated",
            "email": "new_email@example.com",
            "avatar": avatar_file,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.json["name"] == "Charlie Updated"
    assert response.json["avatar"].startswith("https://")


def test_update_user_duplicate_email(test_client, db_session):
    """Test updating a user with an existing email."""
    response = test_client.post(
        "/users/",
        data={
            "name": "UserOne",
            "email": "user1@example.com",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201

    response = test_client.post(
        "/users/",
        data={
            "name": "UserTwo",
            "email": "user2@example.com",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    user2_id = response.json["id"]

    response = test_client.put(
        f"/users/{user2_id}/",
        data={
            "name": "UserTwo Updated",
            "email": "user1@example.com",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 409
    assert response.json["detail"] == "Email user1@example.com already exists"


def test_update_user_invalid_data(test_client, db_session):
    """Test updating a user with invalid data (invalid email)."""
    unique_email = "user_test_invalid@example.com"
    response = test_client.post(
        "/users/",
        data={
            "name": "Test",
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    user_id = response.json["id"]

    response = test_client.put(
        f"/users/{user_id}/",
        data={
            "name": "Test",
            "email": "invalid-email",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 422
    assert "detail" in response.json


def test_update_user_not_found(test_client, db_session):
    """Test updating a non-existent user."""
    response = test_client.put(
        "/users/999/",
        data={
            "name": "Nonexistent",
            "email": "none@example.com",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 404
    assert response.json["detail"] == "User not found"


def test_delete_user(test_client, db_session):
    """Test deleting an existing user."""
    unique_email = "user_test_delete@example.com"
    response = test_client.post(
        "/users/",
        data={
            "name": "Charlie",
            "email": unique_email,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}"
    )
    user_id = response.json["id"]
    response = test_client.delete(f"/users/{user_id}/")
    assert response.status_code == 204


def test_delete_user_not_found(test_client, db_session):
    """Test deleting a non-existent user."""
    response = test_client.delete("/users/999/")
    assert response.status_code == 404
    assert response.json["detail"] == "User not found"
