"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from firecrawl import (
    AgentRequest,
    CancelResponse,
    CrawlParamsPreviewRequest,
    CrawlRequest,
    CreditUsageResponse,
    JobErrorsResponse,
    Link,
    MapRequest,
    MapResponse,
    ScrapeData,
    ScrapeRequest,
    ScrapeResponse,
    SearchRequest,
)


class TestMapModels:
    def test_map_request_minimal(self) -> None:
        req = MapRequest(url="https://example.com")
        assert str(req.url) == "https://example.com/"
        assert req.limit == 5000
        assert req.sitemap == "include"

    def test_map_request_with_options(self) -> None:
        req = MapRequest(
            url="https://example.com",
            search="blog",
            limit=100,
            sitemap="only",
        )
        assert req.search == "blog"
        assert req.limit == 100

    def test_map_request_invalid_url(self) -> None:
        with pytest.raises(ValidationError):
            MapRequest(url="not-a-url")

    def test_map_response(self) -> None:
        resp = MapResponse(
            success=True,
            links=[
                Link(url="https://example.com/page1", title="Page 1"),
                Link(url="https://example.com/page2"),
            ],
        )
        assert resp.success
        assert len(resp.links) == 2
        assert resp.links[0].title == "Page 1"


class TestScrapeModels:
    def test_scrape_request_minimal(self) -> None:
        req = ScrapeRequest(url="https://example.com")
        assert req.formats == ["markdown"]
        assert req.onlyMainContent is True

    def test_scrape_request_with_json(self) -> None:
        req = ScrapeRequest(
            url="https://example.com",
            formats=[
                "markdown",
                {"type": "json", "schema": {"type": "object"}},
            ],
        )
        assert len(req.formats) == 2

    def test_scrape_data(self) -> None:
        data = ScrapeData(
            markdown="# Hello",
            json_data={"key": "value"},
        )
        assert data.markdown == "# Hello"
        assert data.json_data == {"key": "value"}

    def test_scrape_response(self) -> None:
        resp = ScrapeResponse(
            success=True,
            data=ScrapeData(markdown="content"),
        )
        assert resp.success
        assert resp.data.markdown == "content"


class TestSearchModels:
    def test_search_request_minimal(self) -> None:
        req = SearchRequest(query="python")
        assert req.query == "python"
        assert req.limit == 5
        assert req.sources == ["web"]

    def test_search_request_with_options(self) -> None:
        req = SearchRequest(
            query="news",
            limit=10,
            sources=["news"],
            tbs="qdr:d",
        )
        assert req.tbs == "qdr:d"


class TestMiscModels:
    def test_cancel_response_variants(self) -> None:
        crawl_cancel = CancelResponse.model_validate({"status": "cancelled"})
        assert crawl_cancel.status == "cancelled"

        batch_cancel = CancelResponse.model_validate(
            {"success": True, "message": "Batch scrape job successfully cancelled."}
        )
        assert batch_cancel.success is True

    def test_job_errors_response(self) -> None:
        resp = JobErrorsResponse.model_validate(
            {
                "errors": [
                    {
                        "id": "1",
                        "timestamp": "2025-01-01T00:00:00Z",
                        "url": "https://example.com",
                        "error": "boom",
                    }
                ],
                "robotsBlocked": ["https://example.com/robots"],
            }
        )
        assert resp.errors[0].id == "1"

    def test_crawl_params_preview_request(self) -> None:
        req = CrawlParamsPreviewRequest(url="https://example.com", prompt="Crawl blog")
        assert str(req.url) == "https://example.com/"

    def test_credit_usage_response(self) -> None:
        resp = CreditUsageResponse.model_validate(
            {
                "success": True,
                "data": {
                    "remainingCredits": 1,
                    "planCredits": 2,
                    "billingPeriodStart": "2025-01-01T00:00:00Z",
                    "billingPeriodEnd": "2025-01-31T23:59:59Z",
                },
            }
        )
        assert resp.data.remainingCredits == 1


class TestCrawlModels:
    def test_crawl_request_minimal(self) -> None:
        req = CrawlRequest(url="https://example.com")
        assert req.limit == 10000
        assert req.sitemap == "include"

    def test_crawl_request_with_options(self) -> None:
        req = CrawlRequest(
            url="https://example.com",
            prompt="Only crawl blog posts",
            limit=100,
            maxDiscoveryDepth=2,
        )
        assert req.prompt == "Only crawl blog posts"


class TestAgentModels:
    def test_agent_request_minimal(self) -> None:
        req = AgentRequest(prompt="Extract product info")
        assert req.prompt == "Extract product info"
        assert req.urls is None
        assert req.strictConstrainToURLs is False

    def test_agent_request_with_options(self) -> None:
        req = AgentRequest(
            prompt="Find company information",
            urls=["https://example.com"],
            maxCredits=100,
            strictConstrainToURLs=True,
        )
        assert req.maxCredits == 100
        assert req.strictConstrainToURLs is True
