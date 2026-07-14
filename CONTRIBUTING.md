# Contributing

Keep the public CLI small, readable, and close to the Seabed HTTP contract.

1. Create a focused branch.
2. Install the development extras with `python -m pip install -e '.[dev]'`.
3. Run `ruff check .` and `pytest`.
4. Update the Relay or type notes when behaviour changes.
5. Never add tokens, user data, captured API responses, or local config files.

Prefer Python's standard library over another runtime dependency unless the dependency materially simplifies the public interface. Public response parsing belongs in Pydantic models; command UX belongs in Typer.
