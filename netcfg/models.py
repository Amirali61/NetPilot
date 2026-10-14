"""Shared data shapes (no logic)."""
from __future__ import annotations

from typing import NamedTuple, TypedDict


class Device(TypedDict, total=False):
    """One entry of ~/.netcfg/devices.json. Passwords are NEVER stored."""
    name: str
    vendor: str        # key in vendors.VENDORS (== netmiko device_type)
    method: str        # "ssh" | "telnet" | "serial"
    host: str          # ssh/telnet only
    port: int          # ssh/telnet only
    serial_port: str   # serial only, e.g. COM3 or /dev/ttyUSB0
    baud: int          # serial only
    username: str


class Result(NamedTuple):
    """Outcome of running something on one device."""
    name: str
    ok: bool
    output: str
