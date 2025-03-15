from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from src.users.validators import validate_name, validate_email


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_email(cls, value):
        return validate_name(value)

    @field_validator("email")
    @classmethod
    def validate_password(cls, value):
        return validate_email(value)


class UserCreateRequestSchema(UserBaseSchema):
    pass


class UserCreateResponseSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequestSchema(UserBaseSchema):
    name: Optional[str]
    email: Optional[EmailStr]


class UserUpdateResponseSchema(UserCreateResponseSchema):
    pass
