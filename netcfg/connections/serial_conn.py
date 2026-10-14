"""Console (serial) connection via pyserial. Works with any vendor."""
from __future__ import annotations

import time

import serial

from ..models import Device
from .base import Connection


class SerialConnection(Connection):
    def __init__(self, dev: Device, user: str, password: str, enable: str):
        super().__init__(dev)
        self._s = serial.Serial(dev["serial_port"], dev["baud"], timeout=0.5)
        self._s.reset_input_buffer()
        self._login(user, password, enable)

    # --- low level -------------------------------------------------------
    def _send(self, text: str) -> None:
        self._s.write((text + "\r").encode())  # CR only: CRLF would count as two Enters

    def _read(self, quiet: float = 0.6, maxwait: float = 30) -> str:
        out, last, start = b"", time.time(), time.time()
        while time.time() - start < maxwait:
            chunk = self._s.read(4096)
            if chunk:
                out += chunk
                last = time.time()
            elif time.time() - last > quiet:
                break
        return out.decode(errors="replace")

    def _run(self, lines, delay: float = 0.25) -> str:
        out = ""
        for line in lines:
            self._send(line)
            time.sleep(delay)
            out += self._read(0.4)
        return out

    def _current_prompt(self) -> str:
        self._send("")
        lines = [ln.strip() for ln in self._read(0.8).splitlines() if ln.strip()]
        return lines[-1] if lines else ""

    # --- login: wake the console, handle username/password/enable ---------
    def _login(self, user: str, password: str, enable: str) -> None:
        self._send("")
        time.sleep(0.5)
        self._send("")
        low = self._read(1.5).lower()
        if ("username" in low or "login" in low) and user:
            self._send(user)
            low = self._read(1.0).lower()
        if "password" in low and password:
            self._send(password)
            self._read(1.5)

        prompt = self._current_prompt()
        if self.vendor.needs_enable and prompt.endswith(">"):
            self._send("enable")
            if "password" in self._read(1.0).lower():
                self._send(enable)
                self._read(1.0)
            prompt = self._current_prompt()

        self._leave_config_mode(prompt)
        self._run(self.vendor.no_paging, delay=0.2)

    def _leave_config_mode(self, prompt: str) -> None:
        """The console may have been left in config mode (e.g. after the live terminal)."""
        key = self.vendor.key
        in_config = (("(config" in prompt) if key == "cisco_ios"
                     else prompt.startswith("[") if key == "huawei"
                     else False)
        if in_config:
            self._run(self.vendor.console_post, delay=0.2)

    # --- Connection interface ---------------------------------------------
    def config(self, lines):
        v = self.vendor
        return self._run(list(v.console_pre) + list(lines) + list(v.console_post))

    def show(self, command):
        self._send(command)
        return self._read(1.5, maxwait=90)

    def save(self):
        return self._run(self.vendor.save_cmds, delay=1)

    def close(self):
        self._s.close()
