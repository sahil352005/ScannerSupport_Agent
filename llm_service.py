import requests
import streamlit as st
import hashlib
from typing import Optional, Dict, Any
from config import SYSTEM_PROMPT

class LLMService:
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions" if provider == "Groq" else "https://api.openai.com/v1/chat/completions"

    def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        # Create a hash of the prompt and model to use as a cache key
        cache_key = f"llm_response_{hashlib.md5((prompt + self.model).encode()).hexdigest()}"
        
        # Check if we have a cached response
        if cache_key in st.session_state:
            return st.session_state[cache_key]
            
        # If not cached, make the API call
        try:
            with st.spinner(f"Generating response with {self.provider}..."):
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1024
                }
                
                # Use a timeout to prevent hanging on slow API calls
                response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()["choices"][0]["message"]["content"]
                
                # Cache the result
                st.session_state[cache_key] = result
                return result
        except requests.exceptions.RequestException as e:
            return f"[{self.provider} API Error] {str(e)}"
        except Exception as e:
            return f"[Error] {str(e)}"

    @staticmethod
    def format_prompt(context: str, query: str, is_comparison: bool = False) -> str:
        """Format the prompt based on the query type."""
        if is_comparison:
            # Special formatting for comparison queries
            prompt = (
                f"Context:\n{context}\n\n"
                f"User Query: {query}\n\n"
                "INSTRUCTIONS:\n"
                "1. Create a comparison table with clear headers and rows.\n"
                "2. Format as an HTML table with <table>, <tr>, <th>, and <td> tags.\n"
                "3. Include key differences and similarities.\n"
                "4. Do NOT include any reasoning, thought process, or explanations.\n"
                "5. Do NOT include any introductory or summary statements.\n"
                "6. Cite sources at the end.\n"
                "7. ONLY output the table and sources."
            )
        else:
            # For regular queries, encourage bullet points for clarity
            prompt = (
                f"Context:\n{context}\n\n"
                f"User Query: {query}\n\n"
                "INSTRUCTIONS:\n"
                "1. Format your response with bullet points (using - or * symbols) for clarity.\n"
                "2. Keep each point brief and concise.\n"
                "3. Do NOT include any reasoning, thought process, or explanation.\n"
                "4. Do NOT include any introductory or summary statements.\n"
                "5. If the answer is a list, use bullet points.\n"
                "6. Cite sources at the end.\n"
                "7. ONLY provide the final answer based on the context."
            )
        return prompt 