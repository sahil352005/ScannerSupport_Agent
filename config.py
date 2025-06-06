import os

# Supabase Configuration
SUPABASE_URL = "https://szsxuszodpflthkclrck.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6c3h1c3pvZHBmbHRoa2NscmNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxNzA1NTgsImV4cCI6MjA2Mzc0NjU1OH0.bx6NtC671WSbgB6S0LKW5V4U1tdxR0y0Oa16_nilhIs"

# API Keys
GROQ_API_KEY_DEFAULT = "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"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Model Configuration
GROQ_MODELS = [
    # Production Models
    "llama3-70b-8192",
    "llama3-8b-8192",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "meta-llama/Llama-Guard-4-12B",
    
    # Preview Models
    "deepseek-r1-distill-llama-70b",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "mistral-saba-24b",
    "qwen-qwq-32b",
    "allam-2-7b"
]
OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4"]

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RESULTS = 5

# UI Configuration
PAGE_TITLE = "Scanner Support Agent"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# System Prompts
SYSTEM_PROMPT = """
You are a support agent. Only output the final answer, in a clear, concise, and professional style, based strictly on the provided context.
- Do NOT include any reasoning, thought process, or explanation.
- Do NOT include any introductory or summary statements.
- If the answer is a list, only output the list.
- If the answer is a table, only output the table.
- Always cite sources from the context.
- If information is not in the context, say so clearly.
"""

# File Paths
INPUT_DIRS = ["Input documents", os.path.join("Input documents", "Brochures")] 