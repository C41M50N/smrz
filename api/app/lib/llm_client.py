from enum import StrEnum
import os
import time

import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import Type, TypedDict


class Models(StrEnum):
    # Google Gemini Models
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_FLASH_LITE_PREVIEW = "gemini-2.5-flash-lite-preview-06-17"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    # OpenAI Models
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_1_NANO_2025_04_14 = "gpt-4.1-nano-2025-04-14"
    GPT_4_1_MINI_2025_04_14 = "gpt-4.1-mini-2025-04-14"
    # OpenRouter Models
    OR_LLAMA_4_MAVERICK = "meta-llama/llama-4-maverick"
    OR_LLAMA_3_3_70B_INSTRUCT = "meta-llama/llama-3.3-70b-instruct"
    OR_GPT_4O_MINI = "openai/gpt-4o-mini"
    OR_GPT_4_1_MINI = "openai/gpt-4.1-mini"
    OR_KIMI_K2 = "moonshotai/kimi-k2"


class ModelInfo(TypedDict):
    name: str
    provider: str
    cost_per_1M_input_tokens: int
    cost_per_1M_output_tokens: int


MODEL_REGISTRY: dict[Models, ModelInfo] = {
    # Google Gemini Models
    Models.GEMINI_2_5_PRO: {
        "name": "Gemini 2.5 Pro",
        "provider": "Google",
        "cost_per_1M_input_tokens": 20,  # 0.20 USD
        "cost_per_1M_output_tokens": 80,  # 0.80 USD
    },
    Models.GEMINI_2_5_FLASH: {
        "name": "Gemini 2.5 Flash",
        "provider": "Google",
        "cost_per_1M_input_tokens": 10,  # 0.10 USD
        "cost_per_1M_output_tokens": 40,  # 0.40 USD
    },
    Models.GEMINI_2_5_FLASH_LITE_PREVIEW: {
        "name": "Gemini 2.5 Flash Lite Preview",
        "provider": "Google",
        "cost_per_1M_input_tokens": 5,  # 0.05 USD
        "cost_per_1M_output_tokens": 20,  # 0.20 USD
    },
    Models.GEMINI_2_0_FLASH: {
        "name": "Gemini 2.0 Flash",
        "provider": "Google",
        "cost_per_1M_input_tokens": 5,  # 0.05 USD
        "cost_per_1M_output_tokens": 20,  # 0.20 USD
    },
    # OpenAI Models
    Models.GPT_4O_MINI: {
        "name": "GPT-4o Mini",
        "provider": "OpenAI",
        "cost_per_1M_input_tokens": 15,  # 0.15 USD
        "cost_per_1M_output_tokens": 60,  # 0.60 USD
    },
    Models.GPT_4_1_NANO_2025_04_14: {
        "name": "GPT-4.1 Nano",
        "provider": "OpenAI",
        "cost_per_1M_input_tokens": 10,  # 0.10 USD
        "cost_per_1M_output_tokens": 40,  # 0.40 USD
    },
    Models.GPT_4_1_MINI_2025_04_14: {
        "name": "GPT-4.1 Mini",
        "provider": "OpenAI",
        "cost_per_1M_input_tokens": 40,  # 0.40 USD
        "cost_per_1M_output_tokens": 160,  # 1.60 USD
    },
    # OpenRouter Models
    Models.OR_LLAMA_4_MAVERICK: {
        "name": "Llama 4 Maverick",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 15,  # 0.15 USD
        "cost_per_1M_output_tokens": 60,  # 0.60 USD
    },
    Models.OR_LLAMA_3_3_70B_INSTRUCT: {
        "name": "Llama 3.3 70B Instruct",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 5,  # 0.05 USD
        "cost_per_1M_output_tokens": 25,  # 0.25 USD
    },
    Models.OR_GPT_4O_MINI: {
        "name": "GPT-4o Mini",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 15,  # 0.15 USD
        "cost_per_1M_output_tokens": 60,  # 0.60 USD
    },
    Models.OR_GPT_4_1_MINI: {
        "name": "GPT-4.1 Mini",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 40,  # 0.40 USD
        "cost_per_1M_output_tokens": 160,  # 1.60 USD
    },
    Models.OR_KIMI_K2: {
        "name": "Kimi K2",
        "provider": "OpenRouter",
        "cost_per_1M_input_tokens": 14,  # 0.14 USD
        "cost_per_1M_output_tokens": 249,  # 2.49 USD
    },
}

