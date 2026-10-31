from app.database.connection import engine
from sqlalchemy import text

def audit_indexes():
    with engine.connect() as conn:
        # Get all indexes for the relevant tables
        result = conn.execute(text(
            "SELECT tablename, indexname, indexdef "
            "FROM pg_indexes "
            "WHERE tablename IN ('chunks', 'document_versions', 'documents');"
        ))
        print("--- Actual Database Indexes ---")
        for row in result:
            print(f"Table: {row[0]} | Index: {row[1]} | Def: {row[2]}")

if __name__ == "__main__":
    audit_indexes()
