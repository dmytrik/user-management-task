from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from src.users.validators import validate_name, validate_email


class UserBaseSchema(BaseModel):
    """Base schema for user data with name and email."""

    name: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        """Validate the name field."""
        return validate_name(value)

    @field_validator("email")
    @classmethod
    def check_email(cls, value):
        """Validate the email field."""
        return validate_email(value)


class UserCreateRequestSchema(UserBaseSchema):
    """Schema for creating a new user request."""
    pass


class UserCreateResponseSchema(BaseModel):
    """Schema for user creation response."""
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequestSchema(UserBaseSchema):
    """Schema for updating a user request."""
    pass


class UserUpdateResponseSchema(UserCreateResponseSchema):
    """Schema for user update response."""
    pass
