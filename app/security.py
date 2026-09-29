from datetime import datetime, timedelta, timezone

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)

from jose import JWTError, jwt

from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.config import settings
from app.database import User, get_db


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ---------------------------------------------------------
# Password hashing
# ---------------------------------------------------------

def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return password_context.verify(
        password,
        password_hash,
    )


# ---------------------------------------------------------
# JWT
# ---------------------------------------------------------

def create_access_token(
    user_id: int,
) -> str:

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.ACCESS_TOKEN_MINUTES,
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> int:

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[
                settings.JWT_ALGORITHM
            ],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError(
                "Missing user id"
            )

        return int(user_id)

    except (
        JWTError,
        ValueError,
        TypeError,
    ) as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        ) from exc


# ---------------------------------------------------------
# Current authenticated user
# ---------------------------------------------------------

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:

    token = request.session.get(
        "access_token"
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login first.",
        )

    user_id = decode_access_token(
        token
    )

    user = db.get(
        User,
        user_id,
    )

    if user is None:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
        )

    return user
