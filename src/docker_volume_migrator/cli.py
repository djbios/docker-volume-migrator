"""CLI entrypoint wrapping Typer app."""

from __future__ import annotations
import typer

from .core import app as _app


app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def main() -> None:  # noqa: D401
    """Run the interactive wizard."""
    _app()


if __name__ == "__main__":  # pragma: no cover
    main()
