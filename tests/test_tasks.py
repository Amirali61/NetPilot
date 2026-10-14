"""Pure-logic tests (no device, no prompts):  pytest"""
import pytest

from netcfg.tasks import TASKS, UnsupportedVendor
from netcfg.tasks.access_ports import TASK as access
from netcfg.tasks.common import expand_vlans, mask_to_prefix, split_list
from netcfg.tasks.custom import TASK as custom
from netcfg.tasks.hostname import TASK as hostname
from netcfg.tasks.mgmt_ip import TASK as mgmt
from netcfg.tasks.vlan import TASK as vlan


def test_expand_vlans():
    assert expand_vlans("10, 20,30-32") == [10, 20, 30, 31, 32]
    assert expand_vlans("5,5") == [5]


def test_split_list_and_prefix():
    assert split_list("Gi0/1, Gi0/2 ,") == ["Gi0/1", "Gi0/2"]
    assert mask_to_prefix("255.255.255.0") == 24


def test_hostname_per_vendor():
    p = {"hostname": "SW1"}
    assert hostname.build("cisco_ios", p) == ["hostname SW1"]
    assert hostname.build("huawei", p) == ["sysname SW1"]
    assert hostname.build("mikrotik_routeros", p) == ["/system identity set name=SW1"]


def test_vlan_cisco_and_huawei():
    p = {"ids": [10, 20], "name": ""}
    assert vlan.build("cisco_ios", p) == ["vlan 10", "vlan 20"]
    assert vlan.build("huawei", p) == ["vlan batch 10 20"]


def test_access_huawei():
    p = {"ports": ["Ge0/0/1"], "vlan": 10}
    assert access.build("huawei", p) == [
        "interface Ge0/0/1", "port link-type access", "port default vlan 10", "quit"]


def test_mgmt_mikrotik_uses_prefix():
    p = {"vlan": 1, "ip": "10.0.0.2", "mask": "255.255.255.0", "gw": "10.0.0.1", "bridge": "bridge"}
    assert mgmt.build("mikrotik_routeros", p)[0] == "/ip address add address=10.0.0.2/24 interface=bridge"


def test_unsupported_vendor_raises():
    with pytest.raises(UnsupportedVendor):
        vlan.build("juniper_junos", {"ids": [10], "name": ""})


def test_custom_works_for_any_vendor():
    assert custom.build("juniper_junos", {"lines": ["a", "b"]}) == ["a", "b"]


def test_labels_unique():
    labels = [t.label for t in TASKS]
    assert len(labels) == len(set(labels))


# ---- serial console helpers (no hardware: __init__ is bypassed) -------------
def _serial_conn(vendor_key):
    from netcfg.connections.serial_conn import SerialConnection
    from netcfg.vendors import get_vendor
    c = object.__new__(SerialConnection)
    c.vendor = get_vendor(vendor_key)
    c.sent = []
    c._run = lambda lines, delay=0: c.sent.extend(lines)
    return c


def test_serial_leaves_cisco_config_mode():
    c = _serial_conn("cisco_ios")
    c._leave_config_mode("Switch(config-if)#")
    assert c.sent == ["end"]


def test_serial_does_not_touch_privileged_prompt():
    c = _serial_conn("cisco_ios")
    c._leave_config_mode("Switch#")
    assert c.sent == []


def test_serial_leaves_huawei_system_view():
    c = _serial_conn("huawei")
    c._leave_config_mode("[Huawei-GigabitEthernet0/0/1]")
    assert c.sent == ["return"]
    c.sent.clear()
    c._leave_config_mode("<Huawei>")
    assert c.sent == []
