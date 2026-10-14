"""
Compatibility patch for OLD devices (e.g. old Cisco IOS) that only offer SHA-1 key
exchange / CBC ciphers. Legacy algorithms are appended with the LOWEST priority, so
modern devices still negotiate strong algorithms.

NOTE: paramiko 5.0 removed SHA-1 kex and ssh-rsa(SHA-1) entirely. With paramiko>=5 this
patch has nothing to enable -> keep `pip install "paramiko<5"` for old devices.
"""
import paramiko

_LEGACY_KEX = ("diffie-hellman-group-exchange-sha1",
               "diffie-hellman-group14-sha1",
               "diffie-hellman-group1-sha1")
_LEGACY_CIPHERS = ("aes128-cbc", "aes192-cbc", "aes256-cbc", "3des-cbc")


def enable_legacy_ssh() -> None:
    T = paramiko.Transport
    kex = tuple(T._preferred_kex)
    for k in _LEGACY_KEX:
        if k in getattr(T, "_kex_info", {}) and k not in kex:
            kex += (k,)
    T._preferred_kex = kex

    ciphers = tuple(T._preferred_ciphers)
    for c in _LEGACY_CIPHERS:
        if c in getattr(T, "_cipher_info", {}) and c not in ciphers:
            ciphers += (c,)
    T._preferred_ciphers = ciphers


def legacy_ssh_available() -> bool:
    info = getattr(paramiko.Transport, "_kex_info", {})
    return any(k in info for k in _LEGACY_KEX)


def paramiko_version() -> str:
    return paramiko.__version__
