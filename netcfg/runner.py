"""Runs something on many devices in parallel + logging."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Callable, Literal, TypeVar

from .config import LOG_DIR, MAX_WORKERS
from .connections import connect
from .credentials import get_enable, get_password
from .models import Device, Result
from .ui import console
from .vendors import get_vendor

Mode = Literal["config", "show"]
T = TypeVar("T")


def log(name: str, text: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    f = LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"
    with f.open("a", encoding="utf-8") as fh:
        fh.write(f"\n===== {datetime.now():%H:%M:%S} {name} =====\n{text}\n")


def prepare_credentials(devs: list[Device]) -> None:
    """Ask for all passwords BEFORE starting threads, so prompts don't interleave."""
    for d in devs:
        if d.get("username"):
            get_password(d["username"])
        if get_vendor(d["vendor"]).needs_enable:
            get_enable()


def friendly_error(e: Exception) -> str:
    msg = str(e)
    low = msg.lower()
    if "kex" in low or "no matching" in low:
        msg += ("\n\nHint: the device only offers algorithms this client lacks.\n"
                "Old device? Make sure paramiko<5 is installed:  pip install \"paramiko<5\"")
    return msg


def run_parallel(devs: list[Device], worker: Callable[[Device], T],
                 status: str = "Running") -> list[T]:
    """Call worker(device) for every device in a thread pool; results keep the input order."""
    prepare_credentials(devs)
    with console.status(f"{status} on {len(devs)} device(s)..."):
        with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(devs))) as ex:
            futures = [ex.submit(worker, d) for d in devs]
            return [f.result() for f in futures]


def run_on_device(dev: Device, mode: Mode, payload, save: bool) -> Result:
    try:
        with connect(dev) as conn:
            if mode == "config":
                out = conn.config(payload)
                if save:
                    out += "\n" + str(conn.save())
            else:
                out = conn.show(payload)
        log(dev["name"], out)
        return Result(dev["name"], True, out)
    except Exception as e:  # noqa: BLE001 - we report every failure per device
        msg = friendly_error(e)
        log(dev["name"], f"ERROR: {msg}")
        return Result(dev["name"], False, msg)


def run_all(devs: list[Device], mode: Mode, payload_for: Callable[[Device], object],
            save: bool = False) -> list[Result]:
    """payload_for(device) -> list of config lines (mode=config) or one command (mode=show)."""
    return run_parallel(devs, lambda d: run_on_device(d, mode, payload_for(d), save))
