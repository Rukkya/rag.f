"""Streamlit frontend application."""

import streamlit as st
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from ragchat import DatabaseManager, DataManager, DocumentProcessor
from ragchat.frontend.components import (
    ChatInput,
    ChatList,
    ChatMessages,
    FileUpload,
    RSSForm
)

# Initialize components
db_manager = DatabaseManager()
doc_processor = DocumentProcessor()
data_manager = DataManager(db_manager)

def main():
    """Main application entry point."""
    # Streamlit configuration
    st.set_page_config(page_title="RAG Chat App", layout="wide")
    
    # Session state initialization
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None
    if 'show_rss_form' not in st.session_state:
        st.session_state.show_rss_form = False
    
    # Sidebar
    with st.sidebar:
        st.title("RAG Chat App")
        
        # Create new chat
        st.subheader("Create New Chat")
        chat_name = st.text_input("Chat Name", key="new_chat_name")
        model_options = ["openai", "gemini", "claude", "bloom", "llama", "mpt"]
        selected_model = st.selectbox("Select Model", model_options)
        
        if st.button("Create Chat"):
            if chat_name:
                chat_id, error = db_manager.create_chat(chat_name, selected_model)
                if chat_id:
                    st.session_state.current_chat_id = chat_id
                    st.success(f"Created new chat: {chat_name}")
                    st.experimental_rerun()
                else:
                    st.error(error)
        
        # List existing chats
        st.subheader("Your Chats")
        chats = db_manager.get_all_chats()
        ChatList.render(chats, db_manager)
    
    # Main chat area
    if st.session_state.current_chat_id:
        chat_id = st.session_state.current_chat_id
        chat = db_manager.get_chat_by_id(chat_id)
        
        st.title(f"Chat: {chat.name}")
        
        # File upload
        FileUpload.render(chat_id, chat.model, doc_processor, db_manager)
        
        # Display messages
        messages_container = st.container()
        with messages_container:
            messages = db_manager.get_chat_messages(chat_id)
            ChatMessages.render(messages)
        
        # Input area
        ChatInput.render(chat_id, chat.model, data_manager)
        
        # RSS Form
        if st.session_state.show_rss_form:
            RSSForm.render(chat_id, chat.model, data_manager)
    
    else:
        st.title("Welcome to RAG Chat App!")
        st.write("Create a new chat or select an existing one to start conversing.")

if __name__ == "__main__":
    main()