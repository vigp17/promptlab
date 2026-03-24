"""CLI entry point for promptlab."""

import json
import sys
import time
from pathlib import Path

import click

from promptlab.loader import load_test_files
from promptlab.runner import run_all_tests
from promptlab.reporter import print_results, print_summary


@click.group()
@click.version_option(version="0.1.0")
def main():
    """promptlab — Automated testing for LLM prompts."""
    pass


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show full LLM responses")
@click.option("--json-output", "--json", "json_out", is_flag=True, help="Output results as JSON")
@click.option("--dry-run", is_flag=True, help="Show tests without calling APIs")
def run(path: str, verbose: bool, json_out: bool, dry_run: bool):
    """Run prompt tests from a file or directory."""
    target = Path(path)

    # Collect test files
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = sorted(target.glob("**/*.yaml")) + sorted(target.glob("**/*.yml"))
    else:
        click.echo(f"Error: {path} is not a file or directory", err=True)
        sys.exit(1)

    if not files:
        click.echo(f"No .yaml or .yml files found in {path}", err=True)
        sys.exit(1)

    # Load test suites
    suites = load_test_files(files)

    if dry_run:
        for suite in suites:
            click.echo(f"\n📄 {suite['file']}")
            click.echo(f"   Model: {suite['model']}")
            click.echo(f"   Tests: {len(suite['tests'])}")
            for test in suite["tests"]:
                assertions = ", ".join(a["type"] for a in test["assert"])
                click.echo(f"   - {test['name']} [{assertions}]")
        return

    # Run tests
    start = time.time()
    results = run_all_tests(suites, verbose=verbose)
    elapsed = time.time() - start

    if json_out:
        output = {
            "results": results,
            "elapsed_seconds": round(elapsed, 2),
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
        }
        click.echo(json.dumps(output, indent=2))
    else:
        print_results(results, verbose=verbose)
        print_summary(results, elapsed)

    # Exit with non-zero if any test failed
    if any(not r["passed"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
