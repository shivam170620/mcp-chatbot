import os
from typing import Optional, Dict

class GeminiClientWrapper:
    """Wrapper for the Gemini client to handle generation requests."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = "gemini-2.0-flash", mock_mode: bool = False):
        self.mock_mode = mock_mode

        if not mock_mode:
            import google.generativeai as genai

            if api_key is None:
                api_key = os.getenv("GEMINI_API_KEY")
            if model_name is None:
                model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-pro")

            if not api_key:
                raise ValueError("GEMINI_API_KEY must be set in env or passed directly")

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.mock_responses = {}

    def set_mock_response(self, step_id: str, response: Dict):
        if not self.mock_mode:
            raise ValueError("Cannot set mock responses when not in mock mode")
        self.mock_responses[step_id] = response

    def generate_response(self, prompt: str, step_id: Optional[str] = None) -> str:
        if self.mock_mode:
            return self.mock_responses.get(step_id, {}).get("response", "Mocked response")
        else:
            response = self.model.generate_content(prompt)
            return response.text.strip()
