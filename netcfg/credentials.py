"""Passwords are asked once and kept IN MEMORY ONLY (never written to disk)."""
import questionary

from .ui import ask

_cache: dict[str, str] = {}


def get_password(user: str) -> str:
    key = f"pwd:{user}"
    if key not in _cache:
        _cache[key] = ask(questionary.password(f"Password for '{user}':"))
    return _cache[key]


def get_enable() -> str:
    if "enable" not in _cache:
        _cache["enable"] = ask(questionary.password("Enable secret (empty if not needed):"))
    return _cache["enable"]


def remember(user: str, password: str) -> None:
    """Pre-fill the cache (used when we just configured the credentials ourselves, e.g. Day-0)."""
    _cache[f"pwd:{user}"] = password


def remember_enable(secret: str) -> None:
    _cache["enable"] = secret
