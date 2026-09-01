from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import UserModel


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_username(
        self,
        username: str,
    ) -> UserModel | None:

        statement = (
            select(UserModel)
            .where(
                UserModel.username == username
            )
            .limit(1)
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def get_by_id(
        self,
        user_id: str,
    ) -> UserModel | None:

        statement = (
            select(UserModel)
            .where(
                UserModel.id == user_id
            )
            .limit(1)
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def create(
        self,
        user: UserModel,
    ) -> UserModel:

        self.session.add(user)
        self.session.flush()

        return user