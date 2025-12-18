import os
from anthropic import Anthropic

class ClaudeAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-opus-20240229" # Opus for deep reasoning

    def synthesize(self, query, context, perplexity_report, gemini_report):
        print(f"🧠 [Claude Opus] Synthesizing Master Report...")
        
        prompt = f"""
        You are the Chief Technology Officer (CTO) of an industrial R&D center.
        
        OBJECTIVE: Produce a "Master Research Report" on the following topic.
        TOPIC: {query}
        
        SPECIFIC INSTRUCTIONS/CONTEXT:
        {context}
        
        INPUTS:
        1. MARKET/NEWS REPORT (Perplexity):
        {perplexity_report}
        
        2. TECHNICAL/ENGINEERING REPORT (Gemini + Tavily):
        {gemini_report}
        
        STRUCTURE OF THE MASTER REPORT:
        # 📑 Deep Research: {query}
        
        ## 1. Executive Summary
        High-level overview for decision makers. ROI potential.
        
        ## 2. State of the Art (Market & Tech)
        Synthesis of current trends, key players, and technological maturity.
        
        ## 3. Engineering Deep Dive
        Detailed analysis of the process/data challenges.
        - Methodologies
        - Algorithms / Chem. Processes
        - Infrastructure requirements
        
        ## 4. Critical Analysis & Risks
        What could go wrong? What are the bottlenecks?
        
        ## 5. Action Plan
        Recommended next steps (POC, Partnership, Buy vs Build).
        
        TONE: Professional, authoritative, concise, and actionable. No fluff.
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"❌ [Claude] Error: {e}")
            return f"Error during Claude synthesis: {e}"
