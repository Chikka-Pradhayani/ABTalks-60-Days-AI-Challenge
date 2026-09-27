"""AURONIX Core AI Loop.

Implements the single most important interaction function for AURONIX:
user question -> AI processing -> useful answer.
"""

import os
from typing import Optional
from openai import (
    OpenAI,
    OpenAIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
)

DEFAULT_MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = (
    "You are AURONIX, a private company AI assistant. "
    "Your objective is to answer employee questions clearly, accurately, and concisely "
    "regarding internal company operations, policies, engineering architecture, and incident runbooks. "
    "Provide grounded, factual answers. If information is not known, state it clearly."
)


def get_openai_client() -> OpenAI:
    """Initializes and returns an OpenAI client using environment credentials.

    Raises:
        ValueError: If OPENAI_API_KEY is not set or empty.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "OPENAI_API_KEY environment variable is missing or empty. "
            "Please configure your OpenAI API key in your environment:\n"
            "  PowerShell: $env:OPENAI_API_KEY='sk-...'\n"
            "  Bash:       export OPENAI_API_KEY='sk-...'"
        )
    return OpenAI(api_key=api_key.strip())


def core_ai_loop(user_input: str, model: Optional[str] = None) -> str:
    """Executes the core AI reasoning loop for a single user query.

    Args:
        user_input: Natural language question from an employee.
        model: Optional OpenAI model identifier override.

    Returns:
        The generated answer string from the AI model.

    Raises:
        ValueError: If user_input is empty, whitespace-only, or not a string.
        PermissionError: If API credentials fail authentication.
        ConnectionError: If network connection to OpenAI fails.
        RuntimeError: If OpenAI returns empty responses or encounters API errors.
    """
    if not isinstance(user_input, str) or not user_input.strip():
        raise ValueError("User input must be a non-empty string.")

    cleaned_input = user_input.strip()
    selected_model = model or os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)

    client = get_openai_client()

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": cleaned_input},
            ],
            temperature=0.2,
            max_tokens=800,
        )

        if not response.choices:
            raise RuntimeError("OpenAI API returned an empty choices list.")

        message = response.choices[0].message
        content = message.content

        if not content:
            raise RuntimeError("OpenAI API returned empty message content.")

        return content.strip()

    except AuthenticationError as e:
        raise PermissionError(
            f"OpenAI Authentication Failed: Invalid or expired API key. Details: {e}"
        )
    except RateLimitError as e:
        raise RuntimeError(
            f"OpenAI Rate Limit Exceeded: Quota or concurrency limit hit. Details: {e}"
        )
    except APIConnectionError as e:
        raise ConnectionError(
            f"OpenAI Connection Error: Unable to reach endpoint. Details: {e}"
        )
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API Error: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error in core_ai_loop: {e}")
