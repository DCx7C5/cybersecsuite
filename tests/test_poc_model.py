"""Tests for ProofOfConcept model, PocStatus enum, and seed_poc()."""
from __future__ import annotations

import pytest
from tortoise.context import TortoiseContext

from db.models.enums import PocStatus, Severity


# ── Tortoise in-memory SQLite fixture ────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
async def tortoise_ctx():
    """Initialise Tortoise with SQLite in-memory for the test module."""
    async with TortoiseContext() as ctx:
        await ctx.init(
            db_url="sqlite://:memory:",
            modules={
                "models": [
                    "db.models.scope",
                    "db.models.core",
                    "db.models.cve",
                    "db.models.poc",
                ]
            },
            _enable_global_fallback=True,
        )
        await ctx.generate_schemas(safe=True)
        yield ctx


# ── PocStatus enum ───────────────────────────────────────────────────────────

class TestPocStatusEnum:
    def test_values(self):
        assert PocStatus.UNVERIFIED == "unverified"
        assert PocStatus.VERIFIED == "verified"
        assert PocStatus.WEAPONIZED == "weaponized"
        assert PocStatus.PATCHED == "patched"
        assert PocStatus.DISPUTED == "disputed"

    def test_is_str_subclass(self):
        assert isinstance(PocStatus.WEAPONIZED, str)

    def test_all_members(self):
        members = {m.value for m in PocStatus}
        assert members == {"unverified", "verified", "weaponized", "patched", "disputed"}


# ── ProofOfConcept model ─────────────────────────────────────────────────────

class TestProofOfConceptModel:
    async def test_create_minimal(self):
        from db.models.poc import ProofOfConcept

        poc = await ProofOfConcept.create(
            title="Test PoC",
            poc_url="https://example.com/poc-minimal",
            source="GitHub",
            language="python",
        )
        assert poc.id is not None
        assert poc.title == "Test PoC"
        assert poc.status == PocStatus.UNVERIFIED
        assert poc.is_weaponized is False
        assert poc.requires_auth is False
        assert poc.tags == []
        await poc.delete()

    async def test_create_full(self):
        from db.models.poc import ProofOfConcept

        poc = await ProofOfConcept.create(
            title="EternalBlue PoC",
            poc_url="https://github.com/worawit/MS17-010-full-test",
            source="GitHub",
            language="python",
            status=PocStatus.WEAPONIZED,
            severity=Severity.CRITICAL,
            reliability_score=0.99,
            is_weaponized=True,
            requires_auth=False,
            requires_interaction=False,
            description="SMBv1 exploit basis for WannaCry.",
            affected_versions=["Windows XP", "Windows 7"],
            tags=["smb", "rce", "eternalblue"],
        )
        assert poc.status == PocStatus.WEAPONIZED
        assert poc.severity == Severity.CRITICAL
        assert poc.reliability_score == pytest.approx(0.99)
        assert poc.is_weaponized is True
        assert "smb" in poc.tags
        assert "Windows XP" in poc.affected_versions
        await poc.delete()

    async def test_str_representation(self):
        from db.models.poc import ProofOfConcept

        poc = await ProofOfConcept.create(
            title="MyPoC",
            poc_url="https://example.com/test-str",
        )
        assert "MyPoC" in str(poc)
        await poc.delete()

    async def test_str_falls_back_to_url(self):
        from db.models.poc import ProofOfConcept

        poc = await ProofOfConcept.create(
            title="",
            poc_url="https://example.com/fallback-url",
        )
        assert "https://example.com/fallback-url" in str(poc)
        await poc.delete()

    async def test_default_fields(self):
        from db.models.poc import ProofOfConcept

        poc = await ProofOfConcept.create(poc_url="https://example.com/defaults-test")
        assert poc.title == ""
        assert poc.description == ""
        assert poc.source == ""
        assert poc.language == ""
        assert poc.raw_record == {}
        assert poc.affected_versions == []
        assert poc.tags == []
        assert poc.published_at is None
        assert poc.reliability_score is None
        assert poc.severity is None
        await poc.delete()

    async def test_fk_to_cveintel(self):
        from db.models.poc import ProofOfConcept
        from db.models.cve import CVEIntel

        cve = await CVEIntel.create(
            cve_id="CVE-2021-99999",
            severity="critical",
            cvss_score=10.0,
        )
        poc = await ProofOfConcept.create(
            title="FK Test PoC",
            poc_url="https://example.com/fk-test",
            cve=cve,
        )

        fetched = await ProofOfConcept.get(id=poc.id).prefetch_related("cve")
        assert fetched.cve_id == cve.id
        assert fetched.cve.cve_id == "CVE-2021-99999"

        await poc.delete()
        await cve.delete()

    async def test_fk_nullable(self):
        from db.models.poc import ProofOfConcept

        poc = await ProofOfConcept.create(
            title="No CVE PoC",
            poc_url="https://example.com/no-cve-test",
            cve=None,
        )
        assert poc.cve_id is None
        await poc.delete()

    async def test_filter_by_status(self):
        from db.models.poc import ProofOfConcept

        p1 = await ProofOfConcept.create(
            poc_url="https://example.com/filter-w1", status=PocStatus.WEAPONIZED
        )
        p2 = await ProofOfConcept.create(
            poc_url="https://example.com/filter-u1", status=PocStatus.UNVERIFIED
        )

        weaponized = await ProofOfConcept.filter(
            status=PocStatus.WEAPONIZED, poc_url__in=[p1.poc_url, p2.poc_url]
        )
        assert len(weaponized) == 1
        assert weaponized[0].id == p1.id

        await p1.delete()
        await p2.delete()

    async def test_filter_weaponized_flag(self):
        from db.models.poc import ProofOfConcept

        p1 = await ProofOfConcept.create(poc_url="https://example.com/wf-true", is_weaponized=True)
        p2 = await ProofOfConcept.create(poc_url="https://example.com/wf-false", is_weaponized=False)

        results = await ProofOfConcept.filter(
            is_weaponized=True, poc_url__in=[p1.poc_url, p2.poc_url]
        )
        assert len(results) == 1
        assert results[0].id == p1.id

        await p1.delete()
        await p2.delete()


