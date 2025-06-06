import streamlit as st
import re
from config import (
    GROQ_API_KEY_DEFAULT,
    GROQ_MODELS,
    OPENAI_MODELS,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT
)
from llm_service import LLMService
from embedding_service import EmbeddingService
from ui_service import UIService

# Configure the page - must be the first Streamlit command
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT
)

def filter_llm_output(text):
    # Remove lines that look like reasoning or intro/summary statements
    lines = text.split('\n')
    filtered = []
    for line in lines:
        if re.match(r"^(Okay|Let me|Looking at|I should|So, |First,|Wait,|Based on|In summary|To answer|I don't see|Just the facts|I also need|I'll|\s*$)", line.strip()):
            continue
        filtered.append(line)
    return '\n'.join(filtered).strip()

@st.cache_resource
def create_ui_service():
    return UIService()

def main():
    # Initialize services with caching
    ui = create_ui_service()
    
    # Only initialize embedding service when needed
    if 'embedding_service' not in st.session_state:
        st.session_state.embedding_service = EmbeddingService()
    embedding_service = st.session_state.embedding_service
    
    # Setup sidebar and get LLM configuration
    llm_provider, groq_api_key, groq_model, openai_api_key, openai_model = ui.setup_sidebar(
        GROQ_MODELS,
        OPENAI_MODELS,
        GROQ_API_KEY_DEFAULT
    )
    
    # Setup document downloads
    ui.setup_document_downloads()
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display title - use a placeholder for faster loading
    title_placeholder = st.empty()
    title_placeholder.title(f"🤖 {PAGE_TITLE}")
    
    # Create a fresh container for chat history each time
    chat_container = st.container()
    
    # Display chat history in the container
    with chat_container:
        ui.display_chat_history(st.session_state.chat_history)
    
    # Get user input
    user_input = st.chat_input("Ask me anything about scanners, troubleshooting, or comparisons...")
    
    # Check if there's a pending user input from the previous run
    if "pending_user_input" in st.session_state and st.session_state.pending_user_input:
        user_input = st.session_state.pending_user_input
        st.session_state.pending_user_input = ""
    
    # Process user input
    if user_input:
        # Store the user input in session state to preserve it
        if "current_user_input" not in st.session_state:
            st.session_state.current_user_input = ""
        st.session_state.current_user_input = user_input
        
        # Immediately display the user message
        st.chat_message("user").write(user_input)
        
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Show a spinner while processing to indicate activity
        with st.spinner('Searching for relevant information...'):
            # Generate embeddings and search for relevant documents
            query_embedding = embedding_service.embed_query(user_input)
            results = embedding_service.search_documents(query_embedding)
            
            # Prepare context and check if it's a comparison query
            context = "\n".join([r["content"] for r in results])
            is_comparison = embedding_service.is_comparison_query(user_input)
        
        # Initialize LLM service
        llm = LLMService(
            provider=llm_provider,
            api_key=groq_api_key if llm_provider == "Groq" else openai_api_key,
            model=groq_model if llm_provider == "Groq" else openai_model
        )
        
        # Generate prompt and get response
        prompt = llm.format_prompt(context, user_input, is_comparison)
        response = llm.generate_response(prompt)
        response = filter_llm_output(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "sources": embedding_service.format_sources(results),
            "is_table": is_comparison
        })
        
        # Display the response
        ui.display_response(response, embedding_service.format_sources(results), is_comparison)

if __name__ == "__main__":
    main() 