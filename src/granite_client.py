"""
IBM Granite LLM Integration for Digital Financial Literacy Agent
Uses IBM watsonx.ai with Granite 4 H Small via IBM Cloud Lite
Model: ibm/granite-4-h-small  (chat API)
Embeddings: ibm/slate-125m-english-rtrvr-v2  (fallback: sentence-transformers)
"""

import os
from typing import Optional
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv(override=True)


class GraniteClient:
    """
    Wrapper around IBM watsonx.ai Granite 4 H Small model.
    Uses the /ml/v1/text/chat endpoint for instruction-following Q&A.
    """

    def __init__(self):
        self.api_key = os.getenv("IBM_API_KEY")
        self.project_id = os.getenv("IBM_PROJECT_ID")
        self.watsonx_url = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        self.model_id = os.getenv("GRANITE_MODEL_ID", "ibm/granite-4-h-small")

        if not self.api_key or not self.project_id:
            raise ValueError(
                "IBM_API_KEY and IBM_PROJECT_ID must be set. "
                "Get free IBM Cloud Lite credentials at https://cloud.ibm.com/registration"
            )

        self.credentials = Credentials(
            url=self.watsonx_url,
            api_key=self.api_key,
        )
        self.client = APIClient(self.credentials)
        self._model: Optional[ModelInference] = None

    @property
    def model(self) -> ModelInference:
        """Lazy-load the Granite model inference instance."""
        if self._model is None:
            self._model = ModelInference(
                model_id=self.model_id,
                credentials=self.credentials,
                project_id=self.project_id,
            )
        return self._model

    def generate(self, prompt: str, max_tokens: int = 600, _retries: int = 3) -> str:
        """
        Generate a response using IBM Granite chat API.
        Automatically retries on 429 rate-limit errors with exponential backoff.

        Args:
            prompt: Full prompt string (system context + user question combined)
            max_tokens: Maximum tokens to generate
            _retries: Number of retry attempts on rate-limit (internal)

        Returns:
            Generated text response
        """
        import time

        system_text = (
            "You are a helpful Digital Financial Literacy Assistant for India. "
            "Answer questions about UPI, online scams, interest rates, budgeting, "
            "and personal finance using the provided context. "
            "Be clear, simple, and practical. Cite sources when available."
        )
        messages = [
            {"role": "system", "content": system_text},
            {"role": "user", "content": prompt},
        ]
        params = {
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }

        for attempt in range(_retries):
            try:
                response = self.model.chat(messages=messages, params=params)
                result = (
                    response.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                return result if result else "I was unable to generate a response. Please try again."

            except Exception as e:
                err = str(e)

                # Rate limit (429) — wait and retry
                if "429" in err or "consumption_limit_reached" in err:
                    if attempt < _retries - 1:
                        wait = 10 * (attempt + 1)  # 10s, 20s, 30s
                        print(f"Rate limit hit, retrying in {wait}s (attempt {attempt + 1}/{_retries})")
                        time.sleep(wait)
                        continue
                    return (
                        "IBM Granite is currently busy (free tier rate limit reached). "
                        "Please wait 30 seconds and try again. "
                        "If this persists, try a shorter question or check your IBM Cloud usage."
                    )

                # Service not linked
                if "no_associated_service_instance" in err:
                    return (
                        "IBM watsonx.ai service is not linked to this project. "
                        "Please associate a Watson Machine Learning instance with your project."
                    )

                # Any other error on last attempt
                if attempt == _retries - 1:
                    return (
                        "I encountered a temporary error. Please try again in a moment. "
                        f"(Detail: {err[:120]})"
                    )
                time.sleep(3)

        return "Unable to generate a response after multiple attempts. Please try again."

    def health_check(self) -> dict:
        """Check IBM Watson connection health."""
        try:
            self.client.foundation_models.get_model_specs()
            return {
                "status": "healthy",
                "model": self.model_id,
                "watsonx_url": self.watsonx_url,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
