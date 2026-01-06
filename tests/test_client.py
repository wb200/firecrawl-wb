"""Tests for FirecrawlClient."""

import pytest

from firecrawl import FirecrawlClient, FirecrawlError


class TestFirecrawlClient:
    def test_client_requires_context_manager(self) -> None:
        client = FirecrawlClient("fc-test")
        assert client._client is None

    @pytest.mark.asyncio
    async def test_client_context_manager(self) -> None:
        async with FirecrawlClient("fc-test") as client:
            assert client._client is not None
        assert client._client is None or client._client.is_closed

    @pytest.mark.asyncio
    async def test_client_not_initialized_error(self) -> None:
        client = FirecrawlClient("fc-test")
        with pytest.raises(FirecrawlError, match="not initialized"):
            from firecrawl import MapRequest

            await client.map(MapRequest(url="https://example.com"))
