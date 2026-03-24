"""LLM API providers: Claude and OpenAI."""

import os

import httpx


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def _is_anthropic_model(model: str) -> bool:
    return model.startswith("claude")


def _is_openai_model(model: str) -> bool:
    return model.startswith("gpt") or model.startswith("o1") or model.startswith("o3")


def call_llm(
    prompt: str,
    model: str,
    system: str | None = None,
    temperature: float = 0,
    max_tokens: int = 1024,
) -> dict:
    """Call an LLM and return the response.

    Returns:
        dict with keys: text, model, input_tokens, output_tokens
    """
    if _is_anthropic_model(model):
        return _call_anthropic(prompt, model, system, temperature, max_tokens)
    elif _is_openai_model(model):
        return _call_openai(prompt, model, system, temperature, max_tokens)
    else:
        raise ValueError(
            f"Unknown model: {model}. "
            "Supported prefixes: 'claude' (Anthropic), 'gpt'/'o1'/'o3' (OpenAI)"
        )


def _call_anthropic(
    prompt: str,
    model: str,
    system: str | None,
    temperature: float,
    max_tokens: int,
) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Get a key at https://console.anthropic.com/"
        )

    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    body: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    with httpx.Client(timeout=60) as client:
        resp = client.post(ANTHROPIC_API_URL, headers=headers, json=body)

    if resp.status_code != 200:
        raise RuntimeError(f"Anthropic API error ({resp.status_code}): {resp.text}")

    data = resp.json()
    text = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")

    return {
        "text": text,
        "model": data.get("model", model),
        "input_tokens": data.get("usage", {}).get("input_tokens", 0),
        "output_tokens": data.get("usage", {}).get("output_tokens", 0),
    }


def _call_openai(
    prompt: str,
    model: str,
    system: str | None,
    temperature: float,
    max_tokens: int,
) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Get a key at https://platform.openai.com/"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    with httpx.Client(timeout=60) as client:
        resp = client.post(OPENAI_API_URL, headers=headers, json=body)

    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI API error ({resp.status_code}): {resp.text}")

    data = resp.json()
    text = data["choices"][0]["message"]["content"]

    return {
        "text": text,
        "model": data.get("model", model),
        "input_tokens": data.get("usage", {}).get("prompt_tokens", 0),
        "output_tokens": data.get("usage", {}).get("completion_tokens", 0),
    }
