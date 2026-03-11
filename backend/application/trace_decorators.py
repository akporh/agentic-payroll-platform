"""
Trace Decorators.

Provides the ``trace_step`` decorator so that functions can automatically
produce ExecutionTracer step output without manual ``with tracer.step()``
blocks.

Usage
-----
    from backend.application.trace_decorators import trace_step

    @trace_step("Calculate gross pay")
    def calculate_gross(components: list[dict], *, tracer=None):
        ...

Rules
-----
* The decorated function **must** accept ``tracer`` as a keyword-only arg
  (``*, tracer=None``) so the decorator can pass it through.
* If the caller omits ``tracer`` (or passes ``tracer=None``), the function
  runs exactly as before — zero overhead, no imports required from callers.
* Business logic is never touched; the decorator is purely observational.
"""

from functools import wraps


def trace_step(step_name: str):
    """Decorator factory.  Wraps a function in ``tracer.step(step_name)``.

    Args:
        step_name: Human-readable label shown in the trace output.

    Returns:
        A decorator that wraps the target function.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = kwargs.get("tracer")

            if tracer is None:
                # No tracer in scope — run transparently, no side effects.
                return func(*args, **kwargs)

            with tracer.step(step_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator
