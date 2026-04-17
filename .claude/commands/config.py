#!/usr/bin/env python3
"""
MalwareHunter Configuration - Dynamic system detection and configuration
Provides system-agnostic configuration for the MalwareHunter suite
"""
import os
import platform
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class MalwareHunterConfig:
    def __init__(self):
        self.config = self._detect_system()
        self.base_dir = self._get_base_dir()
        self.session_dir = None

    def _get_base_dir(self) -> Path:
        """Get base directory for MalwareHunter sessions"""
        # Check environment variable first
        base_dir = os.environ.get('MALWAREHUNTER_BASE_DIR')
        if base_dir:
            return Path(base_dir).expanduser()

        # Default to user home
        return Path.home() / "MalwareHunter"

    def _detect_system(self) -> Dict:
        """Dynamically detect system configuration"""
        config = {}

        # Basic system info
        config['os'] = platform.system()
        config['distribution'] = self._get_distribution()
        config['kernel'] = platform.release()
        config['architecture'] = platform.machine()
        config['hostname'] = platform.node()

        # Hardware detection
        config['gpu'] = self._detect_gpu()
        config['desktop'] = self._detect_desktop()

        # Security features
        config['security'] = self._check_security_features()

        # Available tools
        config['tools'] = self._check_available_tools()

        # Browsers
        config['browsers'] = self._detect_browsers()

        # Package manager
        config['package_manager'] = self._detect_package_manager()

        return config

    def _get_distribution(self) -> str:
        """Detect Linux distribution"""
        try:
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('NAME='):
                            return line.split('=')[1].strip().strip('"')
            return platform.system()
        except Exception:
            return platform.system()

    def _detect_gpu(self) -> Dict:
        """Detect GPU configuration"""
        gpu_info = {
            'nvidia_devices': [],
            'framebuffer_devices': [],
            'dri_devices': [],
            'accessible_devices': []
        }

        # Check for NVIDIA devices
        nvidia_base = '/dev'
        for i in range(10):
            nvidia_dev = f'/dev/nvidia{i}'
            if os.path.exists(nvidia_dev):
                gpu_info['nvidia_devices'].append(nvidia_dev)
                # Check permissions
                try:
                    stat_info = os.stat(nvidia_dev)
                    if stat_info.st_mode & 0o006:  # World readable/writable
                        gpu_info['accessible_devices'].append(nvidia_dev)
                except OSError:
                    pass

        # Check framebuffer devices
        for i in range(10):
            fb_dev = f'/dev/fb{i}'
            if os.path.exists(fb_dev):
                gpu_info['framebuffer_devices'].append(fb_dev)
                try:
                    stat_info = os.stat(fb_dev)
                    if stat_info.st_mode & 0o006:
                        gpu_info['accessible_devices'].append(fb_dev)
                except OSError:
                    pass

        # Check DRI devices
        dri_dir = Path('/dev/dri')
        if dri_dir.exists():
            for device in dri_dir.iterdir():
                gpu_info['dri_devices'].append(str(device))

        return gpu_info

    def _detect_desktop(self) -> Dict:
        """Detect desktop environment"""
        desktop_info = {
            'environment': None,
            'display_server': None,
            'session_type': None
        }

        # Common desktop environment variables
        de_vars = ['XDG_CURRENT_DESKTOP', 'DESKTOP_SESSION', 'GDMSESSION']
        for var in de_vars:
            value = os.environ.get(var)
            if value:
                desktop_info['environment'] = value
                break

        # Display server detection
        if os.environ.get('WAYLAND_DISPLAY'):
            desktop_info['display_server'] = 'Wayland'
            desktop_info['session_type'] = 'wayland'
        elif os.environ.get('DISPLAY'):
            desktop_info['display_server'] = 'X11'
            desktop_info['session_type'] = 'x11'

        return desktop_info

    def _check_security_features(self) -> Dict:
        """Check system security features"""
        security = {}

        # Secure Boot
        try:
            result = subprocess.run(['mokutil', '--sb-state'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                security['secure_boot'] = 'enabled' if 'enabled' in result.stdout.lower() else 'disabled'
        except (FileNotFoundError, subprocess.SubprocessError):
            security['secure_boot'] = 'unknown'

        # IOMMU/VT-d
        try:
            with open('/proc/cmdline', 'r') as f:
                cmdline = f.read()
            security['iommu'] = 'enabled' if 'iommu=on' in cmdline else 'unknown'
        except Exception:
            security['iommu'] = 'unknown'

        # Ptrace scope
        try:
            with open('/proc/sys/kernel/yama/ptrace_scope', 'r') as f:
                security['ptrace_scope'] = int(f.read().strip())
        except Exception:
            security['ptrace_scope'] = 'unknown'

        return security

    def _check_available_tools(self) -> Dict:
        """Check availability of forensic tools"""
        tools = {}

        tool_categories = {
            'rootkit_detection': ['rkhunter', 'unhide', 'unhide-tcp', 'lynis'],
            'network_analysis': ['tcpdump', 'tshark', 'wireshark', 'nmap', 'ss', 'ip'],
            'memory_analysis': ['gcore', 'strings', 'hexdump', 'xxd'],
            'system_analysis': ['lsof', 'strace', 'ltrace', 'pmap'],
            'package_management': ['pacman', 'apt', 'dnf', 'zypper'],
            'forensics': ['binwalk', 'yara', 'volatility']
        }

        for category, tool_list in tool_categories.items():
            tools[category] = {}
            for tool in tool_list:
                tools[category][tool] = shutil.which(tool) is not None

        return tools

    def _detect_browsers(self) -> Dict:
        """Detect installed browsers and their paths"""
        browsers = {}

        home = Path.home()
        browser_configs = {
            'brave': {
                'config_dir': home / '.config/BraveSoftware/Brave-Browser',
                'profile_dir': home / '.config/BraveSoftware/Brave-Browser/Default',
                'executable': 'brave'
            },
            'chrome': {
                'config_dir': home / '.config/google-chrome',
                'profile_dir': home / '.config/google-chrome/Default',
                'executable': 'google-chrome'
            },
            'chromium': {
                'config_dir': home / '.config/chromium',
                'profile_dir': home / '.config/chromium/Default',
                'executable': 'chromium'
            },
            'firefox': {
                'config_dir': home / '.mozilla/firefox',
                'profile_dir': None,  # Dynamic detection needed
                'executable': 'firefox'
            }
        }

        for browser_name, config in browser_configs.items():
            browser_info = {
                'installed': shutil.which(config['executable']) is not None,
                'config_exists': config['config_dir'].exists() if config['config_dir'] else False,
                'config_dir': str(config['config_dir']) if config['config_dir'] else None,
                'profile_dir': str(config['profile_dir']) if config['profile_dir'] else None
            }

            # Special handling for Firefox profiles
            if browser_name == 'firefox' and browser_info['config_exists']:
                profiles_ini = config['config_dir'] / 'profiles.ini'
                if profiles_ini.exists():
                    # Find default profile
                    try:
                        with open(profiles_ini, 'r') as f:
                            content = f.read()
                        for line in content.split('\n'):
                            if line.startswith('Path='):
                                profile_path = line.split('=')[1].strip()
                                browser_info['profile_dir'] = str(config['config_dir'] / profile_path)
                                break
                    except Exception:
                        pass

            browsers[browser_name] = browser_info

        return browsers

    def _detect_package_manager(self) -> Dict:
        """Detect system package manager"""
        managers = {
            'pacman': ['pacman', 'makepkg'],
            'apt': ['apt', 'dpkg'],
            'dnf': ['dnf', 'rpm'],
            'zypper': ['zypper', 'rpm'],
            'portage': ['emerge', 'ebuild']
        }

        for manager, commands in managers.items():
            if all(shutil.which(cmd) for cmd in commands):
                return {
                    'type': manager,
                    'available': True,
                    'commands': commands
                }

        return {'type': 'unknown', 'available': False, 'commands': []}

    def create_session_dir(self) -> Path:
        """Create a new session directory"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.base_dir / "sessions" / timestamp
        session_dir.mkdir(parents=True, exist_ok=True)

        # Create artifact subdirectories
        artifact_dirs = [
            'artifacts/network', 'artifacts/processes', 'artifacts/browser',
            'artifacts/firmware', 'artifacts/kernel', 'artifacts/memory',
            'artifacts/logs', 'artifacts/packages', 'artifacts/raw',
            'raw_dumps'
        ]

        for artifact_dir in artifact_dirs:
            (session_dir / artifact_dir).mkdir(parents=True, exist_ok=True)

        self.session_dir = session_dir
        return session_dir

    def get_browser_paths(self, browser: str) -> Dict:
        """Get browser-specific paths"""
        if browser not in self.config['browsers']:
            return {}

        browser_info = self.config['browsers'][browser]
        if not browser_info['installed'] or not browser_info['config_exists']:
            return {}

        home = Path.home()

        if browser == 'brave':
            base_dir = home / '.config/BraveSoftware/Brave-Browser/Default'
            return {
                'config': home / '.config/BraveSoftware/Brave-Browser',
                'profile': base_dir,
                'cookies': base_dir / 'Cookies',
                'history': base_dir / 'History',
                'extensions': base_dir / 'Extensions',
                'preferences': base_dir / 'Preferences'
            }
        elif browser == 'chrome':
            base_dir = home / '.config/google-chrome/Default'
            return {
                'config': home / '.config/google-chrome',
                'profile': base_dir,
                'cookies': base_dir / 'Cookies',
                'history': base_dir / 'History',
                'extensions': base_dir / 'Extensions',
                'preferences': base_dir / 'Preferences'
            }
        elif browser == 'firefox' and browser_info['profile_dir']:
            profile_dir = Path(browser_info['profile_dir'])
            return {
                'config': home / '.mozilla/firefox',
                'profile': profile_dir,
                'cookies': profile_dir / 'cookies.sqlite',
                'history': profile_dir / 'places.sqlite',
                'extensions': profile_dir / 'extensions.json',
                'preferences': profile_dir / 'prefs.js'
            }

        return {}

    def get_legitimate_services(self) -> List[str]:
        """Get list of legitimate services that should not be flagged"""
        base_services = [
            # Network services
            'NetworkManager', 'systemd-networkd', 'wpa_supplicant',
            # Display services
            'Xorg', 'gdm', 'lightdm', 'sddm', 'cosmic-greeter',
            # Package managers
            'pacman', 'apt', 'dpkg', 'dnf', 'zypper',
            # Container services
            'docker', 'podman', 'containerd',
            # Security services
            'ufw', 'firewalld', 'auditd',
            # Hardware services
            'pulseaudio', 'pipewire', 'haveged'
        ]

        # Add GPU-specific services
        if self.config['gpu']['nvidia_devices']:
            base_services.extend(['nvidia-persistenced', 'nvidia-powerd'])

        # Add desktop-specific services
        desktop = self.config['desktop']['environment']
        if desktop:
            if 'gnome' in desktop.lower():
                base_services.extend(['gnome-shell', 'gnome-session'])
            elif 'kde' in desktop.lower():
                base_services.extend(['plasmashell', 'kwin'])
            elif 'cosmic' in desktop.lower():
                base_services.extend(['cosmic-comp', 'cosmic-panel'])

        return base_services

    def get_mode_config(self) -> Dict:
        """Get red/blue team mode configuration"""
        mode = get_mode()
        base_config = {
            "mode": mode,
            "non_destructive": mode == "blue",
            "cross_validation_required": mode == "blue",
            "exploit_suggestions": mode == "red",
            "offensive_capabilities": mode == "red"
        }

        if mode == "red":
            base_config.update({
                "focus": ["vulnerability_assessment", "exploit_development", "attack_simulation"],
                "preferred_model": "opus",
                "analysis_depth": "aggressive"
            })
        else:
            base_config.update({
                "focus": ["threat_detection", "incident_response", "forensic_analysis"],
                "preferred_model": "sonnet",
                "analysis_depth": "thorough"
            })

        return base_config

    def get_enabled_skills(self) -> List[str]:
        """Get skills enabled for current mode"""
        mode = get_mode()
        base_skills = ["shared-memory"]

        if mode == "red":
            base_skills.extend([
                "reverse-engineering:binary-analysis-patterns",
                "reverse-engineering:anti-reversing-techniques",
                "reverse-engineering:malware-analyst"
            ])
        else:
            base_skills.extend([
                "reverse-engineering:memory-forensics",
                "reverse-engineering:protocol-reverse-engineering",
                "reverse-engineering:mitre-attack-mapper"
            ])

        return base_skills
        """Save current configuration to file"""
        if session_dir is None:
            session_dir = self.session_dir or self.create_session_dir()

        # Include mode configuration in saved config
        config_to_save = {
            **self.config,
            "mode_config": self.get_mode_config(),
            "enabled_skills": self.get_enabled_skills()
        }

        config_file = session_dir / 'system_config.json'
        with open(config_file, 'w') as f:
            json.dump(config_to_save, f, indent=2, default=str)

        return config_file

def get_mode(settings_path: str = None) -> str:
    """
    Lese den aktuellen Red/Blue Team Modus aus settings.json.
    Gibt "blue" zurück, falls kein Modus gesetzt ist.
    """
    if settings_path is None:
        settings_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        return settings.get('mode', 'blue')
    except Exception:
        return 'blue'

# Global configuration instance
_config_instance = None

def get_config() -> MalwareHunterConfig:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = MalwareHunterConfig()
    return _config_instance