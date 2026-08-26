from sqlalchemy import inspect

from app.database.connection import engine


def main():
    inspector = inspect(engine)

    tables = inspector.get_table_names()

    print("Database tables:")

    for table in tables:
        print(f"- {table}")


if __name__ == "__main__":
    main()