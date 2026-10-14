import questionary

from ..ui import ask, console
from .base import Task


def ask_params(vendors):
    console.print("[dim]Enter commands, one per line. Finish with Esc then Enter.[/]")
    text = ask(questionary.text("Commands:", multiline=True))
    return {"lines": [ln for ln in text.splitlines() if ln.strip()]}


TASK = Task(
    label="Custom commands",
    ask_params=ask_params,
    builders={"*": lambda p: p["lines"]},   # same lines for every vendor
)
