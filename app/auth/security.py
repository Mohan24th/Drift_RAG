from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(
    password: str,
) -> str:

    password_bytes = password.encode(
        "utf-8"
    )

    if len(password_bytes) > 72:
        raise ValueError(
            "Password must be 72 bytes or fewer."
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    password_bytes = password.encode(
        "utf-8"
    )

    if len(password_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(
            password_bytes,
            password_hash.encode("utf-8"),
        )

    except ValueError:
        return False


def create_access_token(
    user_id: str,
    username: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = (
        datetime.now(timezone.utc)
        + expires_delta
    )

    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:

    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[ALGORITHM],
        )

    except JWTError as exc:
        raise ValueError(
            "Invalid or expired token."
        ) from exc