"""Assertion types for evaluating LLM outputs."""

import re

from promptlab.providers import call_llm


def check_assertion(assertion: dict, output: str, model: str) -> dict:
    """Check a single assertion against an LLM output.

    Returns:
        dict with keys: passed (bool), type, expected, got, message
    """
    atype = assertion["type"]
    value = assertion.get("value")

    checkers = {
        "contains": _check_contains,
        "not_contains": _check_not_contains,
        "starts_with": _check_starts_with,
        "regex": _check_regex,
        "equals": _check_equals,
        "max_tokens": _check_max_tokens,
        "min_length": _check_min_length,
        "max_length": _check_max_length,
        "llm_judge": _check_llm_judge,
    }

    checker = checkers.get(atype)
    if checker is None:
        return {
            "passed": False,
            "type": atype,
            "expected": value,
            "got": None,
            "message": f"Unknown assertion type: {atype}",
        }

    if atype == "llm_judge":
        return checker(output, value, model)
    return checker(output, value)


def _check_contains(output: str, value: str) -> dict:
    passed = value.lower() in output.lower()
    return {
        "passed": passed,
        "type": "contains",
        "expected": f'contains "{value}"',
        "got": output[:200] + "..." if len(output) > 200 else output,
        "message": "" if passed else f'Output does not contain "{value}"',
    }


def _check_not_contains(output: str, value: str) -> dict:
    passed = value.lower() not in output.lower()
    return {
        "passed": passed,
        "type": "not_contains",
        "expected": f'does not contain "{value}"',
        "got": output[:200] + "..." if len(output) > 200 else output,
        "message": "" if passed else f'Output contains "{value}" (should not)',
    }


def _check_starts_with(output: str, value: str) -> dict:
    passed = output.strip().lower().startswith(value.lower())
    return {
        "passed": passed,
        "type": "starts_with",
        "expected": f'starts with "{value}"',
        "got": output[:100],
        "message": "" if passed else f'Output does not start with "{value}"',
    }


def _check_regex(output: str, value: str) -> dict:
    try:
        passed = bool(re.search(value, output))
    except re.error as e:
        return {
            "passed": False,
            "type": "regex",
            "expected": f"matches /{value}/",
            "got": None,
            "message": f"Invalid regex: {e}",
        }
    return {
        "passed": passed,
        "type": "regex",
        "expected": f"matches /{value}/",
        "got": output[:200] + "..." if len(output) > 200 else output,
        "message": "" if passed else f"Output does not match regex /{value}/",
    }


def _check_equals(output: str, value: str) -> dict:
    passed = output.strip() == value.strip()
    return {
        "passed": passed,
        "type": "equals",
        "expected": value,
        "got": output.strip(),
        "message": "" if passed else "Output does not exactly match expected value",
    }


def _check_max_tokens(output: str, value: int) -> dict:
    # Rough token estimate: ~4 chars per token
    token_estimate = len(output.split())
    passed = token_estimate <= value
    return {
        "passed": passed,
        "type": "max_tokens",
        "expected": f"<= {value} tokens",
        "got": f"~{token_estimate} tokens ({len(output)} chars)",
        "message": "" if passed else f"Output has ~{token_estimate} tokens, max is {value}",
    }


def _check_min_length(output: str, value: int) -> dict:
    length = len(output.strip())
    passed = length >= value
    return {
        "passed": passed,
        "type": "min_length",
        "expected": f">= {value} chars",
        "got": f"{length} chars",
        "message": "" if passed else f"Output is {length} chars, minimum is {value}",
    }


def _check_max_length(output: str, value: int) -> dict:
    length = len(output.strip())
    passed = length <= value
    return {
        "passed": passed,
        "type": "max_length",
        "expected": f"<= {value} chars",
        "got": f"{length} chars",
        "message": "" if passed else f"Output is {length} chars, maximum is {value}",
    }


def _check_llm_judge(output: str, criteria: str, model: str) -> dict:
    """Use an LLM to judge the output quality."""
    judge_prompt = f"""You are evaluating an LLM output. Answer only YES or NO.

Criteria: {criteria}

Output to evaluate:
---
{output}
---

Does the output meet the criteria? Answer only YES or NO."""

    try:
        response = call_llm(
            prompt=judge_prompt,
            model=model,
            temperature=0,
            max_tokens=10,
        )
        answer = response["text"].strip().upper()
        passed = answer.startswith("YES")
    except Exception as e:
        return {
            "passed": False,
            "type": "llm_judge",
            "expected": criteria,
            "got": f"Judge error: {e}",
            "message": f"LLM judge failed: {e}",
        }

    return {
        "passed": passed,
        "type": "llm_judge",
        "expected": criteria,
        "got": f"Judge answered: {answer}",
        "message": "" if passed else f"LLM judge said NO to: {criteria}",
    }
