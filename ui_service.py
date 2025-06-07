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
            /* Fixed Footer HTML injected at the top of the body for global positioning */
            html body::after {
                content: '';
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 50px; /* Adjust height as needed for your footer content */
                background-color: #fff; /* White Areas */
                border-top: 1px solid #e9ecef; /* Primary Borders */
                box-shadow: 0 -2px 4px rgba(0,0,0,0.04); /* Subtle shadow */
                z-index: 1000; /* Ensure it's on top */
            }
            html body::before {
                content: '© 2025 S3K Technologies | All rights reserved';
                position: fixed;
                bottom: 18px; /* Adjust to vertically center the text */
                left: 0;
                width: 100%;
                color: #495057; /* Primary Text */
                text-align: center;
                z-index: 1001; /* Ensure text is above the footer background */
                font-size: 0.9em;
            }

            /* General body and layout improvements */
            body {
                color: #495057; /* Primary Text */
                background-color: #f8f9fa; /* Main Background */
                font-family: sans-serif;
            }
            
            /* Ensure content doesn't get hidden by fixed footer */
            .main .block-container {
                padding-bottom: 80px; /* Increased padding to account for fixed footer */
            }
            
            /* Sidebar styling */
            .stSidebar > div:first-child {
                background-color: #f8f9fa; /* Sidebar Background */
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05); /* Subtle shadow for cards */
            }
            
            /* Header styling */
            .stApp > header {
                background-color: #fff; /* White Areas */
                padding: 10px 20px;
                border-bottom: 2px solid #e9ecef; /* Primary Borders */
                box-shadow: 0 2px 4px rgba(0,0,0,0.04); /* Header Shadow */
                position: sticky; /* Make header sticky */
                top: 0; /* Stick to the top */
                z-index: 999; /* Ensure it's on top of other content */
            }
            
            /* Custom header content alignment */
            .stApp > header .st-emotion-cache-18ni7ap.e1fqkh3o1.css-18ni7ap.e1fqkh3o1 {
                width: 100%;
                display: flex;
                justify-content: flex-start; /* Align logo and title to the left */
                align-items: center;
            }
            
            .stApp > header .st-emotion-cache-18ni7ap.e1fqkh3o1.css-18ni7ap.e1fqkh3o1 > div:first-child {
                flex-grow: 0; /* No longer need this to grow, keep content together */
            }

            /* Chat message styling */
            .stChatMessage {
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                border: 1px solid #e9ecef; /* Message Border */
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); /* Cards Shadow */
                max-width: 95%;
            }
            
            .user-msg {
                background: #e9ecef; /* Avatar Background for user message */
                font-weight: 500;
                border-bottom-right-radius: 2px;
                margin-left: auto; /* Align user message to the right */
                border-color: #dee2e6; /* Secondary Borders */
                color: #495057;
            }
            
            .bot-msg {
                background: #f8f9fa; /* Bot Message Background */
                border-bottom-left-radius: 2px;
                margin-right: auto; /* Align bot message to the left */
                color: #495057;
            }
            
            /* List and table styling within bot messages */
            .bot-msg ul,
            .bot-msg ol {
                margin-left: 25px;
                padding-left: 0;
            }
            
            .bot-msg li {
                margin-bottom: 8px;
                line-height: 1.5;
            }
            
            .bot-msg table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0 5px;
                margin: 15px 0;
                border: none;
            }
            
            .bot-msg th,
            .bot-msg td {
                border: 1px solid #dee2e6; /* Secondary Borders for table cells */
                padding: 12px;
                text-align: left;
                border-radius: 5px;
            }
            
            .bot-msg th {
                background-color: #e9ecef; /* Light Border for table headers */
                font-weight: bold;
                color: #495057; /* Primary Text */
            }
            
            /* Input area and dropdown styling */
            .stTextInput > div > div > input,
            .stSelectbox > div:first-child > div {
                border-radius: 8px;
                padding: 12px 16px;
                border: 2px solid #e9ecef; /* Primary Borders */
                background-color: #fff; /* Input Background */
                font-size: 14px;
                color: #495057; /* Primary Text */
                transition: all 0.2s ease;
            }

            /* Focus styling for inputs and selectboxes */
            .stTextInput > div > div > input:focus,
            .stSelectbox > div:first-child > div:focus-within {
                outline: none;
                border-color: #6c757d; /* Focus Borders */
                box-shadow: 0 0 0 3px rgba(108, 117, 125, 0.1);
            }

            .stTextInput > label, .stSelectbox > label {
                font-weight: 600;
                margin-bottom: 5px;
                color: #6c757d; /* Label Text */
            }
            
            /* Dropdown arrow customization */
            .stSelectbox > div:first-child > div {
                appearance: none;
                background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236c757d' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
                background-position: right 12px center;
                background-repeat: no-repeat;
                background-size: 16px;
                padding-right: 40px;
            }

            /* Button styling */
            .stButton > button {
                border-radius: 8px;
                padding: 10px 20px;
                background-color: #6c757d; /* Button Background */
                color: #fff;
                border: none;
                cursor: pointer;
                box-shadow: 0 2px 3px rgba(0,0,0,0.1);
                transition: background-color 0.2s ease;
            }
            .stButton > button:hover {
                background-color: #5a6268; /* Button Hover */
            }
            .stButton > button:disabled {
                background-color: #ced4da; /* Disabled Button */
                color: #6c757d;
                cursor: not-allowed;
            }
            
            /* Adjust alignment for Streamlit native chat elements */
            .st-emotion-cache-user-message {
                margin-left: auto;
                text-align: right;
            }

            .st-emotion-cache-assistant-message {
                 margin-right: auto;
                 text-align: left;
            }

            /* Specific targeting for the header container within stApp */
            .stApp > div:first-child > div:first-child > div:first-child > div:nth-child(2) {
                /* This targets the div wrapping the st.container in app.py */
                padding: 0px !important; /* Remove default padding */
            }

            /* Visit Us Button Styling */
            .visit-button {
                display: inline-block;
                padding: 8px 20px;
                background-color: #b22222;
                color: white !important;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                margin-right: 10px;
            }

            .visit-button:hover {
                background-color: #189B9B;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                text-decoration: none;
            }

            /* Adjust header columns alignment */
            .stApp > header .st-emotion-cache-18ni7ap {
                align-items: center;
            }

            /* Chat input submit button styling */
            .stChatInput > div > div > div > button {
                background-color: #b22222 !important;
                border-color: #b22222 !important;
                color: white !important;
            }

            .stChatInput > div > div > div > button:hover {
                background-color: #8b0000 !important;
                border-color: #8b0000 !important;
                box-shadow: 0 2px 4px rgba(178, 34, 34, 0.2) !important;
            }

            .stChatInput > div > div > div > button svg {
                fill: white !important;
            }

            /* Ensure the button maintains its color */
            .stChatInput > div > div > div > button::before,
            .stChatInput > div > div > div > button::after {
                background-color: #b22222 !important;
            }

            /* Override any default Streamlit styles */
            .st-emotion-cache-1ch5132 {
                background-color: #b22222 !important;
            }

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