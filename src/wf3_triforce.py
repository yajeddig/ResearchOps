import os
import re
from datetime import datetime
from agents.perplexity_agent import PerplexityAgent
from agents.gemini_agent import GeminiAgent
from agents.claude_agent import ClaudeAgent
from utils.git_ops import safe_commit
from utils.notify import telegram_notify

def main():
    issue_title = os.getenv("ISSUE_TITLE")
    issue_body = os.getenv("ISSUE_BODY")
    issue_number = os.getenv("ISSUE_NUMBER")
    
    # Extract query from title (remove "Research: " prefix if present)
    topic = issue_title.replace("Research: ", "").strip()
    context = issue_body if issue_body else ""
    
    full_query = topic
    if context:
        full_query += f"\n\nContext: {context}"
        
    print(f"🚀 [WF3] Starting Deep Research on: {topic}")
    if context:
        print(f"📝 Context provided: {context[:100]}...")
        
    telegram_notify(f"🚀 Starting Deep Research: {topic}", "INFO")

    # 1. Initialize Agents
    agent_perplexity = PerplexityAgent()
    agent_gemini = GeminiAgent()
    agent_claude = ClaudeAgent()

    # 2. Parallel Execution (Simulated here sequentially for simplicity, but conceptually parallel)
    # In a more advanced setup, we could use asyncio.gather
    
    print("--- Phase 1: Information Gathering ---")
    report_perplexity = agent_perplexity.research(topic, context)
    report_gemini = agent_gemini.research(topic, context)

    # 3. Synthesis
    print("--- Phase 2: Strategic Synthesis ---")
    master_report = agent_claude.synthesize(topic, context, report_perplexity, report_gemini)

    # 4. Save Output
    safe_title = re.sub(r'[^a-zA-Z0-9]', '_', topic[:30])
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"research/{date_str}_Deep_{safe_title}.md"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(master_report)
        
    print(f"✅ [WF3] Report saved: {filename}")

    # 5. Commit & Notify
    safe_commit(
        files=[filename],
        message=f"WF3: Deep Research - {topic[:50]}"
    )

    telegram_notify(f"✅ Deep Research Complete!\nTopic: {topic}\nFile: {filename}", "SUCCESS")

if __name__ == "__main__":
    main()
