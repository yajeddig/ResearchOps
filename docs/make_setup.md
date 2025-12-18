# Make.com Setup Guide

This guide explains how to configure the Make.com scenario to bridge Telegram and GitHub.

## Prerequisites
1.  **Telegram Bot:** Create one via @BotFather and get the Token.
2.  **GitHub Account:** Ensure you have access to the `ResearchOps` repo.
3.  **Make.com Account:** Free plan is sufficient.

## Scenario Overview
The scenario listens for new Telegram messages and creates corresponding GitHub Issues.

### Modules

1.  **Telegram Bot - Watch Updates (Webhook)**
    *   Create a webhook and connect your Bot Token.
    *   This is the trigger.

2.  **Flow Control - Router**
    *   Splits the flow into 3 paths: Text, Image, Document.

3.  **Path 1: Text (URLs, Notes)**
    *   **Filter:** `Message: Text` Exists.
    *   **GitHub - Create an Issue:**
        *   Title: `Ingest: Text - {{substring(1.message.text; 0; 50)}}...`
        *   Body: `{{1.message.text}}`
        *   Labels: `veille`

4.  **Path 2: Image (Screenshots, Photos)**
    *   **Filter:** `Message: Photo` Exists.
    *   **GitHub - Create an Issue:**
        *   Title: `Ingest: Image - {{formatDate(now; "YYYY-MM-DD HH:mm")}}`
        *   Body:
            ```
            IMG_ID: {{last(map(1.message.photo; "file_id"))}}
            CAPTION: {{1.message.caption}}
            ```
        *   Labels: `veille`

5.  **Path 3: Document (PDFs)**
    *   **Filter:** `Message: Document` Exists.
    *   **GitHub - Create an Issue:**
        *   Title: `Ingest: {{1.message.document.file_name}}`
        *   Body:
            ```
            DOC_ID: {{1.message.document.file_id}}
            MIME: {{1.message.document.mime_type}}
            ```
        *   Labels: `veille`

## Important Note on File Handling
We pass the **File ID** (`IMG_ID` / `DOC_ID`) to GitHub, not the file itself. The Python script `src/wf1_ingest.py` uses this ID to securely download the file directly from Telegram's servers, bypassing Make.com's file size limits.
