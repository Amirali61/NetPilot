"""
Per-vendor constants: console behaviour, show/backup commands, safe-mode (reload guard)
commands and Day-0 (factory state) dialog rules.

To add a vendor: add a Vendor(...) to _ALL below, then add a builder for it in
the tasks you want to support (see tasks/*.py).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    """Day-0 dialog rule: if the console output ends with `pattern`, answer with `reply`."""
    pattern: str            # regex, searched case-insensitively in the tail of the output
    reply: str              # may use {factory_user} {factory_password} {admin_password}
    enter: bool = True      # press Enter after the reply


@dataclass(frozen=True)
class Vendor:
    key: str                              # netmiko device_type
    label: str                            # shown in menus
    # --- console (serial) ---
    console_pre: tuple[str, ...] = ()     # commands to enter config mode
    console_post: tuple[str, ...] = ()    # commands to leave config mode
    save_cmds: tuple[str, ...] = ()       # commands to persist config
    no_paging: tuple[str, ...] = ()       # disable --More--
    prompt_re: str = ""                   # regex of a normal CLI prompt (whole last line)
    needs_enable: bool = False            # ask for an enable secret?
    # --- show / backup ---
    show_run: str = ""
    show_startup: str = ""                # used to check "is running-config saved?"
    verify_cmd: str = ""                  # harmless command to prove the device still answers
    # --- safe mode: reload guard (auto-revert timer). Empty guard_start = unsupported ---
    guard_start: str = ""                 # e.g. "reload in {minutes}"
    guard_cancel: str = ""                # e.g. "reload cancel"
    reload_now: str = ""                  # immediate revert = reload (running-config is NOT saved)
    guard_answers: tuple[tuple[str, str], ...] = ()   # (text in output, reply) for the prompts
    # --- Day-0 ---
    factory_user: str = ""
    factory_password: str = ""
    day0_rules: tuple[Rule, ...] = ()

    @property
    def supports_guard(self) -> bool:
        return bool(self.guard_start and self.guard_cancel)


_MORE = Rule(r"--\s*more\s*--", " ", enter=False)

_ALL = (
    Vendor(
        key="cisco_ios", label="Cisco IOS / IOS-XE",
        console_pre=("configure terminal",), console_post=("end",),
        save_cmds=("write memory",), no_paging=("terminal length 0",),
        prompt_re=r"^[\w.\-]+(\([\w\-/. ]+\))?[>#]$", needs_enable=True,
        show_run="show running-config", show_startup="show startup-config",
        verify_cmd="show clock",
        guard_start="reload in {minutes}", guard_cancel="reload cancel", reload_now="reload",
        guard_answers=(("[yes/no]", "no"), ("[confirm]", "")),
        day0_rules=(
            Rule(r"(initial configuration dialog|basic management setup)", "no"),
            Rule(r"terminate autoinstall", "yes"),
            Rule(r"press return to get started", ""),
            _MORE,
            Rule(r"(username|login):\s*$", "{factory_user}"),
            Rule(r"password:\s*$", "{factory_password}"),
        ),
    ),
    Vendor(
        key="huawei", label="Huawei VRP",
        console_pre=("system-view",), console_post=("return",),
        save_cmds=("save", "y"), no_paging=("screen-length 0 temporary",),
        prompt_re=r"^(<[\w\-.~+]+>|\[[\w\-.~+]+\])$",
        show_run="display current-configuration", verify_cmd="display clock",
        factory_user="admin", factory_password="admin@huawei.com",
        # best effort: forced first-login password change is NOT automated -> manual fallback
        day0_rules=(
            Rule(r"stop auto-?config\?\s*\[y/n\]", "y"),
            _MORE,
            Rule(r"username:\s*$", "{factory_user}"),
            Rule(r"password:\s*$", "{factory_password}"),
        ),
    ),
    Vendor(
        key="mikrotik_routeros", label="MikroTik RouterOS",
        prompt_re=r"^\[[\w\-.@]+\]\s*>$",
        show_run="/export", verify_cmd="/system clock print",
        factory_user="admin", factory_password="",
        day0_rules=(
            Rule(r"see the software license\?", "n"),
            Rule(r"repeat new password>\s*$", "{admin_password}"),
            Rule(r"new password>\s*$", "{admin_password}"),
            Rule(r"login:\s*$", "{factory_user}"),
            Rule(r"password:\s*$", "{factory_password}"),
        ),
    ),
)

VENDORS: dict[str, Vendor] = {v.key: v for v in _ALL}
LABEL_TO_KEY: dict[str, str] = {v.label: v.key for v in _ALL}


def get_vendor(key: str) -> Vendor:
    try:
        return VENDORS[key]
    except KeyError:
        raise ValueError(f"Unknown vendor '{key}'. Known: {', '.join(VENDORS)}") from None
