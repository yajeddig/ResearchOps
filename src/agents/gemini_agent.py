import os
import google.generativeai as genai
from tavily import TavilyClient

class GeminiAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def research(self, query, context=""):
        print(f"🔍 [Gemini+Tavily] Investigating: {query}")
        
        search_query = query
        if context:
            search_query += f" {context[:200]}" # Append a bit of context to search query for better relevance

        # 1. Tavily Search for Context
        try:
            search_results = self.tavily.search(
                query=search_query,
                search_depth="advanced",
                max_results=5,
                include_answer=True
            )
            web_context = search_results.get('answer', '') + "\n\n"
            for result in search_results.get('results', []):
                web_context += f"- {result['title']}: {result['content']} ({result['url']})\n"
        except Exception as e:
            print(f"⚠️ [Gemini] Tavily failed: {e}")
            web_context = "Search failed. Relying on internal knowledge."

        # 2. Gemini Analysis
        prompt = f"""
        You are a Senior Process Engineer and Data Scientist.
        
        TASK: Analyze the following query using the provided search context.
        QUERY: {query}
        
        ADDITIONAL CONTEXT/INSTRUCTIONS:
        {context}
        
        CONTEXT FROM WEB SEARCH:
        {web_context}
        
        INSTRUCTIONS:
        - Focus on technical feasibility, engineering challenges, and data requirements.
        - Identify specific technologies, algorithms, or chemical processes involved.
        - Be critical: What are the limitations?
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ [Gemini] Error: {e}")
            return f"Error during Gemini analysis: {e}"
