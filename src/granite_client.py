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

    def generate(self, prompt: str, max_tokens: int = 600) -> str:
        """
        Generate a response using IBM Granite chat API.

        The prompt is treated as the user turn; system instruction is
        embedded at the top of the prompt string by the agent's build_prompt().

        Args:
            prompt: Full prompt string (system context + user question combined)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        try:
            # Use chat messages format for granite-4-h-small
            # Split prompt into system + user parts if possible
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
            response = self.model.chat(messages=messages, params=params)
            # Extract text from chat response
            result = (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            return result if result else "I was unable to generate a response. Please try again."
        except Exception as e:
            err = str(e)
            if "no_associated_service_instance" in err:
                return (
                    "IBM watsonx.ai service is not linked to this project. "
                    "Please associate a Watson Machine Learning instance with your project."
                )
            return f"LLM error: {err}"

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
