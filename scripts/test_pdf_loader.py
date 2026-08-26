from app.ingestion.pdf_loader import load_pdf


def main():
    file_path = "data/test_documents/company_policy.pdf"

    text = load_pdf(file_path)

    print("Extracted characters:", len(text))

    print("\n=== EXTRACTED TEXT ===\n")
    print(text[:2000])


if __name__ == "__main__":
    main()