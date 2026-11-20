---
name: web-scraping-mcp
description: Practical web scraping workflows with no paid APIs and zero third-party Python dependencies. Exposes search_sources, scrape_page, extract_links, extract_json_ld, extract_table, and crawl_site tools.
trigger: /web-scraping-mcp
---

# Web Scraping MCP Server & Skill

Zero-dependency Python stdio MCP server for practical web scraping, crawling, structured data extraction, and web search across all agents and subagents.

## Server Location & Runner

Script: `/Users/malcolm/.gemini/config/scripts/web_scraping_mcp.py`
Registered in: `mcp_config.json` under `"web-scraping-mcp"`

## Tools Exposed

1. **`search_sources`**: Search web via RSS feeds (`query`, `limit: 1-10`).
2. **`scrape_page`**: Fetch URL, clean text HTML tags, extract title and meta description (`url`, `max_chars: 1000-60000`).
3. **`extract_links`**: Extract hyperlinked URLs with optional same-domain filter (`url`, `limit: 1-200`, `same_domain_only: bool`).
4. **`extract_json_ld`**: Extract embedded JSON-LD blocks for schema/structured data (`url`).
5. **`extract_table`**: Extract table rows/headers by index (`url`, `table_index`, `max_rows`).
6. **`crawl_site`**: Breadth-first crawl starting at a seed URL (`seed_url`, `max_pages: 1-20`, `delay_ms`, `max_chars_per_page`).

## Subagent Workflow Integration

- **Default for Static Web Scraping**: All background agents (`a2a_analyst`, `code_coworkers`, `data_fetcher`, `fusion_agent`) use this MCP server as the default tool for non-interactive site parsing.
- **Zero Third-Party Dependencies**: Pure Python standard library implementation (`urllib.request`, `json`, `re`, `html`).

## References

- Inspired by [crawl4ai-skill](https://github.com/brettdavies/crawl4ai-skill)
