"""
Tool Registry — defines and executes external tool calls.
Add new tools here as your system grows.
"""

import datetime
import math


REGISTRY = {}


def tool(name: str):
    """Decorator to register a tool function."""
    def decorator(fn):
        REGISTRY[name] = fn
        return fn
    return decorator


@tool("calculator")
def calculator(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


@tool("datetime")
def get_datetime(query: str = "") -> str:
    """Return current date and time."""
    now = datetime.datetime.now()
    return f"Current date/time: {now.strftime('%A, %B %d %Y at %H:%M:%S')}"


def run_tool(name: str, input_text: str) -> str:
    if name not in REGISTRY:
        return f"Tool '{name}' not found."
    return REGISTRY[name](input_text)


def list_tools() -> list:
    return list(REGISTRY.keys())