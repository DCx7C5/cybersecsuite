"""
UvicornProcessManager — manages uvicorn as an asyncio subprocess.

Full lifecycle control (start / stop / restart / is_alive) while keeping
the manager's event loop responsive.  Uvicorn runs in a separate process
group so Ctrl+C on the CLI reaches only the manager, which then forwards
a graceful shutdown signal.
"""

import asyncio

import msgspec
from os import getpgid, killpg, getenv
from sys import executable as sys_executable
from signal import SIGINT, SIGTERM

from css.core.logger import getLogger
from css.core.settings.config import DEBUG

log = getLogger(__name__)


class UvicornProcessManager(msgspec.Struct, kw_only=True):
    host: str = getenv("ASGI_HOST", "127.0.0.1")
    port: int = int(getenv("ASGI_PORT", "8000"))
    reload: bool = getenv("ASGI_RELOAD", "false").lower() in ("1", "true", "yes")
    workers: int = 2 if not reload else 1
    log_level: str = "debug" if DEBUG else "info"
    app: str = "css.core.asgi.app:app"

    _process: asyncio.subprocess.Process | None = None

    @property
    def is_alive(self) -> bool:
        return self._process is not None and self._process.returncode is None

    def _build_args(self) -> list[str]:
        args = [
            sys_executable,
            "-m", "uvicorn",
            self.app,
            "--host", str(self.host),
            "--port", str(self.port),
            "--log-level", self.log_level,
        ]
        if self.reload:
            args.append("--reload")
        if not self.reload and self.workers > 1:
            args.extend(["--workers", str(self.workers)])
        return args

    async def start(self) -> None:
        if self.is_alive:
            log.warning("Uvicorn already running (pid=%d)", self._process.pid)
            return

        args = self._build_args()
        log.info("Starting uvicorn: %s", " ".join(args))

        proc = await asyncio.create_subprocess_exec(
            *args,
            start_new_session=True,
        )
        self._process = proc
        log.info("Uvicorn started (pid=%d, process group=%d)", proc.pid, getpgid(proc.pid))

    async def stop(self, timeout: float = 30.0) -> None:
        proc = self._process
        if proc is None or proc.returncode is not None:
            self._process = None
            return

        pid = proc.pid
        log.info("Stopping uvicorn (pid=%d)", pid)

        try:
            pgid = getpgid(pid)
            killpg(pgid, SIGINT)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.send_signal(SIGINT)
            except ProcessLookupError:
                pass

        try:
            await asyncio.wait_for(proc.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            log.warning("Uvicorn pid=%d did not stop in %.0fs, escalating to SIGTERM", pid, timeout)
            try:
                killpg(getpgid(pid), SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                try:
                    proc.send_signal(SIGTERM)
                except ProcessLookupError:
                    pass
            await proc.wait()
        except ProcessLookupError:
            pass

        self._process = None
        log.info("Uvicorn stopped")

    async def restart(self, timeout: float = 30.0) -> None:
        await self.stop(timeout=timeout)
        await self.start()

    async def wait(self) -> None:
        proc = self._process
        if proc is not None:
            await proc.wait()

    async def __aenter__(self) -> UvicornProcessManager:
        await self.start()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.stop()
