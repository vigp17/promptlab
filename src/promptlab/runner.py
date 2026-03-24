"""Test runner: executes test suites and collects results."""

import time

from promptlab.assertions import check_assertion
from promptlab.loader import render_prompt
from promptlab.providers import call_llm


def run_all_tests(suites: list[dict], verbose: bool = False) -> list[dict]:
    """Run all test suites and return results."""
    results = []

    for suite in suites:
        suite_results = _run_suite(suite, verbose=verbose)
        results.extend(suite_results)

    return results


def _run_suite(suite: dict, verbose: bool = False) -> list[dict]:
    """Run a single test suite."""
    results = []
    file_name = suite["file"]
    # Use the filename without extension as the suite name
    suite_name = file_name.rsplit("/", 1)[-1].rsplit(".", 1)[0]

    for test in suite["tests"]:
        result = _run_single_test(suite, test, suite_name, verbose=verbose)
        results.append(result)

    return results


def _run_single_test(suite: dict, test: dict, suite_name: str, verbose: bool = False) -> dict:
    """Run a single test case."""
    test_name = test["name"]
    start = time.time()

    # Render the prompt with variables
    prompt = render_prompt(suite["prompt_template"], test["vars"])

    # Call the LLM
    try:
        response = call_llm(
            prompt=prompt,
            model=suite["model"],
            system=suite.get("system"),
            temperature=suite.get("temperature", 0),
            max_tokens=suite.get("max_tokens", 1024),
        )
        output = response["text"]
        error = None
    except Exception as e:
        output = ""
        error = str(e)
        response = {"input_tokens": 0, "output_tokens": 0, "model": suite["model"]}

    elapsed = time.time() - start

    # Check assertions
    assertion_results = []
    all_passed = error is None

    if error is None:
        for assertion in test["assert"]:
            result = check_assertion(assertion, output, suite["model"])
            assertion_results.append(result)
            if not result["passed"]:
                all_passed = False
    else:
        all_passed = False

    return {
        "suite": suite_name,
        "name": test_name,
        "passed": all_passed,
        "elapsed": round(elapsed, 2),
        "output": output,
        "error": error,
        "assertions": assertion_results,
        "model": response.get("model", suite["model"]),
        "input_tokens": response.get("input_tokens", 0),
        "output_tokens": response.get("output_tokens", 0),
    }
