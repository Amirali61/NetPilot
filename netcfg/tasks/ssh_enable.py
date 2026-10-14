import questionary

from ..ui import ask
from .base import Task


def ask_params(vendors):
    p = {
        "user": ask(questionary.text("SSH admin username:", default="admin")),
        "pwd": ask(questionary.password("SSH admin password:")),
        "no_telnet": ask(questionary.confirm("Disable telnet?", default=True)),
    }
    if "cisco_ios" in vendors:
        p["domain"] = ask(questionary.text("Domain name (needed for RSA key on Cisco):",
                                           default="local.lan"))
    return p


def cisco(p):
    return [
        f"ip domain-name {p['domain']}",
        "crypto key generate rsa modulus 2048",
        "ip ssh version 2",
        f"username {p['user']} privilege 15 secret {p['pwd']}",
        "line vty 0 15",
        "login local",
        "transport input ssh" if p["no_telnet"] else "transport input ssh telnet",
    ]


def huawei(p):
    # NOTE: RSA key creation is interactive on VRP; run "rsa local-key-pair create" once first.
    return [
        "stelnet server enable",
        "aaa",
        f"local-user {p['user']} password irreversible-cipher {p['pwd']}",
        f"local-user {p['user']} privilege level 15",
        f"local-user {p['user']} service-type ssh",
        "quit",
        "user-interface vty 0 4",
        "authentication-mode aaa",
        "protocol inbound ssh" if p["no_telnet"] else "protocol inbound all",
        "quit",
        f"ssh user {p['user']} authentication-type password",
        f"ssh user {p['user']} service-type stelnet",
    ]


def mikrotik(p):
    cmds = ["/ip service set ssh disabled=no port=22",
            f"/user add name={p['user']} password={p['pwd']} group=full"]
    if p["no_telnet"]:
        cmds.append("/ip service set telnet disabled=yes")
    return cmds


TASK = Task(
    label="Enable SSH + create admin user",
    ask_params=ask_params,
    builders={"cisco_ios": cisco, "huawei": huawei, "mikrotik_routeros": mikrotik},
)
