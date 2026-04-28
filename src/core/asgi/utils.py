


# ── Startup / shutdown ────────────────────────────────────────────────────────


async def _on_startup() -> None:
    """Initialize DB + AI asgi rate limiters on startup."""
    log.info("ASGI startup — initialising database and rate limiters")

    # First-run check (non-fatal)
    try:
        from startup.first_run import first_run_setup
        await first_run_setup()
        log.info("Startup status checked")
    except Exception as exc:
        log.warning("First-run check failed: %s", exc)

    # IPC server (non-fatal)
    try:
        from hooks.ipc_receiver import ensure_ipc_server
        await ensure_ipc_server()
        log.info("IPC server started")
    except Exception as exc:
        log.warning("IPC server failed: %s", exc)

    auto_create = os.environ.get("CYBERSEC_AUTO_CREATE_DB", "false").lower() == "true"
    auto_intel = os.environ.get("CYBERSEC_BOOTSTRAP_INTEL_ON_START", "false").lower() == "true"
    await init_tortoise_async(create_db=auto_create, bootstrap_intel=auto_intel)

    for provider in get_enabled_providers():
        rate_limiter.configure(
            provider.id,
            ProviderLimits(
                rpm=provider.rate_limit_rpm,
                tpm=provider.rate_limit_tpm,
            ),
        )

    _telemetry_collector.start()

    app.state.agent_stream_tasks: dict[str, asyncio.Task] = {}
    app.state.agent_stream_queues: dict[str, asyncio.Queue] = {}

    try:
        from llm.otel import setup_otel

        setup_otel(service_name=os.environ.get("OTEL_SERVICE_NAME", "cybersecsuite-asgi"))
        log.info("OTEL tracing configured")
    except Exception as exc:
        log.warning("OTEL unavailable — continuing without tracing export: %s", exc)

    # OpenObserve — non-fatal if unavailable
    try:
        from openobserve.streams import ensure_streams
        from openobserve.writer import start_flush_loop

        await ensure_streams()
        start_flush_loop()
        log.info("OpenObserve streams ready")
    except Exception as exc:
        log.warning("OpenObserve unavailable — continuing without it: %s", exc)


async def _on_shutdown() -> None:
    log.info("ASGI shutdown — flushing telemetry and closing connections")
    _telemetry_collector.stop()

    # IPC server
    try:
        from hooks.ipc_receiver import stop_ipc_server
        await stop_ipc_server()
        log.info("IPC server stopped")
    except Exception as exc:
        log.warning("IPC server shutdown error: %s", exc)

    # OpenObserve
    try:
        from openobserve.writer import flush_all, stop_flush_loop
        from openobserve.client import close_client

        stop_flush_loop()
        await flush_all()
        await close_client()
        log.info("OpenObserve flushed and closed")
    except Exception as exc:
        log.warning("OpenObserve shutdown error: %s", exc)

    await cleanup_executors()
    await close_tortoise()
    log.info("ASGI shutdown complete")
