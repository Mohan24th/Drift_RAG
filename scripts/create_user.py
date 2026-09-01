import sys
from getpass import getpass
from uuid import uuid4

from app.auth.models import Roles
from app.auth.repository import UserRepository
from app.auth.security import hash_password
from app.database.connection import SessionLocal
from app.database.models import UserModel


def main():

    if len(sys.argv) != 3:
        print(
            "Usage: "
            "python -m scripts.create_user "
            "<username> <role>"
        )
        sys.exit(1)

    username = sys.argv[1].strip()
    role = sys.argv[2].upper()

    if not username:
        print("Username cannot be empty.")
        sys.exit(1)

    if role not in Roles.ALL:
        print(
            f"Invalid role: {role}. "
            f"Choose from: {', '.join(sorted(Roles.ALL))}"
        )
        sys.exit(1)

    password = getpass(
        "Password: "
    )

    confirm = getpass(
        "Confirm password: "
    )

    if password != confirm:
        print("Passwords do not match.")
        sys.exit(1)

    if not password:
        print("Password cannot be empty.")
        sys.exit(1)

    session = SessionLocal()

    try:
        repository = UserRepository(
            session=session
        )

        existing = repository.get_by_username(
            username
        )

        if existing is not None:
            print(
                "A user with this username "
                "already exists."
            )
            sys.exit(1)

        user = UserModel(
            id=str(uuid4()),
            username=username,
            password_hash=hash_password(
                password
            ),
            role=role,
            is_active=True,
        )

        repository.create(user)

        session.commit()

        print(
            f"Created user '{username}' "
            f"with role '{role}'."
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()