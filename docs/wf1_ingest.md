# Workflow 1: Omni-Channel Ingest

**Goal:** Transform any input (URL, Text, Image, PDF) into a structured Markdown intelligence card.

## Trigger
*   **Event:** GitHub Issue created or labeled with `veille`.
*   **Source:** Usually triggered by Make.com (Telegram Bridge), but can be manual.

## Process (`src/wf1_ingest.py`)

1.  **Input Detection:**
    *   Parses the Issue Body to find `IMG_ID:`, `DOC_ID:`, or URLs.
    *   **Images/Docs:** Downloads the file securely using the Telegram Bot API.
    *   **URLs:** Scrapes content using Jina Reader.
    *   **Text:** Uses raw text directly.

2.  **Analysis (Gemini 1.5 Flash):**
    *   Sends the content (Text, Image, or PDF) to Gemini.
    *   **Prompt:** Expert-level analysis focusing on ROI, Innovation, and Feasibility for Process Engineering.
    *   **Output:** JSON containing Title, Category, Summary, Relevance, Tags.

3.  **Categorization:**
    *   Automatically assigns one of the categories defined in `config/categories.json`.

4.  **Storage:**
    *   Generates a Markdown file with Frontmatter metadata.
    *   Saves to `content/{Category}/{Date}_{Hash}_{Title}.md`.

5.  **Notification:**
    *   Commits the file to the repo.
    *   Sends a success notification back to Telegram.
    *   Closes the GitHub Issue.
