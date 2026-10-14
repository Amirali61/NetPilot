import questionary

from ..ui import ask
from .base import Task


def ask_params(vendors):
    return {"hostname": ask(questionary.text("New hostname:"))}


TASK = Task(
    label="Set hostname",
    ask_params=ask_params,
    builders={
        "cisco_ios": lambda p: [f"hostname {p['hostname']}"],
        "huawei": lambda p: [f"sysname {p['hostname']}"],
        "mikrotik_routeros": lambda p: [f"/system identity set name={p['hostname']}"],
    },
)
