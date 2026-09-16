"""
OpenAI API Service Provider
Handles server-side communication with OpenAI's Chat Completions API using the official OpenAI Python SDK.
Features:
- Secure credential reading strictly from environment variable OPENAI_API_KEY
- Timeout, exception handling, and safe logging (never logs or returns API keys)
- Clean AsyncOpenAI client instantiation
- Safe error sanitization (masks any bearer token or key patterns)
- Structured fallback-ready response contracts
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("OpenAIService")

try:
    import openai
    from openai import AsyncOpenAI, OpenAI
    HAS_OPENAI_SDK = True
except ImportError:
    HAS_OPENAI_SDK = False
    logger.warning("Official OpenAI Python SDK is not installed or failed to import.")


class OpenAIService:
    def __init__(self):
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.default_timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "15.0"))

    @property
    def api_key(self) -> Optional[str]:
        """
        Retrieves the OpenAI API key strictly from environment variables or protected .env file.
        Never returns placeholder or empty values.
        """
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            try:
                from ..core.config import settings
                key = getattr(settings, "OPENAI_API_KEY", None)
            except Exception:
                pass

        if not key:
            try:
                # Read directly from protected backend/.env if running locally without shell export
                backend_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
                if os.path.exists(backend_env_path):
                    with open(backend_env_path, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("OPENAI_API_KEY="):
                                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                                break
            except Exception:
                pass

        if key and isinstance(key, str):
            cleaned = key.strip()
            # Ignore placeholder template values
            if cleaned and not cleaned.startswith("your_new_") and len(cleaned) > 5:
                return cleaned
        return None

    @property
    def model(self) -> str:
        return os.getenv("OPENAI_MODEL") or self.default_model

    @property
    def timeout_seconds(self) -> float:
        try:
            return float(os.getenv("OPENAI_TIMEOUT_SECONDS", str(self.default_timeout)))
        except (ValueError, TypeError):
            return self.default_timeout

    def validate_configuration(self) -> Tuple[bool, Optional[str]]:
        """
        Validates whether the OpenAI API key is configured in the environment.
        Never prints or exposes secret values.
        """
        if not HAS_OPENAI_SDK:
            return False, "OpenAI Python SDK is not installed."
        key = self.api_key
        if not key:
            return False, "OPENAI_API_KEY environment variable is not configured or is empty."
        return True, None

    def is_configured(self) -> bool:
        valid, _ = self.validate_configuration()
        return valid

    def _sanitize_error(self, error_str: str) -> str:
        """
        Sanitizes error messages to ensure OpenAI API keys and Bearer tokens
        are never logged, printed, or returned to clients.
        """
        if not error_str:
            return "Unknown error occurred"

        sanitized = error_str
        key = self.api_key
        if key and key in sanitized:
            sanitized = sanitized.replace(key, "[REDACTED_API_KEY]")

        # Redact any standard sk- pattern
        sanitized = re.sub(r"sk-[a-zA-Z0-9_-]{10,}", "[REDACTED_API_KEY]", sanitized)
        # Redact Bearer authorization headers
        sanitized = re.sub(r"Bearer\s+[a-zA-Z0-9_\-\.]{10,}", "Bearer [REDACTED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 250,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a server-side OpenAI Chat Completion with timeout and full error handling.
        Returns a structured dictionary without revealing credentials.
        """
        is_valid, config_err = self.validate_configuration()
        if not is_valid:
            logger.warning("OpenAI chat completion skipped: %s", config_err)
            return {
                "success": False,
                "error": config_err,
                "status": "NOT_CONFIGURED",
                "content": None
            }

        target_model = model or self.model
        client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

        try:
            kwargs: Dict[str, Any] = {
                "model": target_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if response_format:
                kwargs["response_format"] = response_format

            logger.info("Dispatching OpenAI chat completion with model: %s", target_model)
            response = await client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content or ""
            return {
                "success": True,
                "content": content.strip(),
                "model": response.model,
                "status": "READY"
            }

        except openai.AuthenticationError as auth_err:
            safe_msg = "OpenAI authentication failed. Please verify OPENAI_API_KEY configuration."
            logger.error("OpenAI AuthenticationError: %s", safe_msg)
            return {
                "success": False,
                "error": safe_msg,
                "status": "AUTHENTICATION_FAILED",
                "content": None
            }
        except openai.RateLimitError as rate_err:
            safe_msg = "OpenAI rate limit or quota exceeded. Please check your OpenAI account billing."
            logger.error("OpenAI RateLimitError: %s", safe_msg)
            return {
                "success": False,
                "error": safe_msg,
                "status": "RATE_LIMITED",
                "content": None
            }
        except openai.APITimeoutError:
            safe_msg = f"OpenAI request timed out after {self.timeout_seconds} seconds."
            logger.error("OpenAI APITimeoutError: %s", safe_msg)
            return {
                "success": False,
                "error": safe_msg,
                "status": "TIMEOUT",
                "content": None
            }
        except openai.APIConnectionError:
            safe_msg = "Could not connect to OpenAI API servers. Please check network connectivity."
            logger.error("OpenAI APIConnectionError: %s", safe_msg)
            return {
                "success": False,
                "error": safe_msg,
                "status": "CONNECTION_ERROR",
                "content": None
            }
        except Exception as e:
            safe_err = self._sanitize_error(str(e))
            logger.error("OpenAI unexpected error: %s", safe_err)
            return {
                "success": False,
                "error": safe_err,
                "status": "FAILED",
                "content": None
            }


openai_service = OpenAIService()
