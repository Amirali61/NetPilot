# NetPilot — Network Device Configuration Tool

**NetPilot** is an interactive terminal-based tool for managing and configuring network devices. It supports connecting to devices over SSH, Telnet, or a serial console, previewing configuration commands before execution, and managing multiple devices in parallel.

## Features

- Connect through **SSH, Telnet, and Serial Console**
- Support for **Cisco IOS / IOS-XE, Huawei VRP, and MikroTik RouterOS** for features implemented by their task builders
- Manage saved devices using a local inventory
- Run operations on multiple devices in parallel
- Preview configuration commands and request confirmation before applying them
- Run custom commands to inspect device status
- Back up running configurations or equivalent device output
- Save operation logs and command output to files
- Use an interactive serial console and run automated operations over the same connection
- Send commands from a text file
- Keep connection passwords in memory while the application is running; passwords are not stored in the inventory file

## Built-in Configuration Tasks

| Task | Description |
|---|---|
| Set hostname | Configure the device hostname |
| Enable SSH | Enable SSH on supported devices |
| Create VLAN(s) | Create one or more VLANs |
| Configure access ports | Configure access ports |
| Configure trunk ports | Configure trunk ports |
| Configure management IP | Configure a management IP address |
| Custom commands | Run a custom set of commands |
| Send commands from a file | Read commands from a text file |

The exact commands depend on the device vendor. Check the task builders in `netcfg/tasks/` to see which vendors and features are supported.

## Requirements

- Python 3.10 or newer (Python 3.11 or 3.12 recommended)
- Network access to the target device for SSH/Telnet, or local access to a serial console port
- Valid login credentials and sufficient privileges on the device

## Installation

Clone the repository and enter the project directory:

```bash
git clone <REPOSITORY_URL>
cd netcfg_tool
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the Application

From the project directory, run the command:

```bash
python run.py
```

## Usage Guide

1. Select **Configure a NEW device** to define a new device, or **Configure SAVED device(s)** to choose devices from the local inventory.
2. Select the device vendor and connection method.
3. For network connections, enter the IP address or hostname and port. For serial connections, select the COM port or serial device and set the baud rate.
4. Choose an operation from the task menu.
5. Enter the required parameters and review the command preview.
6. Confirm execution only after verifying that the commands are correct.

Use **Run a show command** to inspect device status. The **Backup running-config** option saves the current configuration output in the backup directory.

### Live Console

The **Live console (terminal + auto config)** option provides an interactive serial terminal and then allows automated operations to run over the same connection.

- To exit the interactive `miniterm` terminal, use `Ctrl+]` in typical configurations.
- If the device remains in configuration mode, the application attempts to leave that mode before running automated operations.
- The console line ending is configured in `netcfg/config.py` using `CONSOLE_EOL`. The default is `CR`; change it to `CRLF` only if your device requires it.

### Run Commands from a File

With **Send commands from a file**, each line is treated as a command. Blank lines and lines starting with `#` or `!` are ignored.

## Local Data Storage

The application stores local data under `~/.netcfg/`:

| Path | Contents |
|---|---|
| `devices.json` | Device information, excluding passwords |
| `backups/` | Configuration backup files |
| `logs/` | Daily operation logs and command output |

Logs and backups may contain sensitive network information. Restrict access to this directory and review files before sharing them.

## Security and Operational Notes

- **Review the command preview carefully before confirming.** Incorrect configuration changes can interrupt connectivity or lock you out of a device.
- Test new tasks on a lab device or during a maintenance window before using them in production.
- Use an account with the minimum privileges required for the operation.
- Telnet traffic is unencrypted. Prefer SSH whenever possible.
- Treat backup files and logs as confidential information.
- Avoid running concurrent operations against the same serial port.
- Older devices may require a compatible version of Paramiko. This project specifies a `<5` constraint in `requirements.txt`:
  ```bash
  pip install "paramiko<5"
  ```
- On some Huawei devices, enabling SSH may require manually generating an RSA key. If necessary, run the appropriate command for your device model and software version first.

## Run Tests

The tests check command-generation logic and do not normally require a connection to a physical device.

```bash
pip install pytest
pytest
```

## Project Structure

```text
netcfg_tool/
├── run.py
├── requirements.txt
├── conftest.py
├── tests/
│   └── test_tasks.py
└── netcfg/
    ├── __main__.py
    ├── config.py
    ├── models.py
    ├── vendors.py
    ├── credentials.py
    ├── inventory.py
    ├── menus.py
    ├── actions.py
    ├── runner.py
    ├── live_console.py
    ├── ui.py
    ├── legacy_ssh.py
    ├── connections/
    │   ├── base.py
    │   ├── netmiko_conn.py
    │   └── serial_conn.py
    └── tasks/
        ├── base.py
        ├── common.py
        ├── hostname.py
        ├── ssh_enable.py
        ├── vlan.py
        ├── access_ports.py
        ├── trunk_ports.py
        ├── mgmt_ip.py
        ├── custom.py
        └── script_file.py
```

## Extending the Project

### Add a New Task

1. Create a new module in `netcfg/tasks/`.
2. Define the required parameters and command builders for the target vendors.
3. Create a `Task` object with a label, a parameter-collection function, and command builders.
4. Import the module in `netcfg/tasks/__init__.py` and add the task to the `TASKS` list.

Example:

```python
from ..ui import ask
from .base import Task
import questionary

def ask_params(vendors):
    return {"server": ask(questionary.text("NTP server IP:"))}

TASK = Task(
    label="Set NTP server",
    ask_params=ask_params,
    builders={
        "cisco_ios": lambda p: [f"ntp server {p['server']}"],
        "huawei": lambda p: [f"ntp-service unicast-server {p['server']}"],
        "mikrotik_routeros": lambda p: [
            f"/system ntp client set enabled=yes servers={p['server']}"
        ],
    },
)
```

To enable the new task, import the module in `netcfg/tasks/__init__.py` and add `ntp.TASK` to the `TASKS` list. Verify commands against the target device model and operating-system version before using them.

### Common Customization Points

| Goal | Location |
|---|---|
| Add or modify configuration tasks | `netcfg/tasks/` |
| Register and order tasks in the menu | `netcfg/tasks/__init__.py` |
| Define vendor-specific behavior | `netcfg/vendors.py` and task builders |
| Add a connection method | `netcfg/connections/` and relevant settings in `config.py` |
| Change parallelism, timeouts, and serial settings | `netcfg/config.py` |
| Modify device models and inventory | `netcfg/models.py` and `netcfg/inventory.py` |
| Modify menus and operations | `netcfg/menus.py` and `netcfg/actions.py` |

## Contributing

Bug reports, feature requests, and pull requests are welcome. Please include clear reproduction steps for bugs and add relevant tests when possible. Run the test suite before submitting changes.

## License

NetPilot is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See the LICENSE file for the full license text.

Commercial use, modification, and redistribution are permitted subject to the terms of the license.

