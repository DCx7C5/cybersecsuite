"""Snapshot management helpers — DB operations on ThreatIntelFeedSnapshot."""


from pathlib import Path
from typing import Any

from db.models.feed_snapshot import ThreatIntelFeedSnapshot
from db.intel._utils import _relative_source, _snapshot_id, _count_payload_records


async def _snapshot_is_current(
    path: Path, force: bool = False
) -> tuple[str, ThreatIntelFeedSnapshot | None, bool]:
    snap_id = _snapshot_id(path)
    if force:
        return snap_id, None, False

    source_file = _relative_source(path)
    existing = await ThreatIntelFeedSnapshot.get_or_none(source_file=source_file)
    return snap_id, existing, bool(existing and existing.snapshot_id == snap_id)


async def _store_snapshot(
    path: Path,
    snapshot_id: str,
    feed_name: str,
    payload: dict[str, Any],
    **extra: Any,
) -> None:
    source_file = _relative_source(path)
    existing = await ThreatIntelFeedSnapshot.get_or_none(source_file=source_file)
    defaults = {
        "provider": extra.get("provider", "internal"),
        "feed_name": feed_name,
        "feed_kind": extra.get("feed_kind", feed_name),
        "snapshot_id": snapshot_id,
        "source_url": extra.get("source_url", ""),
        "record_count": extra.get("record_count", _count_payload_records(payload)),
        "payload": payload,
    }
    if existing:
        existing.provider = defaults["provider"]
        existing.feed_name = feed_name
        existing.feed_kind = defaults["feed_kind"]
        existing.snapshot_id = snapshot_id
        existing.source_url = defaults["source_url"]
        existing.record_count = defaults["record_count"]
        existing.payload = payload
        await existing.save()
    else:
        await ThreatIntelFeedSnapshot.create(
            provider=defaults["provider"],
            feed_name=feed_name,
            feed_kind=defaults["feed_kind"],
            snapshot_id=snapshot_id,
            source_file=source_file,
            source_url=defaults["source_url"],
            record_count=defaults["record_count"],
            payload=payload,
        )
