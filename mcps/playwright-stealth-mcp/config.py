import os
import platform

USER_DATA_DIR = "../brave_stealth_profile"


def get_brave_path() -> str:
    """Get Brave browser path with Chromium fallback."""
    brave_path = os.getenv("BRAVE_PATH")
    if brave_path and os.path.exists(brave_path):
        return brave_path

    system = platform.system()
    if system == "Windows":
        path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    elif system == "Darwin":
        path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    elif system == "Linux":
        # Try multiple Brave locations
        for brave_location in ["/usr/bin/brave-browser", "/usr/bin/brave", "/snap/bin/brave"]:
            if os.path.exists(brave_location):
                return brave_location
        # Fallback to chromium
        for chromium_location in ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/snap/bin/chromium"]:
            if os.path.exists(chromium_location):
                return chromium_location
        path = "chromium"  # Let Playwright find it
    else:
        path = "brave"

    return path if os.path.exists(path) else "chromium"
