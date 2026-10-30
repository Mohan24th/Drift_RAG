
import logging

from groq import Groq

from app.config import settings

logger = logging.getLogger(__name__)


class LLM:
    def __init__(
        self,
        model: str | None = None,
        fallback_model: str | None = None,
        timeout: float = 30.0,
    ):
        self.client = Groq(
            api_key=settings.groq_api_key,
            timeout=timeout,
            max_retries=1,
        )

        self.model = model or settings.llm_model
        self.fallback_model = (
            fallback_model or settings.llm_fallback_model
        )

    def _call_model(self, prompt: str, model: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content or not content.strip():
            raise ValueError(f"Model {model} returned an empty response.")

        return content.strip()

    def generate(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            return self._call_model(prompt, self.model)

        except Exception as primary_error:
            logger.warning(
                "Primary LLM failed (%s): %s",
                self.model,
                type(primary_error).__name__,
            )

        if (
            self.fallback_model
            and self.fallback_model != self.model
        ):
            try:
                logger.info(
                    "Attempting fallback LLM: %s",
                    self.fallback_model,
                )
                return self._call_model(
                    prompt,
                    self.fallback_model,
                )

            except Exception as fallback_error:
                logger.error(
                    "Fallback LLM failed (%s): %s",
                    self.fallback_model,
                    type(fallback_error).__name__,
                )

                raise RuntimeError(
                    "Both primary and fallback LLM requests failed. "
                    "Check model availability, API quota, and connectivity."
                ) from fallback_error

        raise RuntimeError(
            "Primary LLM request failed and no distinct fallback model "
            "is configured."
        ) from primary_error
