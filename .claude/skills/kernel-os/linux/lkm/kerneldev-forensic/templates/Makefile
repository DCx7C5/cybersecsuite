# CyberSec Forensic LKM Development Makefile
# For use with kerneldev-forensic skill

# Kernel source directory - adjust as needed
KERNEL_SRC ?= /usr/src/linux-headers-$(shell uname -r)
KERNEL_BUILD ?= /lib/modules/$(shell uname -r)/build

# Module objects
obj-m += forensic_sysfs_interface.o
obj-m += syscall_monitor.o
obj-m += rootkit_scanner.o
obj-m += memory_forensics.o

# Default target - build all modules
all: modules

# Build modules
modules:
	@echo "Building CyberSec Forensic LKMs..."
	$(MAKE) -C $(KERNEL_BUILD) M=$(PWD) modules

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	$(MAKE) -C $(KERNEL_BUILD) M=$(PWD) clean
	rm -f *.symvers *.order

# Install modules to system (requires root)
install: modules
	@echo "Installing forensic modules..."
	sudo $(MAKE) -C $(KERNEL_BUILD) M=$(PWD) modules_install
	sudo depmod -a

# Load forensic sysfs interface
load-sysfs:
	@echo "Loading forensic sysfs interface..."
	sudo insmod forensic_sysfs_interface.ko
	@echo "Interface available at /sys/kernel/forensic_mcp/"

# Load syscall monitor
load-syscall:
	@echo "Loading syscall monitor..."
	sudo insmod syscall_monitor.ko
	@echo "Monitor available at /sys/kernel/syscall_monitor/"

# Unload all forensic modules
unload:
	@echo "Unloading forensic modules..."
	-sudo rmmod syscall_monitor 2>/dev/null || true
	-sudo rmmod forensic_sysfs_interface 2>/dev/null || true
	-sudo rmmod rootkit_scanner 2>/dev/null || true
	-sudo rmmod memory_forensics 2>/dev/null || true

# Test forensic interface
test-sysfs: load-sysfs
	@echo "Testing forensic sysfs interface..."
	@echo "Module status:"
	cat /sys/kernel/forensic_mcp/status
	@echo "Sending PING command:"
	echo "PING" | sudo tee /sys/kernel/forensic_mcp/message
	@echo "Response:"
	cat /sys/kernel/forensic_mcp/message

# Test syscall monitor
test-syscall: load-syscall
	@echo "Testing syscall monitor..."
	@echo "Current configuration:"
	cat /sys/kernel/syscall_monitor/config
	@echo "Enabling monitoring:"
	echo "monitoring_enabled=true" | sudo tee /sys/kernel/syscall_monitor/config
	@echo "Statistics:"
	cat /sys/kernel/syscall_monitor/stats

# Development helpers
check-env:
	@echo "Kernel build environment check:"
	@echo "Kernel version: $(shell uname -r)"
	@echo "Kernel source: $(KERNEL_SRC)"
	@echo "Kernel build: $(KERNEL_BUILD)"
	@echo "Architecture: $(shell uname -m)"
	@if [ ! -d "$(KERNEL_BUILD)" ]; then \
		echo "ERROR: Kernel headers not found at $(KERNEL_BUILD)"; \
		echo "Install with: sudo pacman -S linux-headers"; \
		exit 1; \
	fi

# Sign modules (development signing)
sign: modules
	@echo "Signing modules for development..."
	@if [ -f "MOK.priv" ] && [ -f "MOK.der" ]; then \
		for mod in *.ko; do \
			echo "Signing $$mod"; \
			$(KERNEL_BUILD)/scripts/sign-file sha256 MOK.priv MOK.der $$mod; \
		done; \
	else \
		echo "No signing keys found. Generate with: make generate-keys"; \
	fi

# Generate development signing keys
generate-keys:
	@echo "Generating development module signing keys..."
	openssl req -new -x509 -newkey rsa:2048 -keyout MOK.priv -outform DER -out MOK.der -nodes -days 36500 -subj "/CN=CyberSec Forensic Module Signing/"
	@echo "Keys generated: MOK.priv (private) and MOK.der (certificate)"
	@echo "Install certificate with: sudo mokutil --import MOK.der"

# Show module information
info:
	@echo "Available forensic modules:"
	@for mod in *.ko; do \
		if [ -f "$$mod" ]; then \
			echo "Module: $$mod"; \
			modinfo "$$mod" 2>/dev/null | grep -E "(filename|description|author|license|version)" || true; \
			echo ""; \
		fi; \
	done

# Check loaded forensic modules
status:
	@echo "Currently loaded forensic modules:"
	lsmod | grep -E "(forensic|syscall_monitor|rootkit_scanner|memory_forensics)" || echo "No forensic modules loaded"
	@echo ""
	@echo "Forensic interfaces:"
	@ls -la /sys/kernel/forensic_mcp/ 2>/dev/null || echo "  forensic_mcp: not loaded"
	@ls -la /sys/kernel/syscall_monitor/ 2>/dev/null || echo "  syscall_monitor: not loaded"

# Python script to register built .ko modules with the CyberSec database.
# Stored as a Make variable and piped to Python to avoid multi-line recipe issues.
define _DB_REGISTER_PY
import asyncio, os, sys
_pr = os.environ.get("CYBERSEC_PROJECT_ROOT") or os.path.abspath(
    os.path.join(os.getcwd(), "../../.."))
if _pr not in sys.path:
    sys.path.insert(0, _pr)
try:
    from db.models.kernel import Kernel, KernelModule
    from db.models.enums import ModuleStatus
    async def register_modules():
        print(f"CyberSec DB: registering kernel modules (project root: {_pr})")
        # Uncomment to run against a live database:
        # from tortoise import Tortoise
        # import db.models as _m
        # await Tortoise.init(config=_m.TORTOISE_ORM)
        # for ko in [f for f in os.listdir(".") if f.endswith(".ko")]:
        #     await KernelModule.get_or_create(name=ko[:-3],
        #         defaults={"status": ModuleStatus.LOADED})
        # await Tortoise.close_connections()
        print("Module registration complete.")
    asyncio.run(register_modules())
except ImportError as exc:
    print(f"Warning: CyberSec models not found ({exc}).")
    print("Set CYBERSEC_PROJECT_ROOT or run from inside the project tree.")
endef
export _DB_REGISTER_PY

# Integration with CyberSec database
db-register: modules
	@echo "Registering modules with CyberSec database..."
	@echo "$$_DB_REGISTER_PY" | python3

.PHONY: all modules clean install load-sysfs load-syscall unload test-sysfs test-syscall check-env sign generate-keys info status db-register