import pytest # noqa: F401
import json

def test_create_user(test_client, db_session):
    unique_email = "user_test_create@example.com"
    response = test_client.post("/users/", data=json.dumps({"name": "John Doe", "email": unique_email}), content_type="application/json")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    assert response.json["name"] == "John Doe"
    assert response.json["email"] == unique_email

def test_create_user_duplicate_email(test_client, db_session):
    unique_email = "duplicate@example.com"
    response = test_client.post("/users/", data=json.dumps({"name": "First User", "email": unique_email}), content_type="application/json")
    assert response.status_code == 201
    response = test_client.post("/users/", data=json.dumps({"name": "Second User", "email": unique_email}), content_type="application/json")
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    assert response.json["detail"] == "Email already exists"

def test_create_user_invalid_data(test_client, db_session):
    response = test_client.post("/users/", data=json.dumps({"name": "test1234", "email": "test@mail.com"}), content_type="application/json")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    assert "detail" in response.json

def test_get_users(test_client, db_session):
    response = test_client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_user(test_client, db_session):
    unique_email = "user_test_get@example.com"
    response = test_client.post("/users/", data=json.dumps({"name": "Alice", "email": unique_email}), content_type="application/json")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    user_id = response.json["id"]
    response = test_client.get(f"/users/{user_id}/")
    assert response.status_code == 200
    assert response.json["name"] == "Alice"

def test_get_user_not_found(test_client, db_session):
    response = test_client.get("/users/999/")
    assert response.status_code == 404
    assert response.json["detail"] == "User not found"

def test_update_user(test_client, db_session):
    unique_email = "user_test_update@example.com"
    response = test_client.post("/users/", data=json.dumps({"name": "Bob", "email": unique_email}), content_type="application/json")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    user_id = response.json["id"]

    updated_name = "Bobby"
    response = test_client.put(f"/users/{user_id}/", data=json.dumps({"name": updated_name, "email": unique_email}), content_type="application/json")
    assert response.status_code == 200
    assert response.json["name"] == updated_name

def test_update_user_duplicate_email(test_client, db_session):
    response = test_client.post("/users/", data=json.dumps({"name": "UserOne", "email": "user1@example.com"}), content_type="application/json")
    assert response.status_code == 201

    response = test_client.post("/users/", data=json.dumps({"name": "UserTwo", "email": "user2@example.com"}), content_type="application/json")
    assert response.status_code == 201
    user2_id = response.json["id"]

    response = test_client.put(f"/users/{user2_id}/", data=json.dumps({"name": "UserTwo Updated", "email": "user1@example.com"}), content_type="application/json")
    assert response.status_code == 409
    assert response.json["detail"] == "Email user1@example.com already exists"

def test_update_user_invalid_data(test_client, db_session):
    unique_email = "user_test_invalid@example.com"
    response = test_client.post("/users/", data=json.dumps({"name": "Test", "email": unique_email}), content_type="application/json")
    assert response.status_code == 201
    user_id = response.json["id"]

    response = test_client.put(f"/users/{user_id}/", data=json.dumps({"name": "Test", "email": "invalid-email"}), content_type="application/json")
    assert response.status_code == 422
    assert "detail" in response.json

def test_update_user_not_found(test_client, db_session):
    response = test_client.put("/users/999/", data=json.dumps({"name": "Nonexistent", "email": "none@example.com"}), content_type="application/json")
    assert response.status_code == 404
    assert response.json["detail"] == "User not found"

def test_delete_user(test_client, db_session):
    unique_email = "user_test_delete@example.com"
    response = test_client.post("/users/", data=json.dumps({"name": "Charlie", "email": unique_email}), content_type="application/json")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    user_id = response.json["id"]
    response = test_client.delete(f"/users/{user_id}/")
    assert response.status_code == 204

def test_delete_user_not_found(test_client, db_session):
    response = test_client.delete("/users/999/")
    assert response.status_code == 404
    assert response.json["detail"] == "User not found"
