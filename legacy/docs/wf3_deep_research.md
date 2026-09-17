# Workflow 3: Deep Research (Tri-Force)

## Overview

WF3 is the "Heavy Artillery" of the ResearchOps system. Unlike WF1 (which captures single items) or WF2 (which monitors trends), WF3 is designed to produce **Master-Level Technical Reports** on specific, complex topics.

It employs a **Multi-Agent "Tri-Force" Architecture**, where three distinct AI models work in concert to cover different aspects of a problem before synthesizing a final strategic document.

## 🧠 The Tri-Force Architecture

The system orchestrates three specialized agents:

### 1. Agent Alpha: The Scout (Perplexity Sonar Pro)
*   **Role:** Market Intelligence & News.
*   **Model:** `sonar-pro` (Perplexity).
*   **Focus:** Real-time web search, market trends, key players, recent news, and general context.
*   **Output:** A high-level overview of the "State of the Art" and market dynamics.

### 2. Agent Beta: The Engineer (Gemini 1.5 Pro + Tavily)
*   **Role:** Technical Deep Dive.
*   **Model:** `gemini-1.5-pro` (Google) + `tavily` (Search Tool).
*   **Focus:** Engineering papers, patents, technical specifications, implementation details, code snippets, and scientific principles.
*   **Output:** A dense, technical analysis focusing on "How it works" and "Feasibility".

### 3. Agent Gamma: The Strategist (Claude 3 Opus)
*   **Role:** Synthesis & Strategy.
*   **Model:** `claude-3-opus` (Anthropic).
*   **Focus:** Strategic alignment, ROI analysis, risk assessment, and final report generation.
*   **Action:** It reads the outputs from Alpha and Beta, synthesizes them, and writes the final Master Report in a structured, executive format.

## 🔄 Process Flow

1.  **Trigger:** You create a GitHub Issue with the label `research`.
    *   **Title:** The topic of research (e.g., "Solid State Batteries for EV").
    *   **Body:** Specific questions or context (optional).
2.  **Orchestration:** GitHub Actions triggers `src/wf3_triforce.py`.
3.  **Phase 1 (Parallel-ish):**
    *   Agent Alpha searches the web for market info.
    *   Agent Beta searches for technical info.
4.  **Phase 2 (Synthesis):**
    *   Agent Gamma receives the topic + Alpha's Report + Beta's Report.
    *   Agent Gamma writes the final `Master_Report.md`.
5.  **Delivery:** The report is committed to the `research/` folder in the repository.

## 📝 Output Format

The final report is saved as `research/YYYY-MM-DD_Topic_Name.md` and includes:

*   **Executive Summary:** High-level takeaway for management.
*   **Market Landscape:** Key players, trends, market size (from Alpha).
*   **Technical Deep Dive:** Engineering challenges, solutions, specs (from Beta).
*   **Strategic Analysis:** SWOT, ROI, Feasibility (from Gamma).
*   **References:** Citations from the search results.

## ⚙️ Configuration

The agents are configured in `src/agents/`. You can tweak their system prompts to adjust their "personality" or focus areas.

*   `src/agents/perplexity_agent.py`
*   `src/agents/gemini_agent.py`
*   `src/agents/claude_agent.py`
