from app.database.connection import engine
from app.database.models import Base


def main():
    Base.metadata.create_all(engine)

    print("Database tables created successfully.")


if __name__ == "__main__":
    main()