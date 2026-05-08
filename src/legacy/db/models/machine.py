"""
Physical machine / hardware inventory models.

Hierarchy
─────────
  Network               — subnet / VLAN segment that NICs connect to
  Machine               — physical or virtual host (default: local machine)
  ├── CPUInfo           — CPU socket(s)  [1-to-many]
  ├── MemoryModule      — RAM DIMM slot(s)  [1-to-many]
  ├── NetworkInterface  — NIC / network device  [1-to-many]
  │   └── InterfaceAddress  — IP address(es) per NIC  [1-to-many]
  ├── StorageDrive      — HDD / SSD / NVMe / USB  [1-to-many]
  │   └── StoragePartition  — partitions on a drive  [1-to-many]
  └── PCIDevice         — GPU / expansion cards  [1-to-many]

Machine.get_or_create_local() bootstraps the running host automatically.
"""


import os
import socket
import platform
from typing import TYPE_CHECKING

from css.core.db.models.base import BaseModel
from tortoise import fields

from css.core.db.fields import DescriptionField, PathField
from db.models.enums import (
    MachineType,
    DriveType,
    DriveHealth,
    MemoryType,
    InterfaceType,
)

if TYPE_CHECKING:
    pass


# ══════════════════════════════════════════════════════════════════════════════
# Network  —  subnet / VLAN / broadcast domain
# ══════════════════════════════════════════════════════════════════════════════

class Network(BaseModel):
    """A layer-3 network segment (subnet or VLAN)."""

    id          = fields.IntField(primary_key=True)
    name        = fields.CharField(max_length=128, db_index=True)
    description = DescriptionField(default="")
    cidr        = fields.CharField(max_length=49, default="", db_index=True)  # e.g. 192.168.1.0/24
    vlan_id     = fields.SmallIntField(null=True, db_index=True)               # 802.1Q VLAN tag
    gateway     = fields.CharField(max_length=45, default="")               # default GW IP
    dns_servers = fields.JSONField(default=list)                             # ["8.8.8.8", …]
    domain      = fields.CharField(max_length=255, default="")              # search domain
    is_internal = fields.BooleanField(default=True, db_index=True)
    notes       = fields.TextField(default="")
    created_at  = fields.DatetimeField(auto_now_add=True)
    updated_at  = fields.DatetimeField(auto_now=True)

    # back-references (defined on NetworkInterface)
    interfaces: fields.ReverseRelation["NetworkInterface"]

    class Meta:
        table = "networks"
        unique_together = [("cidr", "vlan_id")]
        ordering = ["name"]


# ══════════════════════════════════════════════════════════════════════════════
# Machine  —  physical / virtual host
# ══════════════════════════════════════════════════════════════════════════════

def _detect_virtual() -> bool:
    """Best-effort VM/container detection via /proc/cpuinfo and systemd-detect-virt."""
    try:
        import subprocess
        r = subprocess.run(
            ["systemd-detect-virt", "--quiet"],
            capture_output=True, timeout=2,
        )
        return r.returncode == 0          # 0 means "yes, virtualised"
    except Exception:
        pass
    try:
        with open("/proc/cpuinfo") as f:
            content = f.read().lower()
        return any(kw in content for kw in ("hypervisor", "vmware", "kvm", "xen", "qemu"))
    except OSError:
        return False


