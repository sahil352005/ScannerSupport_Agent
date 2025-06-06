# Scanner Support Agent

A powerful AI-powered chatbot that provides instant support for scanner-related queries, troubleshooting, and product comparisons.

![Scanner Support Agent](https://i.imgur.com/placeholder.png)

## 🚀 Features

- **Instant Answers**: Get immediate responses to scanner-related questions
- **Product Comparisons**: Compare different scanner models side by side
- **Troubleshooting Help**: Solve common scanner issues with guided assistance
- **RAG-Powered Knowledge**: Utilizes Retrieval Augmented Generation for accurate responses
- **Responsive UI**: Clean, modern interface with optimized performance

## 📋 Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 📖 Overview

The Scanner Support Agent is a specialized chatbot designed to provide instant support for scanner-related queries. It leverages state-of-the-art language models from Groq and OpenAI, combined with a vector database (Supabase) to deliver accurate, context-aware responses.

The system uses Retrieval Augmented Generation (RAG) to pull relevant information from a knowledge base of scanner documentation, product specifications, and troubleshooting guides. This ensures that responses are factual and based on the latest product information.

## 💻 Technology Stack

- **Frontend**: Streamlit
- **Vector Database**: Supabase with pgvector
- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM Providers**: 
  - Groq (llama3-70b-8192, llama-3.3-70b-versatile, and more)
  - OpenAI (GPT-3.5, GPT-4)
- **Document Processing**: pdfplumber, pandas
- **Language**: Python 3.11+

## 🔧 Installation

### Prerequisites

- Python 3.11 or higher
- Supabase account with pgvector extension enabled
- Groq API key and/or OpenAI API key

### Clone the Repository

```bash
git clone https://github.com/yourusername/scanner-support-agent.git
cd scanner-support-agent
```

### Create a Virtual Environment

```bash
python -m venv venv
```

#### Activate the Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🛠️ Setup

### 1. Supabase Configuration

1. Create a new Supabase project
2. Enable the pgvector extension
3. Run the following SQL in the Supabase SQL Editor:

```sql
-- Create a table to store document chunks and their embeddings
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(384),  -- Dimension for all-MiniLM-L6-v2 model
  source TEXT,
  page_num INTEGER,
  metadata JSONB
);

-- Create a function to match documents by embedding similarity
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding VECTOR(384),
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  id BIGINT,
  content TEXT,
  source TEXT,
  page_num INTEGER,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    documents.source,
    documents.page_num,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
```

### 2. Configuration

Update the `config.py` file with your API keys and Supabase credentials:

```python
# Supabase Configuration
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"

# API Keys
GROQ_API_KEY_DEFAULT = "your-groq-api-key"
OPENAI_API_KEY = "your-openai-api-key"  # Optional
```

### 3. Document Ingestion

Place your scanner documentation PDFs and Excel files in the `Input documents` directory, then run:

```bash
python ingest_documents.py
```

This will:
1. Process all PDF and Excel files
2. Generate embeddings for each document chunk
3. Upload the documents and embeddings to your Supabase database

## 🚀 Usage

### Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

### Using the Chat Interface

1. Select your preferred LLM provider (Groq or OpenAI) in the sidebar
2. Enter your API key if not already configured
3. Choose a model from the dropdown
4. Type your scanner-related question in the chat input
5. Receive an instant, context-aware response

## 📁 Project Structure

```
scanner-support-agent/
├── app.py                  # Main Streamlit application
├── config.py               # Configuration settings
├── embedding_service.py    # Handles vector embeddings and similarity search
├── ingest_documents.py     # Processes and uploads documents to Supabase
├── llm_service.py          # Handles LLM API calls
├── ui_service.py           # UI components and styling
├── requirements.txt        # Python dependencies
├── Input documents/        # Directory for scanner documentation
│   ├── Brochures/          # Scanner brochures and manuals
│   └── ...                 # Other documentation
└── README.md               # Project documentation
```

## ⚙️ Configuration Options

### LLM Models

The application supports various models from Groq and OpenAI. You can configure the available models in `config.py`:

```python
# Model Configuration
GROQ_MODELS = [
    "llama3-70b-8192",
    "llama3-8b-8192",
    "llama-3.3-70b-versatile",
    # Add or remove models as needed
]
OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4"]
```

### Embedding Configuration

```python
# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RESULTS = 5  # Number of similar documents to retrieve
```

### UI Configuration

```python
# UI Configuration
PAGE_TITLE = "Scanner Support Agent"
PAGE_ICON = "🤖"
LAYOUT = "wide"
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) for the web framework
- [Supabase](https://supabase.io/) for the vector database
- [Sentence Transformers](https://www.sbert.net/) for the embedding model
- [Groq](https://groq.com/) and [OpenAI](https://openai.com/) for the language models
- [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF processing
