"""Saved devices: JSON storage + the forms/tables to manage them."""
from __future__ import annotations

import json

import questionary
from rich.table import Table

from .config import BAUDS, DEFAULT_PORTS, DEVICES_FILE, METHODS
from .models import Device
from .ui import ask, console, pick_serial_port
from .vendors import LABEL_TO_KEY, VENDORS


def load_devices() -> list[Device]:
    if DEVICES_FILE.exists():
        return json.loads(DEVICES_FILE.read_text())
    return []


def save_devices(devs: list[Device]) -> None:
    DEVICES_FILE.write_text(json.dumps(devs, indent=2, ensure_ascii=False))


def upsert_device(dev: Device) -> None:
    """Insert, or replace the device with the same name."""
    save_devices([d for d in load_devices() if d["name"] != dev["name"]] + [dev])


def show_devices_table(devs: list[Device]) -> None:
    t = Table(title="Saved devices")
    for col in ("#", "Name", "Vendor", "Method", "Address"):
        t.add_column(col)
    for i, d in enumerate(devs, 1):
        addr = (f"{d['serial_port']}@{d['baud']}" if d["method"] == "serial"
                else f"{d['host']}:{d['port']}")
        t.add_row(str(i), d["name"], d["vendor"], d["method"], addr)
    console.print(t)


def device_form(old: Device | None = None) -> Device:
    old = old or {}
    name = ask(questionary.text("Device name:", default=old.get("name", "")))
    default_label = VENDORS[old["vendor"]].label if old.get("vendor") in VENDORS else None
    label = ask(questionary.select("Vendor:", choices=list(LABEL_TO_KEY), default=default_label))
    method = ask(questionary.select("Connection method:", choices=list(METHODS),
                                    default=old.get("method", "ssh")))
    dev: Device = {"name": name, "vendor": LABEL_TO_KEY[label], "method": method}
    if method == "serial":
        dev["serial_port"] = pick_serial_port()
        dev["baud"] = int(ask(questionary.select("Baud rate:", choices=list(BAUDS))))
        dev["host"], dev["port"] = "", 0
    else:
        dev["host"] = ask(questionary.text("IP / hostname:", default=old.get("host", "")))
        dev["port"] = int(ask(questionary.text(
            "Port:", default=str(old.get("port", DEFAULT_PORTS[method])))))
    dev["username"] = ask(questionary.text("Username (empty if none):",
                                           default=old.get("username", "admin")))
    return dev


def manage_devices() -> None:
    while True:
        devs = load_devices()
        if not devs:
            console.print("[yellow]No saved devices.[/]")
            return
        show_devices_table(devs)
        action = ask(questionary.select("Manage:", choices=["Edit", "Delete", "Back"]))
        if action == "Back":
            return
        name = ask(questionary.select("Which device?", choices=[d["name"] for d in devs]))
        idx = next(i for i, d in enumerate(devs) if d["name"] == name)
        if action == "Delete":
            if ask(questionary.confirm(f"Delete {name}?", default=False)):
                devs.pop(idx)
        else:
            devs[idx] = device_form(devs[idx])
        save_devices(devs)
