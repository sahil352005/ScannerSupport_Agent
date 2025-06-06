import os
import pdfplumber
import pandas as pd
from supabase import create_client, Client
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# --- CONFIG ---
SUPABASE_URL = "https://szsxuszodpflthkclrck.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6c3h1c3pvZHBmbHRoa2NscmNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxNzA1NTgsImV4cCI6MjA2Mzc0NjU1OH0.bx6NtC671WSbgB6S0LKW5V4U1tdxR0y0Oa16_nilhIs"
# Set your OpenAI API key here or via environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...your-openai-key...")

INPUT_DIRS = [
    "Input documents",
    os.path.join("Input documents", "Brochures")
]

# --- INIT ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embedder = SentenceTransformer('all-MiniLM-L6-v2')
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

def process_pdf(file_path):
    print(f"Processing PDF: {file_path}")
    docs = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if text.strip():
                for chunk in splitter.split_text(text):
                    docs.append({
                        "content": chunk,
                        "source": os.path.basename(file_path),
                        "page_num": i + 1,
                        "metadata": {}
                    })
    return docs

def process_excel(file_path):
    print(f"Processing Excel: {file_path}")
    docs = []
    df = pd.read_excel(file_path)
    for idx, row in df.iterrows():
        content = " | ".join([str(cell) for cell in row.values if pd.notnull(cell)])
        docs.append({
            "content": content,
            "source": os.path.basename(file_path),
            "page_num": None,
            "metadata": {"row": idx}
        })
    return docs

def embed_and_upload(docs):
    if not docs:
        return
        
    print(f"Embedding and uploading {len(docs)} document chunks...")
    for i, doc in enumerate(docs):
        if i % 10 == 0:  # Progress indicator every 10 chunks
            print(f"Processing chunk {i+1}/{len(docs)}")
            
        try:
            # Since we're clearing the database first, no need to check for existing documents
            embedding = embedder.encode(doc["content"]).tolist()
            data = {
                "content": doc["content"],
                "embedding": embedding,
                "source": doc["source"],
                "page_num": doc["page_num"],
                "metadata": doc["metadata"]
            }
            supabase.table("documents").insert(data).execute()
        except Exception as e:
            print(f"Error uploading document chunk: {str(e)}")
    
    print(f"Successfully uploaded {len(docs)} document chunks.")

def clear_supabase_documents():
    """Clear all documents from the Supabase documents table."""
    print("Clearing existing documents from Supabase...")
    try:
        # Delete all records from the documents table
        supabase.table("documents").delete().execute()
        print("Successfully cleared all documents from Supabase.")
    except Exception as e:
        print(f"Error clearing documents from Supabase: {str(e)}")

def main():
    # Clear existing documents before ingesting new ones
    clear_supabase_documents()
    
    # Process each document in the input directories
    for input_dir in INPUT_DIRS:
        if not os.path.exists(input_dir):
            print(f"Warning: Directory {input_dir} does not exist. Skipping.")
            continue
            
        for fname in os.listdir(input_dir):
            fpath = os.path.join(input_dir, fname)
            if os.path.isfile(fpath):
                print(f"Processing file: {fname}")
                if fname.lower().endswith(".pdf"):
                    docs = process_pdf(fpath)
                    embed_and_upload(docs)
                elif fname.lower().endswith(".xlsx"):
                    docs = process_excel(fpath)
                    embed_and_upload(docs)
                else:
                    print(f"Skipping unsupported file format: {fname}")
            else:
                print(f"Skipping non-file: {fname}")
    
    print("Document ingestion complete!")

if __name__ == "__main__":
    print("Starting document ingestion process...")
    main()
    print("Document ingestion process completed.")
    print("You can now run the Streamlit app to query your documents.")