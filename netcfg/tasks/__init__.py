"""
Registry of configuration tasks. The ORDER of TASKS is the order of the menu.
To add a feature: create tasks/<name>.py exposing TASK, import it here, append to TASKS.
"""
from . import (access_ports, custom, hostname, mgmt_ip, script_file, ssh_enable,
               trunk_ports, vlan)
from .base import Task, UnsupportedVendor

TASKS: list[Task] = [
    hostname.TASK,
    ssh_enable.TASK,
    vlan.TASK,
    access_ports.TASK,
    trunk_ports.TASK,
    mgmt_ip.TASK,
    custom.TASK,
    script_file.TASK,
]
TASKS_BY_LABEL: dict[str, Task] = {t.label: t for t in TASKS}

__all__ = ["TASKS", "TASKS_BY_LABEL", "Task", "UnsupportedVendor"]
