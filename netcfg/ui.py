"""Everything that talks to the terminal: prompts, panels, result printing."""
from __future__ import annotations

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from serial.tools import list_ports

from .models import Result

console = Console()


class Cancel(Exception):
    """Raised when the user cancels a prompt (Ctrl+C / Esc). Menus catch it and go back."""


def ask(question):
    """Run a questionary question; turn 'cancelled' (None) into Cancel."""
    answer = question.ask()
    if answer is None:
        raise Cancel
    return answer


def panel(body: str, title: str, style: str = "cyan") -> None:
    # Text() so device output containing [brackets] is never parsed as rich markup
    console.print(Panel(Text(body), title=title, border_style=style))


def diff_panel(diff: str, title: str) -> None:
    """Colored unified diff: green = added, red = removed."""
    body = Text()
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            style = "green"
        elif line.startswith("-") and not line.startswith("---"):
            style = "red"
        elif line.startswith("@@"):
            style = "dim"
        else:
            style = None
        body.append(line + "\n", style=style)
    console.print(Panel(body, title=title, border_style="cyan"))


def print_results(results: list[Result]) -> None:
    for r in results:
        panel(r.output.strip() or "(no output)",
              f"{'✔' if r.ok else '✘'} {r.name}",
              "green" if r.ok else "red")
    ok = sum(1 for r in results if r.ok)
    console.print(f"[bold]Done: {ok} OK, {len(results) - ok} failed.[/]")


def pick_serial_port() -> str:
    ports = [p.device for p in list_ports.comports()]
    if ports:
        choice = ask(questionary.select("Serial port:", choices=ports + ["(enter manually)"]))
        if choice != "(enter manually)":
            return choice
    return ask(questionary.text("Serial port (e.g. /dev/ttyUSB0 or COM3):"))
