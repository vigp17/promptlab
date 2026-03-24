"""Load and validate YAML test files."""

import re
from pathlib import Path
from typing import Any

import yaml


def load_test_files(files: list[Path]) -> list[dict]:
    """Load and validate test suites from YAML files."""
    suites = []
    for file in files:
        suite = _load_single_file(file)
        suites.append(suite)
    return suites


def _load_single_file(file: Path) -> dict:
    """Load a single YAML test file."""
    with open(file) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"{file}: Expected a YAML mapping at the top level")

    # Required fields
    if "prompt" not in raw:
        raise ValueError(f"{file}: Missing required 'prompt' field")
    if "tests" not in raw:
        raise ValueError(f"{file}: Missing required 'tests' field")

    prompt_template = raw["prompt"]
    model = raw.get("model", "claude-sonnet-4-20250514")
    system = raw.get("system", None)
    temperature = raw.get("temperature", 0)
    max_tokens = raw.get("max_tokens", 1024)

    tests = []
    for i, test_raw in enumerate(raw["tests"]):
        test = _validate_test(test_raw, file, i)
        tests.append(test)

    return {
        "file": str(file),
        "prompt_template": prompt_template,
        "model": model,
        "system": system,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "tests": tests,
    }


def _validate_test(test: dict, file: Path, index: int) -> dict:
    """Validate a single test case."""
    if not isinstance(test, dict):
        raise ValueError(f"{file}: Test {index} must be a mapping")

    name = test.get("name", f"test_{index}")
    variables = test.get("vars", {})
    assertions = test.get("assert", [])

    if not assertions:
        raise ValueError(f"{file}: Test '{name}' has no assertions")

    validated_assertions = []
    for a in assertions:
        if "type" not in a:
            raise ValueError(f"{file}: Test '{name}' has assertion without 'type'")
        validated_assertions.append({
            "type": a["type"],
            "value": a.get("value"),
        })

    return {
        "name": name,
        "vars": variables,
        "assert": validated_assertions,
    }


def render_prompt(template: str, variables: dict) -> str:
    """Render a prompt template with variables using {{ var }} syntax."""
    result = template
    for key, value in variables.items():
        result = result.replace("{{ " + key + " }}", str(value))
        result = result.replace("{{" + key + "}}", str(value))
    return result