class Machine(BaseModel):
    """Physical or virtual host with full hardware inventory."""

    id          = fields.IntField(primary_key=True)

    # ── Identity ──────────────────────────────────────────────────────────────
    hostname    = fields.CharField(max_length=253, unique=True, db_index=True)
    fqdn        = fields.CharField(max_length=253, default="", db_index=True)
    machine_type = fields.CharEnumField(MachineType, default=MachineType.WORKSTATION, db_index=True)

    # ── Hardware overview (denormalised for quick access) ────────────────────
    manufacturer     = fields.CharField(max_length=128, default="")
    model_name       = fields.CharField(max_length=128, default="")
    serial_number    = fields.CharField(max_length=128, default="", db_index=True)
    chassis_type     = fields.CharField(max_length=64,  default="")   # tower, laptop, server…
    cpu_count        = fields.SmallIntField(default=0)                 # physical socket count
    total_memory_mb  = fields.IntField(default=0)

    # ── Firmware ──────────────────────────────────────────────────────────────
    bios_vendor       = fields.CharField(max_length=128, default="")
    bios_version      = fields.CharField(max_length=128, default="")
    bios_release_date = fields.CharField(max_length=32,  default="")
    uefi_enabled      = fields.BooleanField(null=True)
    secure_boot       = fields.BooleanField(null=True)
    tpm_version       = fields.CharField(max_length=16,  default="")  # "2.0", "1.2", ""

    # ── OS snapshot ───────────────────────────────────────────────────────────
    os_name    = fields.CharField(max_length=64,  default="")   # "Linux", "Windows"
    os_distro  = fields.CharField(max_length=128, default="")   # "Garuda Linux", "Ubuntu 24.04"
    os_release = fields.CharField(max_length=128, default="")   # kernel release "6.19.11-zen1"
    os_version = fields.CharField(max_length=256, default="")   # full version string
    os_arch    = fields.CharField(max_length=32,  default="")   # "x86_64", "aarch64"

    # ── Flags ─────────────────────────────────────────────────────────────────
    is_localhost  = fields.BooleanField(default=False, db_index=True)
    is_virtual    = fields.BooleanField(default=False, db_index=True)
    is_target     = fields.BooleanField(default=False, db_index=True)
    is_compromised = fields.BooleanField(default=False, db_index=True)

    # ── Optional link to investigation scope ──────────────────────────────────
    host = fields.ForeignKeyField(
        "models.Host", related_name="machine", null=True, on_delete=fields.SET_NULL,
    )

    # ── Meta ──────────────────────────────────────────────────────────────────
    notes        = fields.TextField(default="")
    discovered_at = fields.DatetimeField(null=True)
    first_seen_at = fields.DatetimeField(auto_now_add=True)
    last_seen_at  = fields.DatetimeField(auto_now=True)

    # ── Back-references ───────────────────────────────────────────────────────
    cpus:        fields.ReverseRelation["CPUInfo"]
    memory:      fields.ReverseRelation["MemoryModule"]
    interfaces:  fields.ReverseRelation["NetworkInterface"]
    drives:      fields.ReverseRelation["StorageDrive"]
    pci_devices: fields.ReverseRelation["PCIDevice"]

    class Meta:
        table    = "machines"
        ordering = ["hostname"]

    # ── Classmethod: bootstrap local machine ──────────────────────────────────
    @classmethod
    async def get_or_create_local(cls) -> tuple["Machine", bool]:
        """Gather system info and upsert the local machine.

        Safe to call repeatedly — uses ``get_or_create`` keyed on hostname.
        Returns (machine, created).
        """
        hostname = socket.gethostname()
        fqdn     = socket.getfqdn()
        os_name  = platform.system()
        os_rel   = platform.release()
        os_ver   = platform.version()
        arch     = platform.machine()

        # Distribution
        os_distro = ""
        try:
            import distro as _distro  # type: ignore[import-untyped] (optional)
            os_distro = _distro.name(pretty=True)
        except Exception:  # ImportError or any runtime error
            pass
        if not os_distro:
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            os_distro = line.split("=", 1)[1].strip().strip('"')
                            break
            except OSError:
                pass

        # Memory total
        total_memory_mb = 0
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        total_memory_mb = int(line.split()[1]) // 1024
                        break
        except OSError:
            pass

        # CPU socket count (unique physical-id values)
        cpu_count = 0
        try:
            with open("/proc/cpuinfo") as f:
                physical_ids: set[str] = set()
                for line in f:
                    if line.startswith("physical id"):
                        physical_ids.add(line.split(":")[1].strip())
            cpu_count = len(physical_ids) or 1
        except OSError:
            cpu_count = os.cpu_count() or 1

        machine, created = await cls.get_or_create(
            hostname=hostname,
            defaults={
                "fqdn":           fqdn,
                "os_name":        os_name,
                "os_distro":      os_distro,
                "os_release":     os_rel,
                "os_version":     os_ver,
                "os_arch":        arch,
                "is_localhost":   True,
                "is_virtual":     _detect_virtual(),
                "total_memory_mb": total_memory_mb,
                "cpu_count":      cpu_count,
                "machine_type":   MachineType.WORKSTATION,
                "notes":          "Local machine — seeded automatically at startup.",
            },
        )
        return machine, created


# ══════════════════════════════════════════════════════════════════════════════
# CPU
# ══════════════════════════════════════════════════════════════════════════════

class CPUInfo(BaseModel):
    """One physical CPU socket / package in a Machine."""

    id         = fields.IntField(primary_key=True)
    machine    = fields.ForeignKeyField("models.Machine", related_name="cpus", on_delete=fields.CASCADE)
    socket_id  = fields.SmallIntField(default=0)            # physical id from /proc/cpuinfo
    vendor     = fields.CharField(max_length=64,  default="")  # GenuineIntel, AuthenticAMD…
    model_name = fields.CharField(max_length=256, default="", db_index=True)
    cores      = fields.SmallIntField(default=0)            # physical cores
    threads    = fields.SmallIntField(default=0)            # logical processors
    base_freq_mhz = fields.IntField(default=0)
    max_freq_mhz  = fields.IntField(default=0)
    cache_l1_kb   = fields.IntField(default=0)
    cache_l2_kb   = fields.IntField(default=0)
    cache_l3_mb   = fields.IntField(default=0)
    architecture  = fields.CharField(max_length=32,  default="")
    flags         = fields.JSONField(default=list)           # ["vmx", "avx2", …]
    microcode     = fields.CharField(max_length=32,  default="")
    notes         = fields.TextField(default="")

    class Meta:
        table          = "cpu_info"
        unique_together = [("machine_id", "socket_id")]
        ordering        = ["machine_id", "socket_id"]


