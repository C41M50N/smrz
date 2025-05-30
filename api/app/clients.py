import os
from enum import Enum

from openai import OpenAI

GEMINI_CLIENT = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


class GeminiModels(str, Enum):
    """
    Enum for Gemini model references.
    """

    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash-preview-05-20"
    GEMINI_2_5_PRO = "gemini-2.5-pro-preview-05-06"


OPENROUTER_CLIENT = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


class OpenRouterModels(str, Enum):
    """
    Enum for OpenRouter model references.
    """

    GEMMA_3_27B_IT = "google/gemma-3-27b-it"
    CLAUDE_3_5_HAIKU = "anthropic/claude-3.5-haiku"
    LLAMA_4_MAVERICK = "meta-llama/llama-4-maverick"
