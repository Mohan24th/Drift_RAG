from app.auth.models import Roles, User
from app.auth.repository import UserRepository
from app.auth.security import (
    create_access_token,
    verify_password,
)
from app.database.models import UserModel


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> str:

        user = self.repository.get_by_username(
            username
        )

        if user is None:
            raise ValueError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise ValueError(
                "User account is inactive."
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError(
                "Invalid username or password."
            )

        if user.role not in Roles.ALL:
            raise ValueError(
                "User has an invalid role."
            )

        return create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role,
        )

    def get_user(
        self,
        user_id: str,
    ) -> UserModel | None:

        return self.repository.get_by_id(
            user_id
        )