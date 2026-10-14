"""What happens when the user picks an operation: gather input -> preview -> confirm -> run."""
from __future__ import annotations

from datetime import datetime

import questionary

from .config import BACKUP_DIR
from .models import Device
from .runner import run_all
from .tasks import Task, UnsupportedVendor
from .ui import ask, console, panel, print_results
from .vendors import get_vendor


def do_config(devs: list[Device], task: Task) -> None:
    vendors = {d["vendor"] for d in devs}
    params = task.ask_params(vendors)

    plans: dict[str, list[str]] = {}
    for v in sorted(vendors):
        try:
            plans[v] = task.build(v, params)
        except UnsupportedVendor as e:
            console.print(f"[yellow]Skipping {v}: {e}[/]")

    targets = [d for d in devs if d["vendor"] in plans]
    if not targets:
        return

    for v, lines in plans.items():
        panel("\n".join(lines), f"Preview - {v}")
    if not ask(questionary.confirm(f"Apply to {len(targets)} device(s)?", default=False)):
        return
    save = ask(questionary.confirm("Save config after applying?", default=True))
    print_results(run_all(targets, "config", lambda d: plans[d["vendor"]], save))


def do_show(devs: list[Device]) -> None:
    cmd = ask(questionary.text("Show command (same on all selected devices):"))
    print_results(run_all(devs, "show", lambda d: cmd))


def do_backup(devs: list[Device]) -> None:
    results = run_all(devs, "show", lambda d: get_vendor(d["vendor"]).show_run)
    for r in results:
        if r.ok:
            f = BACKUP_DIR / f"{r.name}_{datetime.now():%Y%m%d_%H%M%S}.txt"
            f.write_text(r.output, encoding="utf-8")
            console.print(f"[green]✔ {r.name}[/] -> {f}")
        else:
            console.print(f"[red]✘ {r.name}[/]: {r.output}")
