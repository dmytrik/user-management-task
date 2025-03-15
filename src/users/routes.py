from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.users.models import User
from src.users.schemas import (
    UserCreateRequestSchema,
    UserCreateResponseSchema,
)
from core.database import get_db
from flasgger import swag_from

router = Blueprint('users', __name__, url_prefix='/users')


@router.route('/', methods=['POST'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Create a new user',
    'description': 'Creates a user with name and email.',
    'parameters': [
        {'name': 'body', 'in': 'body', 'required': True, 'schema': UserCreateRequestSchema.model_json_schema()},
    ],
    'responses': {
        '201': {'description': 'User created', 'schema': UserCreateResponseSchema.model_json_schema()},
        '422': {'description': 'Validation error'},
        '409': {'description': 'Email already exists'},
        '500': {'description': 'Server error'},
    }
})
def create_user():
    """Creates a new user."""
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


@router.route('/', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Get all users',
    'description': 'Returns a list of all users.',
    'responses': {
        '200': {'description': 'List of users', 'schema': {'type': 'array', 'items': UserCreateResponseSchema.model_json_schema()}},
        '500': {'description': 'Server error'},
    }
})
def get_users():
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
