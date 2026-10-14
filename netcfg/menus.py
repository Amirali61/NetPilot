"""All interactive menus (main menu + per-device action menu)."""
from __future__ import annotations

import questionary
from rich.panel import Panel

from .actions import do_backup, do_config, do_show
from .inventory import (device_form, load_devices, manage_devices, show_devices_table,
                        upsert_device)
from .live_console import live_console_session
from .models import Device
from .tasks import TASKS, TASKS_BY_LABEL
from .ui import Cancel, ask, console

SHOW = "Run a show command"
BACKUP = "Backup running-config"
BACK = "← Back"


def action_menu(devs: list[Device]) -> None:
    names = ", ".join(d["name"] for d in devs)
    while True:
        console.rule(f"[bold]{names}")
        choice = ask(questionary.select(
            "What do you want to do?",
            choices=[t.label for t in TASKS] + [SHOW, BACKUP, BACK]))
        try:
            if choice == BACK:
                return
            elif choice == SHOW:
                do_show(devs)
            elif choice == BACKUP:
                do_backup(devs)
            else:
                do_config(devs, TASKS_BY_LABEL[choice])
        except Cancel:
            console.print("[yellow]Cancelled.[/]")


def _configure_new() -> None:
    dev = device_form()
    if ask(questionary.confirm("Save this device for later?", default=True)):
        upsert_device(dev)
    action_menu([dev])


def _configure_saved() -> None:
    devs = load_devices()
    if not devs:
        console.print("[yellow]No saved devices yet.[/]")
        return
    show_devices_table(devs)
    selected = ask(questionary.checkbox("Select one or more devices (Space to select):",
                                        choices=[d["name"] for d in devs]))
    if selected:
        action_menu([d for d in devs if d["name"] in selected])


def main_menu() -> None:
    console.print(Panel("[bold]NetCfg[/] - Network device configuration tool", border_style="blue"))
    while True:
        try:
            choice = ask(questionary.select("Main menu:", choices=[
                "Configure a NEW device",
                "Configure SAVED device(s)",
                "Live console (terminal + auto config)",
                "Manage saved devices",
                "Exit"]))
            if choice == "Exit":
                return
            elif choice == "Configure a NEW device":
                _configure_new()
            elif choice == "Configure SAVED device(s)":
                _configure_saved()
            elif choice == "Live console (terminal + auto config)":
                live_console_session(action_menu)
            else:
                manage_devices()
        except Cancel:
            continue
        except KeyboardInterrupt:
            console.print("\n[yellow]Bye.[/]")
            return
