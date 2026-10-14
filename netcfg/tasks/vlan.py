import questionary

from ..ui import ask
from .base import Task
from .common import ask_bridge, expand_vlans


def ask_params(vendors):
    ids = expand_vlans(ask(questionary.text("VLAN ID(s) (e.g. 10 or 10,20 or 100-105):")))
    p = {"ids": ids, "name": ""}
    if len(ids) == 1:
        p["name"] = ask(questionary.text("VLAN name (optional):"))
    return ask_bridge(vendors, p)


def cisco(p):
    out = []
    for i in p["ids"]:
        out.append(f"vlan {i}")
        if p["name"]:
            out.append(f"name {p['name']}")
    return out


def huawei(p):
    out = ["vlan batch " + " ".join(map(str, p["ids"]))]
    if p["name"]:
        out += [f"vlan {p['ids'][0]}", f"description {p['name']}", "quit"]
    return out


def mikrotik(p):
    comment = f" comment={p['name']}" if p["name"] else ""
    return [f"/interface bridge vlan add bridge={p['bridge']} vlan-ids={i}{comment}"
            for i in p["ids"]]


TASK = Task(
    label="Create VLAN(s)",
    ask_params=ask_params,
    builders={"cisco_ios": cisco, "huawei": huawei, "mikrotik_routeros": mikrotik},
)
