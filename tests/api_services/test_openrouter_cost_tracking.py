"""Tests for OpenRouter cost tracking and attribution.

Tests cover:
- Generation ID capture from response headers
- Cost attribution fetching
- Event emission
- Failure handling without breaking response
"""

from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

import pytest

from css.api_services.openrouter.cost_tracking import (
    capture_generation_id,
    fetch_cost_attribution,
    emit_cost_tracking_event,
)


class TestCaptureGenerationId:
    """Test generation ID capture from response headers."""

    def test_capture_from_x_request_id(self):
        """Capture generation ID from x-request-id header."""
        headers = {"x-request-id": "gen-12345"}
        gen_id = capture_generation_id(headers)
        assert gen_id == "gen-12345"

    def test_capture_from_request_id(self):
        """Capture from request-id header."""
        headers = {"request-id": "req-67890"}
        gen_id = capture_generation_id(headers)
        assert gen_id == "req-67890"

    def test_capture_from_generation_id(self):
        """Capture from generation-id header."""
        headers = {"generation-id": "gid-abc"}
        gen_id = capture_generation_id(headers)
        assert gen_id == "gid-abc"

    def test_capture_prefers_x_request_id(self):
        """Prefer x-request-id over other headers."""
        headers = {
            "x-request-id": "x-req-1",
            "request-id": "req-2",
        }
        gen_id = capture_generation_id(headers)
        assert gen_id == "x-req-1"

    def test_capture_missing_header(self):
        """Return None when no generation ID header present."""
        headers = {"content-type": "application/json"}
        gen_id = capture_generation_id(headers)
        assert gen_id is None

    def test_capture_empty_headers(self):
        """Return None for empty headers."""
        gen_id = capture_generation_id({})
        assert gen_id is None


class TestFetchCostAttribution:
    """Test cost attribution fetching from OpenRouter API."""

    @pytest.mark.asyncio
    async def test_fetch_success(self):
        """Fetch cost attribution successfully."""
        from unittest.mock import AsyncMock, MagicMock, patch
        import aiohttp

        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200

        async def mock_json():
            return {
                "total_cost": 0.0125,
                "model": "openai/gpt-4-turbo",
            }

        mock_response.json = mock_json

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.get = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.get.return_value.__aexit__.return_value = None

        with patch("aiohttp.ClientSession") as mock_cls:
            mock_cls.return_value.__aenter__.return_value = mock_session
            mock_cls.return_value.__aexit__.return_value = None

            result = await fetch_cost_attribution(
                "gen-123",
                "key-abc",
                "gpt-4-turbo",
            )

            assert result is not None
            assert result["cost_usd"] == 0.0125
            assert result["actual_provider"] == "openai/gpt-4-turbo"
            assert result["generation_id"] == "gen-123"

    @pytest.mark.asyncio
    async def test_fetch_no_generation_id(self):
        """Return None when no generation ID provided."""
        result = await fetch_cost_attribution(None, "key", "model")
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_api_error(self):
        """Return None on API error."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_session.get.side_effect = Exception("Connection error")

            result = await fetch_cost_attribution(
                "gen-123",
                "key-abc",
                "gpt-4",
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_timeout(self):
        """Return None on timeout."""
        import asyncio

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_session.get.side_effect = asyncio.TimeoutError()

            result = await fetch_cost_attribution(
                "gen-123",
                "key-abc",
                "gpt-4",
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_http_error(self):
        """Return None on HTTP error status."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            mock_response = MagicMock()
            mock_response.status = 404
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_session.get.return_value = mock_response

            result = await fetch_cost_attribution(
                "gen-123",
                "key-abc",
                "gpt-4",
            )

            assert result is None


class TestEmitCostTrackingEvent:
    """Test cost tracking event emission."""

    @pytest.mark.asyncio
    async def test_emit_with_generation_id(self):
        """Emit event when generation ID present."""
        with patch("css.api_services.openrouter.cost_tracking.asyncio.create_task") as mock_task:
            await emit_cost_tracking_event(
                "gen-123",
                "gpt-4",
                "key-abc",
                0.0125,
                "openai/gpt-4-turbo",
            )

            # Should create async task
            mock_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_emit_no_generation_id(self):
        """Skip event emission when no generation ID."""
        with patch("css.api_services.openrouter.cost_tracking.asyncio.create_task") as mock_task:
            await emit_cost_tracking_event(
                None,
                "gpt-4",
                "key-abc",
            )

            # Should not create task
            mock_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_emit_no_event_loop(self):
        """Handle case where no event loop is running."""
        with patch("css.api_services.openrouter.cost_tracking.asyncio.create_task") as mock_task:
            mock_task.side_effect = RuntimeError("No running event loop")

            # Should not raise exception
            await emit_cost_tracking_event(
                "gen-123",
                "gpt-4",
                "key-abc",
            )


class TestCostTrackingIntegration:
    """Integration tests for cost tracking workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_with_direct_cost(self):
        """Full workflow when cost is in response."""
        with patch("css.api_services.openrouter.cost_tracking.emit_event") as mock_emit:
            from css.api_services.openrouter.cost_tracking import _emit_cost_event_async

            await _emit_cost_event_async(
                "gen-123",
                "gpt-4",
                "key-abc",
                cost_usd=0.015,
                actual_provider="openai/gpt-4-turbo",
            )

            mock_emit.assert_called_once()
            call_args = mock_emit.call_args
            assert call_args[0][0] == "openrouter.generation.cost_tracked"

    @pytest.mark.asyncio
    async def test_full_workflow_with_attribution_fetch(self):
        """Full workflow when cost must be fetched."""
        with patch("css.api_services.openrouter.cost_tracking.fetch_cost_attribution") as mock_fetch:
            with patch("css.api_services.openrouter.cost_tracking.emit_event") as mock_emit:
                from css.api_services.openrouter.cost_tracking import _emit_cost_event_async

                mock_fetch.return_value = {
                    "cost_usd": 0.02,
                    "actual_provider": "openai/gpt-4",
                    "generation_id": "gen-123",
                }

                await _emit_cost_event_async(
                    "gen-123",
                    "gpt-4",
                    "key-abc",
                )

                mock_fetch.assert_called_once()
                mock_emit.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_with_fetch_failure(self):
        """Emit failure event when attribution fetch fails."""
        with patch("css.api_services.openrouter.cost_tracking.fetch_cost_attribution") as mock_fetch:
            with patch("css.api_services.openrouter.cost_tracking.emit_event") as mock_emit:
                from css.api_services.openrouter.cost_tracking import _emit_cost_event_async

                mock_fetch.return_value = None

                await _emit_cost_event_async(
                    "gen-123",
                    "gpt-4",
                    "key-abc",
                )

                # Should emit failure event
                call_args = mock_emit.call_args
                assert call_args[0][0] == "openrouter.generation.cost_tracking_failed"
