from datetime import UTC, datetime, timedelta

import jwt
import pytest
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.surfaced.auth.utilities import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from surfaced.core.config import settings


def test_password_hash():
    password_hash = hash_password("test123")
    assert isinstance(password_hash, str)
    assert password_hash != "test123"


def test_verify_password():
    password_hash = hash_password("test123")
    assert verify_password("test123", password_hash) is True


def test_verify_password_false():
    hashed = hash_password("test123")
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    subject = "test@test.com"
    access_token = create_access_token(subject)

    assert isinstance(access_token, str)

    payload = decode_token(access_token)

    assert payload.sub == subject
    assert payload.type == "access"


def test_create_refresh_token():
    subject = "test@test.com"
    access_token = create_refresh_token(subject)

    assert isinstance(access_token, str)

    payload = decode_token(access_token)

    assert payload.sub == subject
    assert payload.type == "refresh"


def test_decode_expired_token():
    subject = "test@test.com"
    expired_token = jwt.encode(
        payload={"sub": subject, "exp": datetime.now(UTC) - timedelta(minutes=1)},
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(ExpiredSignatureError):
        decode_token(expired_token)


def test_decode_invalid_token():
    dummy_token = "dummy token that cannot be valid"

    with pytest.raises(InvalidTokenError):
        decode_token(dummy_token)
