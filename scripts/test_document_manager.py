from app.ingestion.document_manager import DocumentManager


def main():
    manager = DocumentManager()

    document = manager.create_document(
        "Leave Policy"
    )

    version = manager.create_version(
        document=document,
        source_file="data/v1/company_policy.txt",
        version_number=1,
    )

    print("Document")
    print("ID:", document.document_id)
    print("Name:", document.name)

    print("\nVersion")
    print("ID:", version.version_id)
    print("Document ID:", version.document_id)
    print("Version:", version.version_number)
    print("Stored at:", version.file_path)


if __name__ == "__main__":
    main()