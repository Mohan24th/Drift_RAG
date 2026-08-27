from groq import Groq

from app.config import settings


class LLM:
    def __init__(
        self,
        model: str | None = None,
    ):
        self.client = Groq(
            api_key=settings.groq_api_key
        )

        self.model = (
            model
            or settings.llm_model
        )

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

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "LLM returned an empty response"
            )

        return content