"""Reporter: pretty terminal output for test results."""

from rich.console import Console
from rich.table import Table

console = Console()


def print_results(results: list[dict], verbose: bool = False):
    """Print individual test results."""
    console.print()

    for result in results:
        status = "[bold green]✅ PASS[/]" if result["passed"] else "[bold red]❌ FAIL[/]"
        name = f"{result['suite']} :: {result['name']}"
        elapsed = f"({result['elapsed']}s)"

        console.print(f"  {status}  {name}  [dim]{elapsed}[/]")

        if result["error"]:
            console.print(f"         [red]Error: {result['error']}[/]")

        if not result["passed"]:
            for assertion in result["assertions"]:
                if not assertion["passed"]:
                    console.print(f"         [dim]Expected:[/] {assertion['expected']}")
                    if assertion.get("message"):
                        console.print(f"         [dim]Reason:[/]   {assertion['message']}")

        if verbose and result["output"]:
            console.print(f"         [dim]Output:[/]")
            # Indent and truncate output
            output_lines = result["output"][:500].split("\n")
            for line in output_lines:
                console.print(f"           [dim]{line}[/]")
            if len(result["output"]) > 500:
                console.print(f"           [dim]... (truncated)[/]")
            console.print()


def print_summary(results: list[dict], elapsed: float):
    """Print summary line."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    total_input = sum(r.get("input_tokens", 0) for r in results)
    total_output = sum(r.get("output_tokens", 0) for r in results)

    console.print()
    console.print("━" * 50)

    if failed == 0:
        console.print(
            f"  [bold green]Results: {passed} passed[/], "
            f"{total} total ({elapsed:.1f}s)"
        )
    else:
        console.print(
            f"  [bold red]Results: {passed} passed, {failed} failed[/], "
            f"{total} total ({elapsed:.1f}s)"
        )

    if total_input > 0 or total_output > 0:
        console.print(
            f"  [dim]Tokens: {total_input:,} input, {total_output:,} output[/]"
        )

    console.print()
