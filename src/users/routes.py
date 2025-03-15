from flask import (
    Blueprint,
    jsonify,
    request
)
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flasgger import swag_from

from src.users.models import User
from src.users.schemas import (
    UserCreateRequestSchema,
    UserCreateResponseSchema,
    UserUpdateRequestSchema,
    UserUpdateResponseSchema,
)
from core.database import get_db


router = Blueprint("users", __name__, url_prefix="/users")


@router.route("/", methods=["POST"])
@swag_from(
    {
        "tags": ["Users"],
        "summary": "Create a new user",
        "description": "Creates a user with name and email.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": UserCreateRequestSchema.model_json_schema(),
            },
        ],
        "responses": {
            "201": {
                "description": "User created",
                "schema": UserCreateResponseSchema.model_json_schema(),
            },
            "422": {"description": "Validation error"},
            "409": {"description": "Email already exists"},
            "500": {"description": "Server error"},
        },
    }
)
def create_user():
    """Create a new user in the database."""
    session = next(get_db())
    try:
        user_data = UserCreateRequestSchema(**request.get_json())

        stmt = select(User).where(User.email == user_data.email)
        existing_user = session.scalars(stmt).first()

        if existing_user:
            return jsonify({"detail": "Email already exists"}), 409

        new_user = User(name=user_data.name, email=user_data.email)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        res = UserCreateResponseSchema.model_validate(new_user).model_dump()
        return jsonify(res), 201
    except TypeError:
        return jsonify({"detail": "ValidationError"}), 422
    except SQLAlchemyError:
        session.rollback()
        return jsonify({"detail": "Database error"}), 500
    except Exception:
        session.rollback()
        return jsonify({"detail": "Unexpected server error"}), 500
    finally:
        session.close()


@router.route("/", methods=["GET"])
@swag_from(
    {
        "tags": ["Users"],
        "summary": "Get all users",
        "description": "Returns a list of all users.",
        "responses": {
            "200": {
                "description": "List of users",
                "schema": {
                    "type": "array",
                    "items": UserCreateResponseSchema.model_json_schema(),
                },
            },
            "500": {"description": "Server error"},
        },
    }
)
def get_users():
    """Retrieve a list of all users."""
    session = next(get_db())
    try:
        stmt = select(User)
        users = session.scalars(stmt).all()

        res = [
            UserCreateResponseSchema.model_validate(user).model_dump()
            for user in users
        ]

        return jsonify(res), 200
    except SQLAlchemyError:
        return jsonify({"detail": "Database error"}), 500
    except Exception:
        session.rollback()
        return jsonify({"detail": "Unexpected server error"}), 500
    finally:
        session.close()


@router.route("/<int:user_id>/", methods=["PUT"])
@swag_from(
    {
        "tags": ["Users"],
        "summary": "Update a user",
        "description": "Updates a user by ID.",
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "User ID",
            },
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": UserUpdateRequestSchema.model_json_schema(),
            },
        ],
        "responses": {
            "200": {
                "description": "User updated",
                "schema": UserUpdateResponseSchema.model_json_schema(),
            },
            "422": {"description": "Validation error"},
            "404": {"description": "User not found"},
            "409": {"description": "Email already exists"},
            "500": {"description": "Server error"},
        },
    }
)
def update_user(user_id: int):
    """Update an existing user by ID."""
    session = next(get_db())
    try:
        user_data = UserUpdateRequestSchema(**request.get_json())
        print("!!!!!!! i am here")
        stmt = select(User).where(User.id == user_id)
        user = session.scalars(stmt).first()

        if not user:
            return jsonify({"detail": "User not found"}), 404

        if user_data.name is not None:
            user.name = user_data.name

        if user_data.email is not None:
            email_exists_stmt = select(User).where(
                User.email == user_data.email, User.id != user_id
            )
            existing_user = session.scalars(email_exists_stmt).first()
            if existing_user:
                return jsonify(
                    {"detail": f"Email {user_data.email} already exists"}
                ), 409
            user.email = user_data.email

        session.commit()
        session.refresh(user)

        res = UserUpdateResponseSchema.model_validate(user).model_dump()
        return jsonify(res), 200
    except ValidationError:
        session.rollback()
        return jsonify({"detail": "Validation error"}), 422
    except SQLAlchemyError:
        session.rollback()
        return jsonify({"detail": "Database error"}), 500
    except Exception:
        session.rollback()
        return jsonify({"detail": "Unexpected server error"}), 500
    finally:
        session.close()


@router.route("/<int:user_id>/", methods=["GET"])
@swag_from(
    {
        "tags": ["Users"],
        "summary": "Get a user by ID",
        "description": "Returns a user by ID.",
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "User ID",
            },
        ],
        "responses": {
            "200": {
                "description": "User details",
                "schema": UserCreateResponseSchema.model_json_schema(),
            },
            "404": {"description": "User not found"},
            "500": {"description": "Server error"},
        },
    }
)
def get_user(user_id: int):
    """Retrieve a user by ID."""
    session = next(get_db())
    try:
        stmt = select(User).where(User.id == user_id)
        user = session.scalars(stmt).first()
        if not user:
            return jsonify({"detail": "User not found"}), 404
        res = UserCreateResponseSchema.model_validate(user).model_dump()
        return jsonify(res), 200
    except SQLAlchemyError:
        return jsonify({"detail": "Database error"}), 500
    except Exception:
        return jsonify({"detail": "Server error"}), 500
    finally:
        session.close()


@router.route("/<int:user_id>/", methods=["DELETE"])
@swag_from(
    {
        "tags": ["Users"],
        "summary": "Delete a user",
        "description": "Deletes a user by ID.",
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "User ID",
            },
        ],
        "responses": {
            "204": {"description": "User deleted"},
            "404": {"description": "User not found"},
            "500": {"description": "Server error"},
        },
    }
)
def delete_user(user_id: int):
    """Deletes a user by ID."""
    session = next(get_db())
    try:
        stmt = select(User).where(User.id == user_id)
        user = session.scalars(stmt).first()
        if not user:
            return jsonify({"detail": "User not found"}), 404
        session.delete(user)
        session.commit()
        return "", 204
    except SQLAlchemyError:
        session.rollback()
        return jsonify({"detail": "Database error"}), 500
    except Exception:
        session.rollback()
        return jsonify({"detail": "Server error"}), 500
    finally:
        session.close()