# ══════════════════════════════════════════════════════════════════════════════
# Memory
# ══════════════════════════════════════════════════════════════════════════════

class MemoryModule(BaseModel):
    """One physical RAM DIMM / memory slot in a Machine."""

    id           = fields.IntField(primary_key=True)
    machine      = fields.ForeignKeyField("models.Machine", related_name="memory", on_delete=fields.CASCADE)
    slot_id      = fields.CharField(max_length=32, default="")  # e.g. "DIMM_A1", "ChannelA-DIMM0"
    size_mb      = fields.IntField(default=0)
    memory_type  = fields.CharEnumField(MemoryType, default=MemoryType.DDR4, db_index=True)
    speed_mhz    = fields.IntField(default=0)
    manufacturer = fields.CharField(max_length=128, default="")
    serial_number = fields.CharField(max_length=64,  default="")
    part_number  = fields.CharField(max_length=64,  default="")
    bank_locator = fields.CharField(max_length=64,  default="")
    is_ecc       = fields.BooleanField(default=False, db_index=True)
    notes        = fields.TextField(default="")

    class Meta:
        table          = "memory_modules"
        unique_together = [("machine_id", "slot_id")]
        ordering        = ["machine_id", "slot_id"]


# ══════════════════════════════════════════════════════════════════════════════
# Network Interface  →  Network  +  InterfaceAddress
# ══════════════════════════════════════════════════════════════════════════════

class NetworkInterface(BaseModel):
    """A NIC / network device on a Machine."""

    id           = fields.IntField(primary_key=True)
    machine      = fields.ForeignKeyField("models.Machine", related_name="interfaces", on_delete=fields.CASCADE)
    network      = fields.ForeignKeyField(
        "models.Network", related_name="interfaces",
        null=True, on_delete=fields.SET_NULL, db_index=True
    )
    name         = fields.CharField(max_length=64, db_index=True)   # eth0, wlan0, enp3s0…
    iface_type   = fields.CharEnumField(InterfaceType, default=InterfaceType.ETHERNET, db_index=True)
    mac_address  = fields.CharField(max_length=17, default="", db_index=True)  # AA:BB:CC:DD:EE:FF
    speed_mbps   = fields.IntField(default=0)
    mtu          = fields.IntField(default=1500)
    driver       = fields.CharField(max_length=128, default="")
    vendor       = fields.CharField(max_length=128, default="")
    pci_address  = fields.CharField(max_length=32,  default="")   # "0000:03:00.0"
    is_up        = fields.BooleanField(default=True,  db_index=True)
    is_virtual   = fields.BooleanField(default=False, db_index=True)
    is_wireless  = fields.BooleanField(default=False, db_index=True)
    is_suspect   = fields.BooleanField(default=False, db_index=True)
    notes        = fields.TextField(default="")

    # back-reference
    addresses: fields.ReverseRelation["InterfaceAddress"]

    class Meta:
        table          = "network_interfaces"
        unique_together = [("machine_id", "name")]
        ordering        = ["machine_id", "name"]


class InterfaceAddress(BaseModel):
    """An IP address (v4 or v6) assigned to a NetworkInterface."""

    id          = fields.IntField(primary_key=True)
    interface   = fields.ForeignKeyField(
        "models.NetworkInterface", related_name="addresses", on_delete=fields.CASCADE,
    )
    address     = fields.CharField(max_length=45, db_index=True)   # "192.168.1.10"
    prefix_len  = fields.SmallIntField(default=24)               # CIDR prefix length
    version     = fields.SmallIntField(default=4, db_index=True)    # 4 or 6
    broadcast   = fields.CharField(max_length=45, default="")
    is_primary  = fields.BooleanField(default=False, db_index=True)
    is_dhcp     = fields.BooleanField(default=False, db_index=True)
    is_link_local = fields.BooleanField(default=False, db_index=True)
    assigned_at = fields.DatetimeField(null=True)
    notes       = fields.TextField(default="")

    class Meta:
        table          = "interface_addresses"
        unique_together = [("interface_id", "address")]
        ordering        = ["interface_id", "-is_primary", "address"]


# ══════════════════════════════════════════════════════════════════════════════
# Storage
# ══════════════════════════════════════════════════════════════════════════════

