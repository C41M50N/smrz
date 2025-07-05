from enum import StrEnum
import os
import time

from openai import OpenAI
from pydantic import BaseModel
from typing import TypedDict


class Models(StrEnum):
    # Google Gemini Models
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_FLASH_LITE_PREVIEW = "gemini-2.5-flash-lite-preview-06-17"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    # OpenRouter Models
    OR_LLAMA_4_MAVERICK = "meta-llama/llama-4-maverick"
    OR_LLAMA_3_3_70B_INSTRUCT = "meta-llama/llama-3.3-70b-instruct"
    OR_GPT_4O_MINI = "openai/gpt-4o-mini"
    OR_GPT_4_1_MINI = "openai/gpt-4.1-mini"


class ModelInfo(TypedDict):
    name: str
    provider: str
    cost_per_1M_input_tokens: float
    cost_per_1M_output_tokens: float


MODEL_REGISTRY: dict[Models, ModelInfo] = {
    # Google Gemini Models
    Models.GEMINI_2_5_PRO: {
        "name": "Gemini 2.5 Pro",
        "provider": "Google",
        "cost_per_1M_input_tokens": 20.0,  # 0.20 USD
        "cost_per_1M_output_tokens": 80.0,  # 0.80 USD
    },
    Models.GEMINI_2_5_FLASH: {
        "name": "Gemini 2.5 Flash",
        "provider": "Google",
        "cost_per_1M_input_tokens": 10.0,  # 0.10 USD
        "cost_per_1M_output_tokens": 40.0,  # 0.40 USD
    },
    Models.GEMINI_2_5_FLASH_LITE_PREVIEW: {
        "name": "Gemini 2.5 Flash Lite Preview",
        "provider": "Google",
        "cost_per_1M_input_tokens": 5.0,  # 0.05 USD
        "cost_per_1M_output_tokens": 20.0,  # 0.20 USD
    },
    Models.GEMINI_2_0_FLASH: {
        "name": "Gemini 2.0 Flash",
        "provider": "Google",
        "cost_per_1M_input_tokens": 5.0,  # 0.05 USD
        "cost_per_1M_output_tokens": 20.0,  # 0.20 USD
    },
    # OpenRouter Models
    Models.OR_LLAMA_4_MAVERICK: {
        "name": "Llama 4 Maverick",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 15.0,  # 0.15 USD
        "cost_per_1M_output_tokens": 60.0,  # 0.60 USD
    },
    Models.OR_LLAMA_3_3_70B_INSTRUCT: {
        "name": "Llama 3.3 70B Instruct",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 5.0,  # 0.05 USD
        "cost_per_1M_output_tokens": 25.0,  # 0.25 USD
    },
    Models.OR_GPT_4O_MINI: {
        "name": "GPT-4o Mini",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 15.0,  # 0.15 USD
        "cost_per_1M_output_tokens": 60.0,  # 0.60 USD
    },
    Models.OR_GPT_4_1_MINI: {
        "name": "GPT-4.1 Mini",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 40.0,  # 0.40 USD
        "cost_per_1M_output_tokens": 160.0,  # 1.60 USD
    },
}

# For the models with "Google" as the provider, we use the GEMINI_CLIENT.
GEMINI_CLIENT = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# For the models with "OpenRouter" as the provider, we use the OPENROUTER_CLIENT.
OPENROUTER_CLIENT = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


class LLMClientResponse(BaseModel):
    content: str
    response_time: float
    provider: str
    cost: float


class LLMClient:
    def __init__(self, model: Models):
        self.model = model
        self.provider = self._get_provider()
        self.client = self._get_client()

    def _get_provider(self):
        try:
            return MODEL_REGISTRY[self.model]["provider"]
        except KeyError:
            raise ValueError(f"Unknown model: {self.model}")

    def _get_client(self):
        provider = self.provider

        if provider == "Google":
            return GEMINI_CLIENT
        elif provider == "OpenRouter":
            return OPENROUTER_CLIENT
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate_response(
        self, system_prompt: str, user_prompt: str, temp: float = 0.7
    ):
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temp,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {str(e)}")

        response_time = time.time() - start_time

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Failed to generate response")

        usage = response.usage
        if not usage:
            raise RuntimeError("Response usage information is missing")

        return LLMClientResponse(
            provider=self.provider,
            content=content,
            response_time=response_time,
            cost=(
                (
                    (len(usage.input_tokens) / 1_000_000)  # type: ignore
                    * MODEL_REGISTRY[self.model]["cost_per_1M_input_tokens"]
                )
                + (
                    (len(usage.output_tokens) / 1_000_000)  # type: ignore
                    * MODEL_REGISTRY[self.model]["cost_per_1M_output_tokens"]
                )
            ),
        )