# ── seed_poc() ───────────────────────────────────────────────────────────────

class TestSeedPoc:
    async def test_seed_creates_records(self):
        from db.models.poc import ProofOfConcept
        from db.models.seeds import seed_poc

        await ProofOfConcept.all().delete()

        result = await seed_poc()
        assert result["total"] == 5
        assert result["created"] == 5
        assert result["skipped"] == 0

        count = await ProofOfConcept.all().count()
        assert count == 5

    async def test_seed_is_idempotent(self):
        """Running seed_poc() twice skips all on second run."""
        from db.models.poc import ProofOfConcept
        from db.models.seeds import seed_poc

        result = await seed_poc()
        assert result["skipped"] == 5
        assert result["created"] == 0

        count = await ProofOfConcept.all().count()
        assert count == 5

    async def test_seed_known_titles(self):
        from db.models.poc import ProofOfConcept

        titles = await ProofOfConcept.all().values_list("title", flat=True)
        assert any("Log4Shell" in t for t in titles)
        assert any("EternalBlue" in t for t in titles)
        assert any("Heartbleed" in t for t in titles)

    async def test_seed_weaponized_pocs(self):
        from db.models.poc import ProofOfConcept

        weaponized = await ProofOfConcept.filter(is_weaponized=True).count()
        assert weaponized >= 2

    async def test_seed_statuses(self):
        from db.models.poc import ProofOfConcept

        weaponized_status = await ProofOfConcept.filter(status=PocStatus.WEAPONIZED).count()
        verified_status = await ProofOfConcept.filter(status=PocStatus.VERIFIED).count()
        assert weaponized_status >= 2
        assert verified_status >= 3

