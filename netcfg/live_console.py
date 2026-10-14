"""
Console session on one serial cable: interactive terminal AND automated config.

Flow:  [Open terminal] --Ctrl+]--> session menu --> [Automated actions] / [Open terminal again]
The port is released each time, so the two modes can alternate freely.
"""
from __future__ import annotations

import subprocess
import sys
import time
from typing import Callable

import questionary

from .config import BAUDS, CONSOLE_EOL
from .inventory import upsert_device
from .models import Device
from .ui import ask, console, pick_serial_port
from .vendors import LABEL_TO_KEY

TERMINAL = "Open interactive terminal"
AUTO = "Automated config / show / backup on this console"
SAVE = "Save this console as a device"
EXIT = "← Back to main menu"


def open_terminal(port: str, baud: int) -> None:
    console.print("[dim]Interactive console. Leave with Ctrl+]  (or Ctrl+T then Q) "
                  "- you will return to the session menu.[/]")
    subprocess.call([sys.executable, "-m", "serial.tools.miniterm",
                     "--eol", CONSOLE_EOL, port, str(baud)])
    time.sleep(0.3)  # give the OS a moment to release the port before we reuse it


def live_console_session(action_menu: Callable[[list[Device]], None]) -> None:
    """action_menu is injected by menus.py (avoids a circular import)."""
    port = pick_serial_port()
    baud = int(ask(questionary.select("Baud rate:", choices=list(BAUDS))))
    vendor_label = ask(questionary.select("Device vendor (needed for automation):",
                                          choices=list(LABEL_TO_KEY)))
    user = ask(questionary.text(
        "Username for auto-login (empty if no login / already logged in):", default=""))

    dev: Device = {"name": f"console-{port}", "vendor": LABEL_TO_KEY[vendor_label],
                   "method": "serial", "serial_port": port, "baud": baud,
                   "host": "", "port": 0, "username": user}

    while True:
        choice = ask(questionary.select("Console session:", choices=[TERMINAL, AUTO, SAVE, EXIT]))
        if choice == EXIT:
            return
        elif choice == TERMINAL:
            open_terminal(port, baud)
        elif choice == AUTO:
            action_menu([dev])
        else:
            dev["name"] = ask(questionary.text("Device name:", default=dev["name"]))
            upsert_device(dev)
            console.print(f"[green]Saved '{dev['name']}'.[/]")
