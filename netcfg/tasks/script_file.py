"""Send commands from a text file (one per line; blank lines and lines starting with # or ! are skipped)."""
from pathlib import Path

import questionary

from ..ui import Cancel, ask, console
from .base import Task


def ask_params(vendors):
    path = Path(ask(questionary.path("Script file:"))).expanduser()
    if not path.is_file():
        console.print(f"[red]File not found: {path}[/]")
        raise Cancel
    lines = [ln.rstrip() for ln in path.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.lstrip().startswith(("#", "!"))]
    console.print(f"[dim]{len(lines)} command(s) loaded from {path}[/]")
    return {"lines": lines}


TASK = Task(
    label="Send commands from a file",
    ask_params=ask_params,
    builders={"*": lambda p: p["lines"]},
)
