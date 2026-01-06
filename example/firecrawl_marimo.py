"""Firecrawl worked examples (Marimo).

Run:
    uv sync --extra dev
    export FIRECRAWL_API_KEY="fc-..."
    uv run marimo edit example/firecrawl_marimo.py

Notes:
    These examples call the live Firecrawl API and will consume credits.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import marimo as mo

from firecrawl import (
    CrawlRequest,
    FirecrawlClient,
    MapRequest,
    ScrapeRequest,
    SearchRequest,
    load_api_key,
)

app = mo.App(width="full")

TARGET_URL = "https://www.bhp.com/"


async def _with_client(fn: Callable[[FirecrawlClient], Awaitable[object]]) -> object:
    api_key = load_api_key()
    async with FirecrawlClient(api_key) as client:
        return await fn(client)


def _run(fn: Callable[[FirecrawlClient], Awaitable[object]]) -> object:
    return asyncio.run(_with_client(fn))


@app.cell
def _():
    mo.md(
        f"""
        # Firecrawl examples (Marimo)

        Target URL: `{TARGET_URL}`

        Requires `FIRECRAWL_API_KEY` (or `~/.secrets/firecrawl.key`).
        """
    )
    return


@app.cell
def _():
    mo.md("## 1) Map")

    def do_map(client: FirecrawlClient) -> Awaitable[object]:
        return client.map(MapRequest(url=TARGET_URL, limit=50))

    result = _run(do_map)
    return result


@app.cell
def _(result):
    links = result.links
    mo.md(f"Found **{len(links)}** links (showing first 20).")
    mo.ui.table(
        [
            {
                "url": link.url,
                "title": link.title,
                "description": link.description,
            }
            for link in links[:20]
        ]
    )
    return


@app.cell
def _():
    mo.md("## 2) Scrape")

    def do_scrape(client: FirecrawlClient) -> Awaitable[object]:
        return client.scrape(
            ScrapeRequest(
                url=TARGET_URL,
                formats=["markdown"],
                onlyMainContent=True,
                maxAge=86_400_000,
            )
        )

    result = _run(do_scrape)
    return result


@app.cell
def _(result):
    data = result.data
    text = data.markdown or data.html or "(no content)"
    mo.md("### Excerpt")
    mo.ui.code(text[:4000], language="markdown")
    return


@app.cell
def _():
    mo.md("## 3) Search")

    def do_search(client: FirecrawlClient) -> Awaitable[object]:
        return client.search(
            SearchRequest(
                query="bhp annual report",
                sources=["web"],
                limit=5,
            )
        )

    result = _run(do_search)
    return result


@app.cell
def _(result):
    web = result.data.web or []
    mo.ui.table(
        [
            {
                "title": item.title,
                "url": item.url,
                "description": item.description,
            }
            for item in web
        ]
    )
    return


@app.cell
def _():
    mo.md("## 4) Crawl (constrained)")
    mo.md(
        """
        This starts a crawl and polls for completion.

        To limit credits usage, this example uses a low `limit` and shallow depth.
        """
    )

    async def do_crawl(client: FirecrawlClient) -> object:
        job = await client.crawl(
            CrawlRequest(
                url=TARGET_URL,
                limit=25,
                maxDiscoveryDepth=1,
                allowExternalLinks=False,
                allowSubdomains=False,
            )
        )

        for _ in range(60):
            status = await client.get_crawl_status(job.id)
            if status.status in {"completed", "failed", "cancelled"}:
                return status
            await asyncio.sleep(3)

        raise TimeoutError("Crawl did not finish within ~3 minutes")

    result = _run(do_crawl)
    return result


@app.cell
def _(result):
    mo.md(f"Status: **{result.status}**")
    data = result.data or []
    rows = []
    for item in data[:20]:
        meta = (item or {}).get("metadata") or {}
        rows.append(
            {
                "sourceURL": meta.get("sourceURL"),
                "title": meta.get("title"),
                "statusCode": meta.get("statusCode"),
            }
        )
    mo.ui.table(rows)
    return


if __name__ == "__main__":
    app.run()
