from sqlalchemy import text

from app.database.connection import engine


def main():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT version();")
        )

        print("Database connection successful!")
        print(result.scalar())


if __name__ == "__main__":
    main()