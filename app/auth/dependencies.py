from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.models import User
from app.auth.repository import UserRepository
from app.auth.security import decode_access_token


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    session: Session = Depends(get_db),
) -> User:

    token = credentials.credentials

    try:
        payload = decode_access_token(
            token
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    repository = UserRepository(
        session=session
    )

    user = repository.get_by_id(
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive.",
        )

    return User(
        id=user.id,
        username=user.username,
        role=user.role,
    )


def require_roles(
    *allowed_roles: str,
):

    def dependency(
        current_user: User = Depends(
            get_current_user
        ),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to perform this action."
                ),
            )

        return current_user

    return dependency