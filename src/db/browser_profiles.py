"""
Browser profile database abstraction — ORM-like wrapper for external browser SQLite files.

Treats browser profile DBs (Firefox, Chrome, Brave) as queryable data sources with
ORM-style method names. Encapsulates all sqlite3 calls.
"""


import sqlite3
from pathlib import Path
from typing import Any


class BrowserCookiesDB:
    """ORM-like wrapper for browser Cookies database."""

    def __init__(self, db_path: Path):
        """Initialize with path to browser cookies.db file."""
        self.db_path = db_path
        if not db_path.exists():
            raise FileNotFoundError(f"Cookies database not found: {db_path}")


    def get_all_tables(self) -> list[str]:
        """List all tables in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def get_cookies_by_domain(self, limit: int = 20) -> list[dict[str, Any]]:
        """
        Get cookie counts aggregated by domain.

        Returns:
            List of {host_key, cookie_count} dicts, sorted by count DESC.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT host_key, COUNT(*) as cookie_count
                FROM cookies
                GROUP BY host_key
                ORDER BY cookie_count DESC
                LIMIT ?
            """, (limit,))
            results = [
                {"host_key": row[0], "cookie_count": row[1]}
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
        return results

    def get_auth_cookies(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Find authentication-related cookies.

        Returns:
            List of {host_key, name, value_length} dicts.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT host_key, name, LENGTH(value) as value_length
                FROM cookies
                WHERE name LIKE '%auth%' OR name LIKE '%session%' OR name LIKE '%token%'
                LIMIT ?
            """, (limit,))
            results = [
                {"host_key": row[0], "name": row[1], "value_length": row[2]}
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
        return results

    def get_suspicious_domains(self) -> list[dict[str, Any]]:
        """Find cookies for suspicious domains (.onion, localhost, etc)."""
        suspicious_patterns = ['.onion', 'localhost', '127.0.0.1']
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT host_key FROM cookies")
            all_domains = [row[0] for row in cursor.fetchall()]
            results = [
                {"host_key": d}
                for d in all_domains
                if any(p in d for p in suspicious_patterns)
            ]
        finally:
            conn.close()
        return results


class BrowserHistoryDB:
    """ORM-like wrapper for browser History database."""

    def __init__(self, db_path: Path):
        """Initialize with path to browser History database."""
        self.db_path = db_path
        if not db_path.exists():
            raise FileNotFoundError(f"History database not found: {db_path}")

    def get_recent_urls(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get most recently visited URLs.

        Returns:
            List of {url, title, visit_count, last_visit_time} dicts.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time
                FROM urls
                ORDER BY last_visit_time DESC
                LIMIT ?
            """, (limit,))
            results = [
                {
                    "url": row[0],
                    "title": row[1],
                    "visit_count": row[2],
                    "last_visit_time": row[3],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
        return results

    def get_suspicious_urls(self) -> list[dict[str, Any]]:
        """Find URLs matching suspicious patterns."""
        suspicious_patterns = [
            'localhost', '127.0.0.1', 'file://', '.onion',
            'data:', 'javascript:', 'chrome-extension://', 'moz-extension://'
        ]
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT url, visit_count, last_visit_time
                FROM urls
                ORDER BY last_visit_time DESC
                LIMIT 500
            """)
            all_urls = cursor.fetchall()
            results = []
            for url, visit_count, last_visit_time in all_urls:
                for pattern in suspicious_patterns:
                    if pattern.lower() in url.lower():
                        results.append({
                            "url": url,
                            "visit_count": visit_count,
                            "last_visit_time": last_visit_time,
                            "pattern": pattern,
                        })
                        break
        finally:
            conn.close()
        return results

    def get_high_visit_urls(self, min_visits: int = 100) -> list[dict[str, Any]]:
        """Find URLs visited very frequently."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT url, visit_count
                FROM urls
                WHERE visit_count > ?
                ORDER BY visit_count DESC
                LIMIT 50
            """, (min_visits,))
            results = [
                {"url": row[0], "visit_count": row[1]}
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
        return results

    def has_downloads_table(self) -> bool:
        """Check if downloads table exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='downloads'
            """)
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def get_downloads(self, limit: int = 20) -> list[dict[str, Any]]:
        """
        Get download history.

        Returns:
            List of {target_path, url, start_time, total_bytes} dicts.
        """
        if not self.has_downloads_table():
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT target_path, url, start_time, total_bytes
                FROM downloads
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            results = [
                {
                    "target_path": row[0],
                    "url": row[1],
                    "start_time": row[2],
                    "total_bytes": row[3],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
        return results

    def get_suspicious_downloads(self) -> list[dict[str, Any]]:
        """Find downloads to suspicious locations or with suspicious extensions."""
        if not self.has_downloads_table():
            return []

        suspicious_extensions = ('.exe', '.scr', '.bat', '.cmd', '.pif', '.com')
        suspicious_paths = ('/tmp/', '/dev/shm/')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT target_path, url, start_time
                FROM downloads
                ORDER BY start_time DESC
                LIMIT 500
            """)
            all_downloads = cursor.fetchall()
            results = []
            for target_path, url, start_time in all_downloads:
                reason = None
                if any(target_path.startswith(p) for p in suspicious_paths):
                    reason = "suspicious_location"
                elif target_path.endswith(suspicious_extensions):
                    reason = "suspicious_extension"

                if reason:
                    results.append({
                        "target_path": target_path,
                        "url": url,
                        "start_time": start_time,
                        "reason": reason,
                    })
        finally:
            conn.close()
        return results


class BrowserPreferencesDB:
    """Wrapper for browser preferences (usually JSON, not SQLite)."""

    def __init__(self, prefs_path: Path):
        """Initialize with path to preferences file."""
        self.prefs_path = prefs_path
        if not prefs_path.exists():
            raise FileNotFoundError(f"Preferences file not found: {prefs_path}")
        self._prefs = None

    def _load_prefs(self) -> dict:
        """Lazy-load preferences JSON."""
        if self._prefs is None:
            import json
            with open(self.prefs_path, 'r') as f:
                self._prefs = json.load(f)
        return self._prefs

    def get_all_settings(self) -> dict:
        """Get entire preferences dict."""
        return self._load_prefs()

    def get_setting(self, path: str, default: Any = None) -> Any:
        """
        Get a nested setting by dot-notation path.

        Example: get_setting("profile.default_content_setting_values.notifications")
        """
        prefs = self._load_prefs()
        current = prefs
        try:
            for key in path.split('.'):
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def get_suspicious_settings(self) -> list[dict[str, Any]]:
        """Find suspicious settings."""
        suspicious_paths = {
            "profile.default_content_setting_values.notifications": "Browser notifications enabled",
            "profile.default_content_settings.popups": "Popups allowed",
            "profile.managed_users": "Managed users configured",
            "browser.startup_urls": "Custom startup URLs",
            "extensions.settings": "Extension settings modifications",
        }

        results = []
        for path, description in suspicious_paths.items():
            value = self.get_setting(path)
            if value:
                results.append({
                    "setting": path,
                    "description": description,
                    "value": str(value)[:100],  # Truncate for readability
                })
        return results

    def get_forced_extensions(self) -> list[dict[str, Any]]:
        """Find extensions that were pre-installed by OEM or default."""
        prefs = self._load_prefs()
        extensions = prefs.get("extensions", {}).get("settings", {})
        results = []

        for ext_id, ext_info in extensions.items():
            if ext_info.get("was_installed_by_oem") or ext_info.get("was_installed_by_default"):
                ext_name = ext_info.get("manifest", {}).get("name", "Unknown")
                results.append({
                    "extension_id": ext_id,
                    "extension_name": ext_name,
                    "oem": ext_info.get("was_installed_by_oem", False),
                    "default": ext_info.get("was_installed_by_default", False),
                })
        return results

