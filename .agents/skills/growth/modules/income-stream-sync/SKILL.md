---
name: income-stream-sync
description: Scrapes GoFundMe profile pages and Gumroad storefront product pages to verify and sync transaction telemetry to the local ledger, triggering real-time UI/UX updates.
---

# Income Stream Sync Workspace Skill

## Overview

The `income-stream-sync` skill automates the scanning, parsing, and syncing of transaction telemetry from GoFundMe and Gumroad campaigns. Scraped data is synced to Next.js API webhook endpoints, updating the local database ledger and broadcasting changes to the client web pages in real-time.

## Capabilities

- **GoFundMe Scanning**: Scrapes the GoFundMe profile page (`https://gofund.me/7047dcec7`) to extract raised totals for active drives.
- **Gumroad Storefront Scanning**: Scrapes Gumroad product pages (Allora App `mzyaak` and Cyberdeck `pkbjbc`), decoding HTML-escaped page data JSON payloads to extract sales counts and prices.
- **Real-Time UI updates**: Sends synced telemetry to Next.js webhooks (`/api/webhook/gofundme` and `/api/webhook/gumroad`), which triggers a Server-Sent Events (SSE) broadcast to all connected clients.
- **Instant UI Refresh**: When the React client receives the SSE event, it pops a success toast notification and calls `fetchDonationTotal()` to fetch and refresh all ledger breakdown tabs and recent transactions lists immediately.
- **Background Daemon**: A background task interval in the database module (`src/lib/db.ts`) runs this scanning process every 3 hours.

## Quick Start

### Manual Execution

To trigger the sub-agent scanner manually, run the Python script from the root of the project:

```bash
python3.11 scripts/income_stream_scanner.py
```

### Next.js API Integration

The Python script communicates with these webhook endpoints:

- **GoFundMe webhook**: `/api/webhook/gofundme`
- **Gumroad webhook**: `/api/webhook/gumroad`

Both webhooks require a Bearer token verification using the `INTERNAL_SYNC_SECRET` environment variable.

## Common Mistakes

- **Next.js Server Offline**: Running the Python script while the local web server is offline will result in connection failures to the webhook endpoints. Ensure the server is running on port `3050` before invoking.
- **Missing Environment Secrets**: Ensure `INTERNAL_SYNC_SECRET` is configured in `.env.secrets` for authorization.
