"""SSH and Telnet connections (via netmiko)."""
from __future__ import annotations

from netmiko import ConnectHandler

from ..config import CONNECT_TIMEOUT
from ..models import Device
from .base import Connection


class NetmikoConnection(Connection):
    def __init__(self, dev: Device, user: str, password: str, enable: str):
        super().__init__(dev)
        device_type = dev["vendor"] + ("_telnet" if dev["method"] == "telnet" else "")
        self._c = ConnectHandler(
            device_type=device_type, host=dev["host"], port=dev["port"],
            username=user, password=password, secret=enable,
            conn_timeout=CONNECT_TIMEOUT,
        )
        if enable:
            try:
                self._c.enable()
            except Exception:
                pass

    def config(self, lines):
        return self._c.send_config_set(lines)

    def show(self, command):
        return self._c.send_command(command, read_timeout=60)

    def save(self):
        if self.dev["vendor"] == "mikrotik_routeros":
            return "(RouterOS saves automatically)"
        return self._c.save_config()

    def close(self):
        self._c.disconnect()
