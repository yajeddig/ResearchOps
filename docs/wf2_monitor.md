# Workflow 2: Strategic Monitor

**Goal:** Generate a monthly intelligence report combining internal captures and external signals.

## Trigger
*   **Schedule:** 1st of every month at 06:00 UTC.
*   **Manual:** Can be triggered via "Run Workflow" in GitHub Actions.

## Process (`src/wf2_monitor.py`)

1.  **Internal Knowledge Retrieval:**
    *   Scans the `content/` directory for all Markdown files created in the previous month.
    *   Aggregates this "Field Intelligence" to form the "Second Brain" context.

2.  **External Signal Search:**
    *   **Academic:** Queries SerpAPI (Google Scholar) for new papers (current year) matching topics in `config/monitoring.json`.
    *   **Industrial:** Queries Perplexity for major news/developments in the last 3 months.
    *   **Deduplication:** Checks `data/history.json` to ensure only *new* external content is reported.

3.  **Hybrid Synthesis (Claude 3.5 Sonnet):**
    *   Injects both Internal and External contexts into Claude.
    *   **Prompt:** Asks for a strategic report highlighting alignment/gaps between field observations and global trends.

4.  **Reporting:**
    *   Generates a Markdown report in `reports/{Year}/{Month}_Monitor.md`.
    *   Commits the report and updates the history file.
