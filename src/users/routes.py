from flask import Blueprint, jsonify, request
from sqlalchemy import select

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
    except Exception:
        session.rollback()
        return jsonify({"detail": "Unexpected server error"}), 500