# from app.ingestion.loader import load_text_file
# from app.ingestion.chunker import chunk_text


# text = load_text_file("data/v1/company_policy.txt")

# print("Loaded characters:", len(text))

# chunks = chunk_text(
#     text,
#     chunk_size=100,
#     chunk_overlap=20,
# )

# print("Number of chunks:", len(chunks))

# for index, chunk in enumerate(chunks, start=1):
#     print(f"\n--- Chunk {index} ---")
#     print(chunk)