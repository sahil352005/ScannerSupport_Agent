import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from config import PAGE_TITLE, PAGE_ICON, LAYOUT, INPUT_DIRS
import os

class UIService:
    def __init__(self):
        self.setup_styles()
        
    def format_response(self, text: str) -> str:
        """Format the response text with better styling."""
        # Convert plain text bullet points to HTML lists
        if '- ' in text or '* ' in text:
            lines = text.split('\n')
            in_list = False
            formatted_lines = []
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('- ') or stripped.startswith('* '):
                    if not in_list:
                        formatted_lines.append('<ul>')
                        in_list = True
                    # Convert bullet point to list item
                    formatted_lines.append(f'<li>{stripped[2:]}</li>')
                else:
                    if in_list:
                        formatted_lines.append('</ul>')
                        in_list = False
                    formatted_lines.append(line)
            
            if in_list:
                formatted_lines.append('</ul>')
                
            return '\n'.join(formatted_lines)
        
        # If no special formatting needed, return as is
        return text

    def setup_styles(self):
        """Set up custom CSS styles."""
        st.markdown("""
            <style>
            .stChatMessage {background: #f7f7f8; border-radius: 8px; padding: 10px; margin-bottom: 8px;}
            .user-msg {background: #e6f7ff; font-weight: 500;}
            .bot-msg {background: #f7f7f8;}
            .bot-msg ul, .bot-msg ol {margin-left: 20px; padding-left: 0;}
            .bot-msg li {margin-bottom: 5px;}
            .bot-msg table {width: 100%; border-collapse: collapse; margin: 10px 0;}
            .bot-msg th, .bot-msg td {border: 1px solid #ddd; padding: 8px; text-align: left;}
            .bot-msg th {background-color: #f2f2f2;}
            </style>
        """, unsafe_allow_html=True)

    def setup_sidebar(self, groq_models: List[str], openai_models: List[str], default_groq_key: str):
        """Set up the sidebar with configuration options."""
        st.sidebar.title("🛠️ Settings")
        
        llm_provider = st.sidebar.selectbox("LLM Provider", ["Groq", "OpenAI"])
        
        if llm_provider == "Groq":
            groq_api_key = st.sidebar.text_input("Groq API Key", value=default_groq_key, type="password")
            groq_model = st.sidebar.selectbox("Groq Model", groq_models, index=0)
            return llm_provider, groq_api_key, groq_model, None, None
        else:
            openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
            openai_model = st.sidebar.selectbox("OpenAI Model", openai_models)
            return llm_provider, None, None, openai_api_key, openai_model

    def setup_document_downloads(self):
        """Set up document download buttons in the sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Source Documents**")
        
        # Add a dropdown to select documents instead of loading all at once
        available_docs = []
        for input_dir in INPUT_DIRS:
            if os.path.exists(input_dir):
                for fname in os.listdir(input_dir):
                    fpath = os.path.join(input_dir, fname)
                    if os.path.isfile(fpath):
                        available_docs.append((fname, fpath))
        
        if available_docs:
            # Only show a dropdown if there are documents
            selected_doc = st.sidebar.selectbox(
                "Select a document to download:",
                options=[doc[0] for doc in available_docs],
                index=0
            )
            
            # Only load the selected document
            selected_path = next((doc[1] for doc in available_docs if doc[0] == selected_doc), None)
            if selected_path:
                with open(selected_path, "rb") as f:
                    st.sidebar.download_button(
                        label=f"Download {selected_doc}",
                        data=f,
                        file_name=selected_doc
                    )

    def display_chat_history(self, chat_history: List[Dict[str, Any]]):
        """Display the chat history using Streamlit's native chat components."""
        # Keep track of which messages have been displayed
        if "_displayed_messages" not in st.session_state:
            st.session_state._displayed_messages = set()
            
        for i, msg in enumerate(chat_history):
            # Create a unique identifier for this message
            msg_id = f"{msg['role']}_{i}"
            
            # Only display messages we haven't shown yet
            if msg_id not in st.session_state._displayed_messages:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant"):
                        self.display_response(
                            msg["content"],
                            msg.get("sources", []),
                            msg.get("is_table", False)
                        )
                # Mark this message as displayed
                st.session_state._displayed_messages.add(msg_id)

    def display_response(self, response: str, sources: List[Dict[str, Any]], is_table: bool = False):
        """Display a response from the assistant."""
        if is_table:
            try:
                # Try to parse HTML table
                df = pd.read_html(response)[0]
                st.write(df)
            except Exception:
                # If it's not a valid HTML table, try to format it as a table
                try:
                    # Check if the response contains comparison data
                    lines = response.strip().split('\n')
                    if len(lines) > 1 and ('vs' in response.lower() or 'comparison' in response.lower()):
                        # Create a simple table from the text
                        data = [line.split('|') for line in lines if '|' in line]
                        if data:
                            df = pd.DataFrame(data[1:], columns=data[0])
                            st.write(df)
                        else:
                            # Format with markdown
                            st.markdown(
                                f'<div class="stChatMessage bot-msg">{self.format_response(response)}</div>',
                                unsafe_allow_html=True
                            )
                    else:
                        # Format with markdown
                        st.markdown(
                            f'<div class="stChatMessage bot-msg">{self.format_response(response)}</div>',
                            unsafe_allow_html=True
                        )
                except Exception:
                    # Fall back to basic formatting
                    st.markdown(
                        f'<div class="stChatMessage bot-msg">{self.format_response(response)}</div>',
                        unsafe_allow_html=True
                    )
        else:
            # Format regular responses with better styling
            st.markdown(
                f'<div class="stChatMessage bot-msg">{self.format_response(response)}</div>',
                unsafe_allow_html=True
            )
        
        # Display sources if available
        if sources:
            st.caption(sources) 