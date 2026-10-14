import questionary

from ..ui import ask
from .base import Task
from .common import ask_bridge, split_list


def ask_params(vendors):
    p = {"ports": split_list(ask(questionary.text("Interfaces (comma separated, e.g. Gi0/1,Gi0/2):"))),
         "vlan": int(ask(questionary.text("Access VLAN ID:")))}
    return ask_bridge(vendors, p)


def cisco(p):
    return [f"interface range {', '.join(p['ports'])}", "switchport mode access",
            f"switchport access vlan {p['vlan']}", "spanning-tree portfast"]


def huawei(p):
    out = []
    for i in p["ports"]:
        out += [f"interface {i}", "port link-type access",
                f"port default vlan {p['vlan']}", "quit"]
    return out


def mikrotik(p):
    return [f"/interface bridge port set [find interface={i}] pvid={p['vlan']}"
            for i in p["ports"]]


TASK = Task(
    label="Assign access ports to VLAN",
    ask_params=ask_params,
    builders={"cisco_ios": cisco, "huawei": huawei, "mikrotik_routeros": mikrotik},
)