# For the models with "Google" as the provider, we use the GEMINI_CLIENT.
GEMINI_CLIENT = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# For the models with "OpenAI" as the provider, we use the OPENAI_CLIENT.
OPENAI_CLIENT = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1",
)

# For the models with "OpenRouter" as the provider, we use the OPENROUTER_CLIENT.
OPENROUTER_CLIENT = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


class LLMClientResponse[T = str](BaseModel):
    content: T
    response_time: float
    provider: str
    cost: float


class LLMClient:
    def __init__(self, model: Models, system_prompt: str, log_key: str | None = None):
        self.model = model
        self.system_prompt = system_prompt
        self.provider = self._get_provider()
        self.client = self._get_client()
        self.instructor_client = instructor.from_openai(self.client)
        self.log_key = log_key

    def _get_provider(self):
        try:
            return MODEL_REGISTRY[self.model]["provider"]
        except KeyError:
            raise ValueError(f"Unknown model: {self.model}")

    def _get_client(self):
        provider = self.provider

        if provider == "Google":
            return GEMINI_CLIENT
        elif provider == "OpenAI":
            return OPENAI_CLIENT
        elif provider == "OpenRouter":
            return OPENROUTER_CLIENT
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate_response(
        self, user_prompt: str, temp: float = 0.7
    ) -> LLMClientResponse:
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
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

        cost = (
            (usage.prompt_tokens / 1_000_000)
            * MODEL_REGISTRY[self.model]["cost_per_1M_input_tokens"]
        ) + (
            (usage.completion_tokens / 1_000_000)
            * MODEL_REGISTRY[self.model]["cost_per_1M_output_tokens"]
        )

        if self.log_key:
            print(
                f"[LLMClient] [{self.log_key}]: Took {response_time:.2f}s to generate response with {self.model} ({self.provider}) - {usage.prompt_tokens} input tokens, {usage.completion_tokens} output tokens costing ~${cost / 100:.4f} USD"
            )

        return LLMClientResponse(
            content=content,
            response_time=response_time,
            provider=self.provider,
            cost=cost,
        )

    def generate_structured_response(
        self, OutputSchema: Type[BaseModel], user_prompt: str, temp: float = 0.7
    ) -> LLMClientResponse[BaseModel]:
        if self.provider != "OpenAI":
            raise ValueError(
                "Structured responses are only supported for OpenAI models."
            )

        start_time = time.time()

        try:
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temp,
                text_format=OutputSchema,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {str(e)}")

        response_time = time.time() - start_time

        content = response.output_parsed
        if not content:
            raise RuntimeError("Failed to generate response")

        usage = response.usage
        if not usage:
            raise RuntimeError("Response usage information is missing")

        cost = (
            (usage.input_tokens / 1_000_000)
            * MODEL_REGISTRY[self.model]["cost_per_1M_input_tokens"]
        ) + (
            (usage.output_tokens / 1_000_000)
            * MODEL_REGISTRY[self.model]["cost_per_1M_output_tokens"]
        )

        if self.log_key:
            print(
                f"[LLMClient] [{self.log_key}]: Took {response_time:.2f}s to generate structured response with {self.model} ({self.provider}) - {usage.input_tokens} input tokens, {usage.output_tokens} output tokens costing ~${cost / 100:.4f} USD"
            )

        return LLMClientResponse[BaseModel](
            content=content,
            response_time=response_time,
            provider=self.provider,
            cost=cost,
        )
