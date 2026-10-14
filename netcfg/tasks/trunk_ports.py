import questionary

from ..ui import ask
from .base import Task
from .common import ask_bridge, expand_vlans, split_list


def ask_params(vendors):
    p = {"ports": split_list(ask(questionary.text("Trunk interfaces (comma separated):"))),
         "vlans": expand_vlans(ask(questionary.text("Allowed VLANs (e.g. 10,20,30-40):")))}
    return ask_bridge(vendors, p)


def cisco(p):
    return [f"interface range {', '.join(p['ports'])}", "switchport mode trunk",
            f"switchport trunk allowed vlan add {','.join(map(str, p['vlans']))}"]


def huawei(p):
    out = []
    for i in p["ports"]:
        out += [f"interface {i}", "port link-type trunk",
                "port trunk allow-pass vlan " + " ".join(map(str, p["vlans"])), "quit"]
    return out


def mikrotik(p):
    return [f"/interface bridge vlan add bridge={p['bridge']} "
            f"tagged={','.join(p['ports'])} vlan-ids={','.join(map(str, p['vlans']))}"]


TASK = Task(
    label="Configure trunk ports",
    ask_params=ask_params,
    builders={"cisco_ios": cisco, "huawei": huawei, "mikrotik_routeros": mikrotik},
)
