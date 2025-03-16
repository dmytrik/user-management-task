from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flasgger import swag_from

from core.settings import settings
from core.utils import upload_file_to_s3, delete_file_from_s3
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
        "description": "Creates a user with name, email, and optional avatar upload.",
        "consumes": ["multipart/form-data"],
        "parameters": [
            {
                "name": "name",
                "in": "formData",
                "type": "string",
                "required": True,
                "description": "The name of the user",
            },
            {
                "name": "email",
                "in": "formData",
                "type": "string",
                "required": True,
                "description": "The email of the user",
            },
            {
                "name": "avatar",
                "in": "formData",
                "type": "file",
                "required": False,
                "description": "The user's avatar image",
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
        user_data = UserCreateRequestSchema(**request.form)

        stmt = select(User).where(User.email == user_data.email)
        existing_user = session.scalars(stmt).first()
        if existing_user:
            return jsonify({"detail": "Email already exists"}), 409

        new_user = User(name=user_data.name, email=user_data.email)
        session.add(new_user)
        session.flush()

        if "avatar" in request.files:
            avatar_file = request.files["avatar"]
            if avatar_file.filename:
                avatar_url = upload_file_to_s3(
                    avatar_file, settings.aws_s3_bucket, new_user.id
                )
                new_user.avatar = avatar_url

        session.commit()
        session.refresh(new_user)

        res = UserCreateResponseSchema.model_validate(new_user).model_dump()
        return jsonify(res), 201
    except TypeError:
        return jsonify({"detail": "Validation error"}), 422
    except SQLAlchemyError:
        session.rollback()
        return jsonify({"detail": "Database error"}), 500
    except Exception as e:
        session.rollback()
        return jsonify({"detail": f"Unexpected server error: {str(e)}"}), 500
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
@swag_from({
    "tags": ["Users"],
    "summary": "Update a user",
    "description": "Updates a user by ID with required name and email, and optional avatar upload.",
    "consumes": ["multipart/form-data"],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "User ID",
        },
        {
            "name": "name",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "The updated name of the user",
        },
        {
            "name": "email",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "The updated email of the user",
        },
        {
            "name": "avatar",
            "in": "formData",
            "type": "file",
            "required": False,
            "description": "The updated avatar image",
        },
    ],
    "responses": {
        "200": {
            "description": "User updated",
            "schema": UserUpdateResponseSchema.model_json_schema(),
        },
        "422": {"description": "Validation error or missing required fields"},
        "404": {"description": "User not found"},
        "409": {"description": "Email already exists"},
        "500": {"description": "Server error"},
    },
})
def update_user(user_id: int):
    """Update an existing user by ID with all required fields."""
    session = next(get_db())
    try:
        user_data = UserUpdateRequestSchema(**request.form)

        stmt = select(User).where(User.id == user_id)
        user = session.scalars(stmt).first()
        if not user:
            return jsonify({"detail": "User not found"}), 404

        email_exists_stmt = select(User).where(
            User.email == user_data.email, User.id != user_id
        )
        existing_user = session.scalars(email_exists_stmt).first()
        if existing_user:
            return jsonify({"detail": f"Email {user_data.email} already exists"}), 409

        user.name = user_data.name
        user.email = user_data.email

        if "avatar" in request.files:
            avatar_file = request.files["avatar"]
            if avatar_file.filename:
                if user.avatar:
                    old_s3_key = user.avatar.split(f"{settings.aws_s3_bucket}.s3.")[1].split("/", 1)[1]
                    delete_file_from_s3(settings.aws_s3_bucket, old_s3_key)
                avatar_url = upload_file_to_s3(avatar_file, settings.aws_s3_bucket, user.id)
                user.avatar = avatar_url

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
    except Exception as e:
        session.rollback()
        return jsonify({"detail": f"Unexpected server error: {str(e)}"}), 500
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
