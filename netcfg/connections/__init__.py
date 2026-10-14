"""connect(device) -> Connection. The only function the rest of the app needs."""
from __future__ import annotations

from ..credentials import get_enable, get_password
from ..models import Device
from ..vendors import get_vendor
from .base import Connection
from .netmiko_conn import NetmikoConnection
from .serial_conn import SerialConnection


def connect(dev: Device) -> Connection:
    user = dev.get("username", "")
    password = get_password(user) if user else ""
    enable = get_enable() if get_vendor(dev["vendor"]).needs_enable else ""
    cls = SerialConnection if dev["method"] == "serial" else NetmikoConnection
    return cls(dev, user, password, enable)
