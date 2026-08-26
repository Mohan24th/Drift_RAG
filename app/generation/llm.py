import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class LLM:
    def __init__(
        self,
        model: str = "openai/gpt-oss-20b",
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set"
            )

        self.client = Groq(
            api_key=api_key
        )

        self.model = model

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

        return response.choices[0].message.content