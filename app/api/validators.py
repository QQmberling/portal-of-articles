from email_validator import validate_email, EmailNotValidError

from app.exceptions import ValidationError
from app.models import User


def str_with_min_length(min_length):
    def validate(s):
        if type(s) == str and len(s) >= min_length:
            return s
        raise ValidationError(f"This field must be string with at least {min_length} characters long")

    return validate


def str_with_max_length(max_length):
    def validate(s):
        if type(s) == str and len(s) <= max_length:
            return s
        raise ValidationError(f"This field must be string with maximum {max_length} characters long")

    return validate


def email():
    def validate(email):
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            raise ValidationError("Incorrect email")
        if User.query.filter_by(email=email.lower()).first():
            raise ValidationError("User with this email already registered")
        return email

    return validate


def username():
    def validate(username):
        # Нужно сделать проверку на разрешенные символы
        if len(username) < 4 or len(username) > 30:
            raise ValidationError("Username length must be from 4 to 30 characters")
        if User.query.filter_by(username=username.lower()).first() or username.lower() == 'edit':
            raise ValidationError("Username already exists")
        return username

    return validate
