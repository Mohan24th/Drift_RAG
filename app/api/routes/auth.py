from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.auth.repository import UserRepository
from app.auth.service import AuthService


router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=100,
    )

    password: str = Field(
        min_length=1,
        max_length=200,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


def get_auth_service(
    session: Session = Depends(get_db),
) -> AuthService:

    return AuthService(
        repository=UserRepository(
            session=session
        )
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):

    username = request.username.strip()

    if not username:
        raise HTTPException(
            status_code=422,
            detail="Username cannot be empty.",
        )

    try:
        token = service.authenticate(
            username=username,
            password=request.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )