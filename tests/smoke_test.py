"""Smoke test for built distributions.

This file is executed in GitHub Actions against the built wheel and sdist.
"""

from __future__ import annotations


def main() -> None:
    import firecrawl
    from firecrawl import (
        AgentRequest,
        CrawlRequest,
        FirecrawlClient,
        MapRequest,
        SearchRequest,
    )

    assert firecrawl.__version__

    _ = FirecrawlClient("fc-test")

    _ = MapRequest(url="https://example.com")
    _ = SearchRequest(query="python")
    _ = CrawlRequest(url="https://example.com")
    _ = AgentRequest(prompt="Extract something")


if __name__ == "__main__":
    main()
