from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth import security


def test_password_hash_roundtrip():
    digest = security.hash_password("correct horse battery")
    assert digest != "correct horse battery"
    assert security.verify_password("correct horse battery", digest)
    assert not security.verify_password("wrong password!!", digest)


def test_token_roundtrip():
    token = security.create_access_token(7, "admin")
    payload = security.decode_access_token(token)
    assert payload["sub"] == "7"
    assert payload["role"] == "admin"


def test_expired_token_rejected():
    expired = jwt.encode(
        {"sub": "1", "role": "admin",
         "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        security.JWT_SECRET, algorithm=security.JWT_ALGORITHM,
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        security.decode_access_token(expired)


def test_tampered_token_rejected():
    forged = jwt.encode({"sub": "1", "role": "admin"}, "other-secret-xxxxxxxxxxxxxxxxxxxxxxxx",
                        algorithm="HS256")
    with pytest.raises(jwt.InvalidTokenError):
        security.decode_access_token(forged)