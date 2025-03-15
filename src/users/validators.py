import email_validator
from pydantic import ValidationError


def validate_name(name: str) -> str:
    normalized_name = name.strip()
    if len(normalized_name) < 2:
        raise ValidationError("Name must be at least 2 characters long")
    elif any(char.isdigit() for char in normalized_name):
        raise ValidationError("Name cannot contain numbers")
    return normalized_name


def validate_email(user_email: str) -> str:
    try:
        email_info = email_validator.validate_email(
            user_email, check_deliverability=False
        )
        email = email_info.normalized
    except email_validator.EmailNotValidError as error:
        raise ValidationError(str(error))
    else:
        return email
