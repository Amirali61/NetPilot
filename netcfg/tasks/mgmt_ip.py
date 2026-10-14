import questionary

from ..ui import ask
from .base import Task
from .common import ask_bridge, mask_to_prefix


def ask_params(vendors):
    p = {"vlan": int(ask(questionary.text("Management VLAN ID:", default="1"))),
         "ip": ask(questionary.text("IP address:")),
         "mask": ask(questionary.text("Subnet mask:", default="255.255.255.0")),
         "gw": ask(questionary.text("Default gateway (optional):"))}
    return ask_bridge(vendors, p)


def cisco(p):
    out = [f"interface vlan {p['vlan']}", f"ip address {p['ip']} {p['mask']}", "no shutdown"]
    if p["gw"]:
        out.append(f"ip default-gateway {p['gw']}")
    return out


def huawei(p):
    out = [f"interface Vlanif{p['vlan']}", f"ip address {p['ip']} {p['mask']}", "quit"]
    if p["gw"]:
        out.append(f"ip route-static 0.0.0.0 0.0.0.0 {p['gw']}")
    return out


def mikrotik(p):
    out = [f"/ip address add address={p['ip']}/{mask_to_prefix(p['mask'])} interface={p['bridge']}"]
    if p["gw"]:
        out.append(f"/ip route add gateway={p['gw']}")
    return out


TASK = Task(
    label="Management IP / default gateway",
    ask_params=ask_params,
    builders={"cisco_ios": cisco, "huawei": huawei, "mikrotik_routeros": mikrotik},
)
