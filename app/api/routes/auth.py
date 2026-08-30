from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.auth.security import create_access_token


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


DEMO_USERS = {
    "employee": {
        "id": "employee-1",
        "password": "employee123",
        "role": "EMPLOYEE",
    },
    "hr": {
        "id": "hr-1",
        "password": "hr123",
        "role": "HR",
    },
    "admin": {
        "id": "admin-1",
        "password": "admin123",
        "role": "ADMIN",
    },
}


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
):

    user = DEMO_USERS.get(
        request.username
    )

    if (
        user is None
        or user["password"] != request.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    token = create_access_token(
        user_id=user["id"],
        username=request.username,
        role=user["role"],
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )