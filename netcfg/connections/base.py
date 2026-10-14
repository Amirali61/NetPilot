"""The interface every connection type must implement."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Device
from ..vendors import get_vendor


class Connection(ABC):
    def __init__(self, dev: Device):
        self.dev = dev
        self.vendor = get_vendor(dev["vendor"])

    @abstractmethod
    def config(self, lines: list[str]) -> str:
        """Send configuration lines (enters/leaves config mode itself)."""

    @abstractmethod
    def show(self, command: str) -> str:
        """Run one read-only command and return its output."""

    @abstractmethod
    def save(self) -> str:
        """Persist the running config (write mem / save)."""

    @abstractmethod
    def close(self) -> None:
        ...

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
