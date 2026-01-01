import os
import json
import glob
from datetime import datetime, timedelta
from serpapi import GoogleSearch
from openai import OpenAI
from anthropic import Anthropic
from utils.dedup import load_history, save_history, compute_hash

config = json.load(open("config/monitoring.json"))
history = load_history()

perplexity = OpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")

def get_monthly_internal_content():
    """Retrieves content ingested last month"""
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    month_prefix = last_month.strftime("%Y%m") # ex: 202501
    
    files = glob.glob(f"content/**/{month_prefix}*.md", recursive=True)
    internal_data = []
    
    # Low Volume: 10-20 docs/month. Inject full content.
    for f_path in files:
        with open(f_path, 'r') as f:
            content = f.read()
            internal_data.append(f"FILE: {os.path.basename(f_path)}\nCONTENT:\n{content}")
            
    return "\n---\n".join(internal_data)

def search_scholar_new(topic_config):
    """SerpAPI with new content filter"""
    params = {
        "engine": "google_scholar",
        "q": " OR ".join(topic_config["keywords_academic"]),
        "as_ylo": datetime.now().year,
        "num": 10,
        "api_key": os.getenv("SERPAPI_KEY")
    }
    
    try:
        results = GoogleSearch(params).get_dict()
    except Exception as e:
        print(f"[WF2] SerpAPI failed: {e}")
        return []
    
    papers = []
    for r in results.get("organic_results", []):
        link = r.get("link", "")
        if not link: continue
        
        link_hash = compute_hash(link)
        
        # Skip if already seen
        if link_hash in history:
            continue
        
        papers.append({
            "title": r["title"],
            "authors": r.get("publication_info", {}).get("summary", ""),
            "link": link,
            "hash": link_hash,
            "snippet": r.get("snippet"),
            "citations": r.get("inline_links", {}).get("cited_by", {}).get("total", 0)
        })
        
        # Add to history
        history[link_hash] = {
            "url": link,
            "type": "paper",
            "added": datetime.now().isoformat()
        }
    
    return papers[:topic_config["paper_limit"]]

def search_news_new(topic_config):
    """Perplexity with 3-month filter"""
    query = f"Major developments in last 3 months: {' OR '.join(topic_config['keywords_news'])}"
    
    try:
        response = perplexity.chat.completions.create(
            model="sonar",
            messages=[{"role": "user", "content": query}],
        )
        
        content = response.choices[0].message.content
        
        return {"content": content, "new_sources": 1} 
    except Exception as e:
        print(f"[WF2] Perplexity failed: {e}")
        return {"content": "", "new_sources": 0}

def synthesize_delta_report(all_papers, all_news, internal_content):
    """Claude Sonnet for hybrid monthly report"""
    
    context = "# New Content This Month\n\n"
    
    # Add Internal Content
    context += f"## 🧠 My Watch (Captured Content)\n{internal_content}\n\n"
    
    # Add External Content
    for topic_id, papers in all_papers.items():
        if papers:
            context += f"## {topic_id}\n### Papers\n"
            for p in papers:
                context += f"- **{p['title']}** ({p['citations']} cit.)\n  {p['snippet']}\n"
            
    for topic_id, news in all_news.items():
        if news["new_sources"] > 0:
            context += f"### News ({topic_id})\n{news['content']}\n"
    
    prompt = f"""Write the monthly strategic intelligence report for the R&D Manager.

SOURCES:
1. INTERNAL: What I manually captured (screenshots, notes, pdfs).
2. EXTERNAL: What agents found on web/scholar.

STRUCTURE:
# 🔬 Monthly Intelligence - {datetime.now():%B %Y}

## �� Executive Summary
- Alignment between my field intelligence and global trends.
- Critical attention points.

## 🧠 My "Second Brain" (Capture Analysis)
Thematic synthesis of my own captures this month. What caught my attention?

## 🌍 External Radar (New Developments)
- Academic (Key Papers)
- Industrial (News & Competition)

## 💡 Opportunities & Actions
- Project ideas / POCs
- Technologies to test

DATA:
{context}
"""

    response = claude.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

def main():
    all_papers = {}
    all_news = {}
    
    # 1. Get Internal Knowledge
    print(f"[WF2] Reading internal content...")
    internal_content = get_monthly_internal_content()
    
    # 2. Get External Knowledge
    for topic in config["topics"]:
        print(f"[WF2] Processing: {topic['name']}")
        
        papers = search_scholar_new(topic)
        all_papers[topic["id"]] = papers
        
        news = search_news_new(topic)
        all_news[topic["id"]] = news
    
    # 3. Generate report
    print(f"[WF2] Synthesizing report...")
    report = synthesize_delta_report(all_papers, all_news, internal_content)
    
    # Save
    month_str = datetime.now().strftime("%Y-%m")
    output_path = f"reports/{datetime.now().year}/{month_str}_Monitor.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    # Persist history
    save_history(history)
    
    # Commit
    from utils.git_ops import safe_commit
    safe_commit(
        files=[output_path, "data/history.json"],
        message=f"WF2: Monthly monitor {month_str}"
    )
    
    print(f"[WF2] ✅ Report: {output_path}")

if __name__ == "__main__":
    main()
