import os
from openai import OpenAI

class PerplexityAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("PERPLEXITY_API_KEY"),
            base_url="https://api.perplexity.ai"
        )
        self.model = "sonar-pro" # Best for research

    def research(self, query, context=""):
        print(f"🔍 [Perplexity] Searching: {query}")
        
        user_content = f"Topic: {query}"
        if context:
            user_content += f"\n\nAdditional Context/Instructions:\n{context}"

        messages = [
            {
                "role": "system",
                "content": "You are an expert industrial researcher. Focus on recent developments, market trends, and key players. Provide concrete data and citations."
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ [Perplexity] Error: {e}")
            return f"Error during Perplexity search: {e}"
