#!/usr/bin/env python3
"""Example entry point for the public Seabed CLI."""

from seabed_cli.cli import main as cli_main


def main() -> None:
    """Run the installed Typer application."""
    cli_main()


if __name__ == "__main__":
    main()
