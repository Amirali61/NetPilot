"""Helpers shared by several tasks."""
from __future__ import annotations

import ipaddress

import questionary

from ..ui import ask


def expand_vlans(text: str) -> list[int]:
    """'10,20,30-32' -> [10, 20, 30, 31, 32]"""
    ids: list[int] = []
    for part in text.replace(" ", "").split(","):
        if "-" in part:
            a, b = part.split("-")
            ids += range(int(a), int(b) + 1)
        elif part:
            ids.append(int(part))
    return sorted(set(ids))


def split_list(text: str) -> list[str]:
    """'Gi0/1, Gi0/2' -> ['Gi0/1', 'Gi0/2']"""
    return [i.strip() for i in text.split(",") if i.strip()]


def mask_to_prefix(mask: str) -> int:
    return ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen


def ask_bridge(vendors: set[str], params: dict) -> dict:
    """MikroTik VLANs live on a bridge; only ask when a MikroTik is selected."""
    if "mikrotik_routeros" in vendors:
        params["bridge"] = ask(questionary.text("MikroTik bridge name:", default="bridge"))
    return params
