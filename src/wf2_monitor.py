import os
import json
import glob
import re
from datetime import datetime, timedelta
from pathlib import Path
from serpapi import GoogleSearch
from openai import OpenAI
from anthropic import Anthropic
from utils.dedup import load_history, save_history, compute_hash

# Load configurations
CONFIG_PATH = Path(__file__).parent.parent / "config"
monitoring_config = json.load(open(CONFIG_PATH / "monitoring.json"))
categories_config = json.load(open(CONFIG_PATH / "categories.json"))
history = load_history()

perplexity = OpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")


def get_monthly_internal_content():
    """Retrieves and structures content ingested last month by category."""
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    month_prefix = last_month.strftime("%Y%m")
    
    files = glob.glob(f"content/**/{month_prefix}*.md", recursive=True)
    
    # Group by category
    by_category = {}
    for f_path in files:
        category = Path(f_path).parent.name
        if category not in by_category:
            by_category[category] = []
        
        with open(f_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata from frontmatter
        metadata = extract_frontmatter(content)
        filename = os.path.basename(f_path)
        
        by_category[category].append({
            "filename": filename,
            "title": metadata.get("title", filename),
            "source": metadata.get("source", "Unknown"),
            "tags": metadata.get("tags", []),
            "content": content
        })
    
    return by_category, len(files)


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    metadata = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            if value.startswith('[') and value.endswith(']'):
                # Parse list
                value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
            metadata[key] = value
    return metadata

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


def search_category_news(category_name: str, description: str) -> dict:
    """Search recent news/developments for a category using Perplexity."""
    
    # Build a focused query based on category
    query = f"""Find the most significant developments, tools, papers, or news from the last 3 months related to: {description}
    
Return ONLY factual information with sources. Format:
- Development/Tool name: Brief description (Source: URL or publication name)

If no recent developments found, say "No significant recent developments found."
Do NOT make up information or sources."""

    try:
        response = perplexity.chat.completions.create(
            model="sonar",
            messages=[{"role": "user", "content": query}],
        )
        content = response.choices[0].message.content
        
        # Check if it's a "no info" response
        if "cannot" in content.lower() or "don't have access" in content.lower():
            return {"content": "", "has_data": False}
        
        return {"content": content, "has_data": True}
    except Exception as e:
        print(f"[WF2] Perplexity failed for {category_name}: {e}")
        return {"content": "", "has_data": False}


def build_structured_context(internal_by_category: dict, all_papers: dict, all_news: dict) -> str:
    """Build a well-structured context for Claude."""
    
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    month_name = last_month.strftime("%B %Y")
    
    context = f"# 📊 Data for Monthly Report - {month_name}\n\n"
    
    # Section 1: Internal captures by category
    context += "## SECTION A: INTERNAL KNOWLEDGE BASE (My captures)\n\n"
    
    if not internal_by_category:
        context += "*No captures this month.*\n\n"
    else:
        for category, docs in internal_by_category.items():
            cat_desc = categories_config["categories"].get(category, {}).get("description", "")
            context += f"### Category: {category}\n"
            context += f"*{cat_desc}*\n\n"
            
            for i, doc in enumerate(docs, 1):
                context += f"**[I{i}] {doc['title']}**\n"
                context += f"- Source: {doc['source']}\n"
                context += f"- File: `{doc['filename']}`\n"
                context += f"- Tags: {', '.join(doc['tags']) if isinstance(doc['tags'], list) else doc['tags']}\n"
                # Include content (truncated if too long)
                content_preview = doc['content'][:3000] + "..." if len(doc['content']) > 3000 else doc['content']
                context += f"\n{content_preview}\n\n"
                context += "---\n\n"
    
    # Section 2: External academic papers
    context += "## SECTION B: ACADEMIC PAPERS (Google Scholar)\n\n"
    
    has_papers = False
    for topic_id, papers in all_papers.items():
        if papers:
            has_papers = True
            context += f"### Topic: {topic_id}\n\n"
            for i, p in enumerate(papers, 1):
                context += f"**[P{i}] {p['title']}**\n"
                context += f"- Authors: {p['authors']}\n"
                context += f"- Citations: {p['citations']}\n"
                context += f"- URL: {p['link']}\n"
                context += f"- Abstract: {p['snippet']}\n\n"
    
    if not has_papers:
        context += "*No new papers found this month.*\n\n"
    
    # Section 3: External news by category
    context += "## SECTION C: INDUSTRY NEWS & DEVELOPMENTS\n\n"
    
    has_news = False
    for category, news_data in all_news.items():
        if news_data.get("has_data") and news_data.get("content"):
            has_news = True
            context += f"### {category}\n\n"
            context += f"{news_data['content']}\n\n"
    
    if not has_news:
        context += "*No significant industry news found this month.*\n\n"
    
    return context


def synthesize_report(context: str, total_docs: int) -> str:
    """Generate the final report using Claude with strict formatting."""
    
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    month_name = last_month.strftime("%B %Y")
    
    prompt = f"""Tu es un ingénieur R&D senior rédigeant un rapport de veille mensuel de qualité scientifique.

RÈGLES STRICTES:
1. CITATIONS OBLIGATOIRES: Chaque affirmation doit citer sa source avec [I1], [P2], etc.
2. NE PAS INVENTER: Si tu n'as pas d'information, dis-le clairement. Pas d'hallucination.
3. LANGUE: Rédige en français
4. FORMAT: Respecte EXACTEMENT la structure ci-dessous

LÉGENDE DES RÉFÉRENCES:
- [I1], [I2]... = Documents internes (mes captures)
- [P1], [P2]... = Papers académiques (Google Scholar)  
- [N1], [N2]... = News/développements externes

---

# 🔬 Rapport de Veille Mensuel — {month_name}

**Documents internes analysés:** {total_docs}  
**Date de génération:** {datetime.now().strftime("%Y-%m-%d")}

---

## 📋 Synthèse Exécutive

Résumé en 3-5 points clés des apprentissages du mois. Chaque point cite ses sources.

---

## 🧠 Base de Connaissances Interne

Pour chaque thématique identifiée dans mes captures:

### [Thématique 1]

**Connaissances mobilisables:**
- Point clé avec citation [I1]
- Point clé avec citation [I2]

**Outils & Ressources identifiés:**
- Outil/lib/framework mentionné [Ix]

**Applications potentielles:**
- Comment utiliser ces connaissances

*(Répéter pour chaque thématique)*

---

## 🌍 Veille Externe

### Frontière Académique

Pour chaque paper pertinent:
- **Titre** — Auteurs (Année)
- Contribution clé (1-2 phrases)
- Pertinence pour mes travaux
- Référence: [Px]

### Actualités Industrielles

- Développement/annonce avec source [Nx]

---

## 🔗 Analyse Croisée

- Connexions entre captures internes et tendances externes
- Lacunes identifiées dans ma veille
- Confirmations ou contradictions

---

## 💡 Recommandations Actionnables

| Priorité | Action | Justification | Refs |
|----------|--------|---------------|------|
| 🔴 Haute | Action 1 | Pourquoi | [I1, P2] |
| 🟡 Moyenne | Action 2 | Pourquoi | [I3] |
| 🟢 Basse | Action 3 | Pourquoi | [N1] |

---

## 📚 Bibliographie

### Sources Internes
[I1] Titre, filename
[I2] ...

### Papers Académiques  
[P1] Auteurs, "Titre", Source, Année, URL
[P2] ...

### Sources Externes
[N1] Titre, Source, URL
[N2] ...

---

DONNÉES À ANALYSER:

{context}
"""

    response = claude.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

def main():
    """Main workflow: gather data and generate monthly report."""
    
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    month_name = last_month.strftime("%B %Y")
    print(f"[WF2] 📅 Generating report for: {month_name}")
    
    # 1. Get Internal Knowledge (grouped by category)
    print(f"[WF2] 📚 Reading internal captures...")
    internal_by_category, total_docs = get_monthly_internal_content()
    print(f"[WF2] ✓ Found {total_docs} documents in {len(internal_by_category)} categories")
    
    for cat, docs in internal_by_category.items():
        print(f"    - {cat}: {len(docs)} docs")
    
    # 2. Get External Academic Papers (from monitoring.json topics)
    all_papers = {}
    print(f"[WF2] 🎓 Searching academic papers...")
    for topic in monitoring_config["topics"]:
        print(f"    - Topic: {topic['name']}")
        papers = search_scholar_new(topic)
        all_papers[topic["id"]] = papers
        print(f"      Found {len(papers)} new papers")
    
    # 3. Get External News (based on active categories with content)
    all_news = {}
    print(f"[WF2] 📰 Searching industry news...")
    
    # Only search news for categories where we have internal content
    categories_to_search = list(internal_by_category.keys())
    if not categories_to_search:
        # Fallback: search main categories
        categories_to_search = ["Data_Science", "Process_Engineering", "Industrial_Systems"]
    
    for category in categories_to_search:
        if category == "_Inbox":
            continue
        cat_config = categories_config["categories"].get(category, {})
        description = cat_config.get("description", category)
        print(f"    - Category: {category}")
        news = search_category_news(category, description)
        all_news[category] = news
    
    # 4. Build structured context
    print(f"[WF2] 🔧 Building context...")
    context = build_structured_context(internal_by_category, all_papers, all_news)
    
    # 5. Generate report
    print(f"[WF2] 🤖 Generating report with Claude...")
    report = synthesize_report(context, total_docs)
    
    # 6. Save
    month_str = datetime.now().strftime("%Y-%m")
    output_path = f"reports/{datetime.now().year}/{month_str}_Monitor.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    # 7. Persist history
    save_history(history)
    
    # 8. Commit
    from utils.git_ops import safe_commit
    safe_commit(
        files=[output_path, "data/history.json"],
        message=f"WF2: Monthly monitor {month_str}"
    )
    
    print(f"[WF2] ✅ Report saved: {output_path}")
    print(f"[WF2] 📊 Stats: {total_docs} internal docs, {sum(len(p) for p in all_papers.values())} papers")


if __name__ == "__main__":
    main()
