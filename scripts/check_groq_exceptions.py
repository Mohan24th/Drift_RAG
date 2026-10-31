try:
    from groq import GroqError, APIError, RateLimitError, ValidationError
    print("Imported: GroqError, APIError, RateLimitError, ValidationError")
except ImportError as e:
    print(f"Import failed: {e}")
