"""
Execution Tracer.

Provides structured, Rich-formatted terminal output for the payroll
execution engine.  Purely observational — no business logic lives here.

Usage
-----
    tracer = ExecutionTracer(run_id)

    with tracer.step("Load employees"):
        employees = fetch_employees()
        tracer.info(f"{len(employees)} employees loaded")

    # outside calling code may also pass tracer=NULL_TRACER when tracing
    # is not needed (e.g. tests, retries).
"""

from contextlib import contextmanager
from time import time

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()


class ExecutionTracer:
    """Rich-formatted structured tracer for a single payroll execution run."""

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        console.print()
        console.print(
            Panel.fit(
                f"[bold white]Payroll Execution[/bold white]  "
                f"[bold cyan]{run_id}[/bold cyan]",
                style="bold blue",
            )
        )
        console.print()

    @contextmanager
    def step(self, name: str):
        """Context manager that wraps a top-level engine stage.

        Logs the step name on entry, measures wall-clock duration, and
        logs SUCCESS or ERROR (with the exception message) on exit.
        The exception is always re-raised so callers are unaffected.
        """
        console.log(f"[bold cyan]►[/bold cyan]  [bold]{name}[/bold]")
        start = time()
        try:
            yield
            duration = round(time() - start, 3)
            console.log(
                f"[bold green]✓  SUCCESS[/bold green]  {name}  "
                f"[dim]({duration}s)[/dim]"
            )
        except Exception as exc:
            duration = round(time() - start, 3)
            console.log(
                f"[bold red]✗  ERROR[/bold red]  {name}  "
                f"[dim]({duration}s)[/dim]  →  [red]{exc}[/red]"
            )
            raise

    def info(self, message: str) -> None:
        """Log a nested informational message inside the current step."""
        console.log(f"  [dim]│[/dim]  {message}")

    def warn(self, message: str) -> None:
        """Log a non-fatal warning (e.g. FAILED employee in isolated mode)."""
        console.log(f"  [dim]│[/dim]  [bold yellow]⚠  WARN[/bold yellow]  {message}")

    def separator(self) -> None:
        """Print a thin horizontal rule between major sections."""
        console.print(Rule(style="dim"))


class _NullTracer:
    """No-op tracer used when tracing is disabled (tests, retries)."""

    @contextmanager
    def step(self, name: str):  # noqa: ARG002
        yield

    def info(self, message: str) -> None:  # noqa: ARG002
        pass

    def warn(self, message: str) -> None:  # noqa: ARG002
        pass

    def separator(self) -> None:
        pass


# Singleton sentinel — import and use instead of None when tracing is off.
NULL_TRACER = _NullTracer()
