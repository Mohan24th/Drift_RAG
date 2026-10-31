import logging
import time
from groq import Groq, APIError, RateLimitError
from app.config import settings

logger = logging.getLogger(__name__)

class LLM:
    def __init__(
        self,
        model: str | None = None,
        fallback_model: str | None = None,
        timeout: float | None = None,
    ):
        self.client = Groq(
            api_key=settings.groq_api_key,
            timeout=timeout if timeout is not None else settings.llm_timeout,
            max_retries=settings.llm_max_retries,
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

    def generate(self, prompt: str) -> tuple[str, str]:
        """
        Generates an answer and returns a tuple of (answer, model_used).
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        start_time = time.perf_counter()
        
        try:
            # Attempt Primary Model
            answer = self._call_model(prompt, self.model)
            latency = time.perf_counter() - start_time
            
            logger.info(
                "LLM Success | Model: %s | Role: primary | Latency: %.4fs | Fallback: No",
                self.model, latency
            )
            return answer, self.model

        except (APIError, RateLimitError) as transient_error:
            # Transient failures trigger fallback
            latency_primary = time.perf_counter() - start_time
            logger.warning(
                "LLM Transient Failure | Model: %s | Error: %s | Latency: %.4fs | Attempting Fallback...",
                self.model, type(transient_error).__name__, latency_primary
            )

            if (
                self.fallback_model
                and self.fallback_model != self.model
            ):
                try:
                    start_fallback = time.perf_counter()
                    answer = self._call_model(prompt, self.fallback_model)
                    latency_fallback = time.perf_counter() - start_fallback
                    
                    logger.info(
                        "LLM Fallback Success | Model: %s | Role: fallback | Latency: %.4fs",
                        self.fallback_model, latency_fallback
                    )
                    return answer, self.fallback_model

                except Exception as fallback_error:
                    logger.error(
                        "LLM Fallback Failed | Model: %s | Error: %s",
                        self.fallback_model, type(fallback_error).__name__,
                    )
                    raise RuntimeError(
                        "Both primary and fallback LLM requests failed. "
                        "Check model availability, API quota, and connectivity."
                    ) from fallback_error

            raise RuntimeError(
                "Primary LLM transient failure and no distinct fallback model configured."
            ) from transient_error

        except Exception as permanent_error:
            # Permanent errors (e.g. ValueError) do not trigger fallback
            latency = time.perf_counter() - start_time
            logger.error(
                "LLM Permanent Failure | Model: %s | Error: %s | Latency: %.4fs | Fallback: Skipped",
                self.model, type(permanent_error).__name__, latency
            )
            
            if isinstance(permanent_error, ValueError):
                raise permanent_error
                
            raise RuntimeError(
                f"LLM permanent failure: {str(permanent_error)}"
            ) from permanent_error
