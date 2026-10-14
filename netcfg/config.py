"""Paths and global constants. Anything that is 'a setting' lives here."""
from pathlib import Path

DATA_DIR = Path.home() / ".netcfg"
DEVICES_FILE = DATA_DIR / "devices.json"
BACKUP_DIR = DATA_DIR / "backups"
LOG_DIR = DATA_DIR / "logs"

METHODS = ("ssh", "telnet", "serial")
BAUDS = ("9600", "115200", "38400", "19200", "57600")
DEFAULT_PORTS = {"ssh": 22, "telnet": 23}

MAX_WORKERS = 10        # how many devices are configured in parallel
CONNECT_TIMEOUT = 20    # seconds

# Line ending the live console sends on Enter. miniterm's default is CRLF, which most
# network devices see as TWO Enters. Use "CRLF" only if a device really needs it.
CONSOLE_EOL = "CR"      # one of: "CR", "LF", "CRLF"

GUARD_MINUTES = 10      # default auto-revert timer of safe mode (Cisco "reload in")
DAY0_TIMEOUT = 300      # seconds to wait for a factory-fresh device to reach its CLI
SSH_WAIT = 90           # seconds to wait for SSH to come up after Day-0 config


def ensure_dirs() -> None:
    for d in (DATA_DIR, BACKUP_DIR, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)