class StorageDrive(BaseModel):
    """A storage device (HDD / SSD / NVMe / USB…) attached to a Machine."""

    id            = fields.IntField(primary_key=True)
    machine       = fields.ForeignKeyField("models.Machine", related_name="drives", on_delete=fields.CASCADE)
    device_path   = PathField(max_length=64,  db_index=True)  # /dev/sda, /dev/nvme0n1
    drive_type    = fields.CharEnumField(DriveType, default=DriveType.SSD, db_index=True)
    health        = fields.CharEnumField(DriveHealth, default=DriveHealth.UNKNOWN, db_index=True)

    # Identity
    model_name    = fields.CharField(max_length=128, default="", db_index=True)
    manufacturer  = fields.CharField(max_length=128, default="")
    serial_number = fields.CharField(max_length=128, default="", db_index=True)
    firmware_rev  = fields.CharField(max_length=32,  default="")
    wwn           = fields.CharField(max_length=24,  default="")  # Worldwide Name

    # Geometry
    capacity_bytes   = fields.BigIntField(default=0)
    sector_size      = fields.IntField(default=512)
    rotational_rpm   = fields.IntField(default=0)   # 0 = non-spinning (SSD/NVMe)
    transport        = fields.CharField(max_length=32, default="")  # SATA, NVMe, USB, SAS…

    # Security
    is_encrypted   = fields.BooleanField(default=False, db_index=True)
    encryption_type = fields.CharField(max_length=64, default="")   # LUKS, BitLocker, …
    is_removable   = fields.BooleanField(default=False, db_index=True)

    # SMART raw JSON blob (populated by smartctl -a --json)
    smart_data     = fields.JSONField(default=dict)
    smart_passed   = fields.BooleanField(null=True, db_index=True)

    notes          = fields.TextField(default="")
    last_checked_at = fields.DatetimeField(null=True)

    # back-reference
    partitions: fields.ReverseRelation["StoragePartition"]

    class Meta:
        table          = "storage_drives"
        unique_together = [("machine_id", "device_path")]
        ordering        = ["machine_id", "device_path"]


class StoragePartition(BaseModel):
    """A partition on a StorageDrive."""

    id           = fields.IntField(primary_key=True)
    drive        = fields.ForeignKeyField("models.StorageDrive", related_name="partitions", on_delete=fields.CASCADE)
    device_path  = PathField(max_length=64, db_index=True)   # /dev/sda1, /dev/nvme0n1p1
    partition_number = fields.SmallIntField(default=1)
    partition_type   = fields.CharField(max_length=64, default="")  # Linux, EFI System, swap…
    filesystem   = fields.CharField(max_length=32, default="", db_index=True)  # ext4, xfs, ntfs…
    label        = fields.CharField(max_length=128, default="")
    uuid         = fields.CharField(max_length=36,  default="", db_index=True)
    mount_point  = fields.CharField(max_length=256, default="", db_index=True)
    size_bytes   = fields.BigIntField(default=0)
    is_mounted   = fields.BooleanField(default=False, db_index=True)
    is_encrypted = fields.BooleanField(default=False, db_index=True)
    is_boot      = fields.BooleanField(default=False, db_index=True)
    is_swap      = fields.BooleanField(default=False, db_index=True)
    notes        = fields.TextField(default="")

    class Meta:
        table          = "storage_partitions"
        unique_together = [("drive_id", "device_path")]
        ordering        = ["drive_id", "partition_number"]


# ══════════════════════════════════════════════════════════════════════════════
# PCI devices
# ══════════════════════════════════════════════════════════════════════════════

class PCIDevice(BaseModel):
    """A PCI / PCIe device (GPU, RAID card, capture card…) in a Machine."""

    id           = fields.IntField(primary_key=True)
    machine      = fields.ForeignKeyField("models.Machine", related_name="pci_devices", on_delete=fields.CASCADE)
    bus_address  = fields.CharField(max_length=16, db_index=True)  # "0000:03:00.0"
    class_code   = fields.CharField(max_length=8,  default="")  # "0x030200"
    class_name   = fields.CharField(max_length=128, default="", db_index=True)  # "VGA compatible controller"
    vendor_id    = fields.CharField(max_length=6,  default="")  # "10de"
    device_id    = fields.CharField(max_length=6,  default="")  # "2204"
    vendor_name  = fields.CharField(max_length=128, default="")
    device_name  = fields.CharField(max_length=256, default="", db_index=True)
    subsystem    = fields.CharField(max_length=256, default="")
    driver       = fields.CharField(max_length=64,  default="", db_index=True)
    kernel_module = fields.CharField(max_length=64, default="")
    is_suspect   = fields.BooleanField(default=False, db_index=True)
    notes        = fields.TextField(default="")

    class Meta:
        table          = "pci_devices"
        unique_together = [("machine_id", "bus_address")]
        ordering        = ["machine_id", "bus_address"]
