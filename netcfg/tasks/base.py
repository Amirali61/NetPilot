"""Task = one configuration feature (hostname, VLAN, SSH...)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

Params = dict
Builder = Callable[[Params], list[str]]


class UnsupportedVendor(Exception):
    """The task has no builder for this vendor."""


@dataclass
class Task:
    label: str                                # text shown in the menu
    ask_params: Callable[[set[str]], Params]  # asks the user; receives the selected vendor keys
    builders: dict[str, Builder] = field(default_factory=dict)
    # builders maps vendor key -> function(params) -> list of CLI lines.
    # Use "*" as a key for a builder that works on every vendor.

    def build(self, vendor: str, params: Params) -> list[str]:
        fn = self.builders.get(vendor) or self.builders.get("*")
        if fn is None:
            raise UnsupportedVendor(f"'{self.label}' is not implemented for '{vendor}'")
        return fn(params)
