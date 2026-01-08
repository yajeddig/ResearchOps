---
title: "UI-TARS-desktop: Open-Source Multimodal AI Agent Stack by ByteDance"
date: 2026-01-08
category: Data_Science
confidence: 0.95
tags: ['AI Agents', 'Multimodal AI', 'Open Source', 'AI Models', 'Agent Infrastructure', 'Software Development', 'Machine Learning', 'ByteDance']
source: "https://github.com/bytedance/UI-TARS-desktop"
type: Article
source_type: GitHub Repository
hash: 200801
---

## 🎯 Relevance
This content is useful for understanding the landscape of open-source AI agent development frameworks, particularly those focusing on multimodal capabilities. For industrial data science, it represents a potential tool (though now sunsetted) for building sophisticated AI-driven automation or decision-making systems. It also provides insights into how large tech companies approach open-sourcing AI infrastructure, and the importance of checking project status (e.g., 'sunsetting') before adoption.

## 📖 Content
This content describes the GitHub repository for `bytedance/UI-TARS-desktop`, an open-source project titled "The Open-Source Multimodal AI Agent Stack: Connecting Cutting-Edge AI Models and Agent Infra." The repository, hosted by ByteDance, has garnered significant attention with 20.8k stars and 2k forks, indicating a notable project in the AI community.

The project aims to provide a framework or stack for developing AI agents that can interact with cutting-edge AI models and leverage agent infrastructure. The term "multimodal" suggests that these AI agents are designed to process and generate information across various modalities (e.g., text, image, audio, video).

Key directories and commit messages reveal aspects of the project's architecture and features:
*   `.changeset`, `.github`, `.husky`, `.vscode`: Standard repository configuration and development tooling.
*   `apps/ui-tars`: Likely contains the main application code for the UI-TARS desktop agent.
*   `docs`: Documentation for the project.
*   `examples`: Illustrative use cases or demonstrations of the agent stack.
*   `images`: Project-related images, possibly for documentation or UI.
*   `infra`: Infrastructure components, suggesting underlying services or frameworks for the agents.
*   `multimodal`: Core components related to multimodal processing within the agents.
*   `packages`: Modular components or libraries used within the stack (e.g., `mcp-browser` for browser DOM context, `agent-ui` for user interface optimization, `pdk` for release management).
*   `patches`: Custom patches or modifications.
*   `rfcs`: Request for Comments, indicating design and architectural discussions.
*   `scripts`: Utility scripts for development, build, or deployment.

Notable commit messages indicate ongoing development and features:
*   `feat(tarko): webui config and render dynamic ui metadata`
*   `feat(ui-tars): sunset UI-TARS-desktop remote operator` (This is a critical commit, indicating a deprecation or end-of-life for a specific feature or the project itself).
*   `fix(cve): react cve`
*   `feat(pdk): support direct release version/tag and improved prerelease`
*   `feat(agent-ui): optimize session status action design`
*   `fix(mcp-browser): browser dom context`
*   `feat(agent-tars): add mcp servers settings` (MCP likely refers to Multi-modal Control Plane or a similar concept for integrating real-world tools).
*   `feat(agent-tars): strict-typed gui agent procotol`
*   `feat(mcp-servers): support mcp offical registry`
*   `feat: add ui-tars GUI Agent SDK`

The project is licensed under the Apache-2.0 license. A significant insight from the commit history is `chore: sunsetting agent tars desktop (#840)` from Jun 29, 2025, which suggests the project is being discontinued or moved to a maintenance-only mode.

## 💡 Key Insights
- UI-TARS-desktop is an open-source multimodal AI agent stack developed by ByteDance.
- It provides infrastructure and tools for connecting cutting-edge AI models to build intelligent agents.
- The project includes components for GUI agent protocols, browser interaction (mcp-browser), and an SDK.
- The project is being 'sunsetted' (discontinued or deprecated), as indicated by recent commit messages.
- It leverages a modular architecture with various packages for different functionalities.

## 📚 References
- bytedance/UI-TARS-desktop, GitHub, https://github.com/bytedance/UI-TARS-desktop *(source)*
- Apache-2.0 license, https://github.com/bytedance/UI-TARS-desktop/blob/main/LICENSE *(cited)*
- agent-tars.com, https://agent-tars.com/ *(cited)*

## 🏷️ Classification
The content describes an open-source stack for building and connecting multimodal AI models and agent infrastructure, which falls directly under the scope of machine learning and AI model application within Data Science.
