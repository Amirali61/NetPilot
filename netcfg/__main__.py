"""Entry point:  python -m netcfg"""
from rich.panel import Panel

from .config import ensure_dirs
from .legacy_ssh import enable_legacy_ssh, legacy_ssh_available, paramiko_version
from .menus import main_menu
from .ui import console


def main() -> None:
    ensure_dirs()
    enable_legacy_ssh()
    if not legacy_ssh_available():
        console.print(Panel(
            f"paramiko {paramiko_version()} has no SHA-1 key exchange (removed in paramiko 5.0).\n"
            "Old devices (e.g. old Cisco IOS) will fail with 'no acceptable kex algorithm'.\n"
            "Fix:  [bold]pip install \"paramiko<5\"[/]",
            title="Warning", border_style="yellow"))
    main_menu()


if __name__ == "__main__":
    main()
