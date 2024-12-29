import streamlit as st
from models.model_factory import ModelFactory
from database.db_manager import DatabaseManager
from utils.document_processor import DocumentProcessor
from utils.data_manager import DataManager
from utils.ui_components import render_message, render_chat_list
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Initialize components
db_manager = DatabaseManager()
doc_processor = DocumentProcessor()
data_manager = DataManager(db_manager)

# Streamlit configuration
st.set_page_config(page_title="RAG Chat App", layout="wide")

# Session state initialization
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'show_rss_form' not in st.session_state:
    st.session_state.show_rss_form = False
if 'message_sent' not in st.session_state:
    st.session_state.message_sent = False

# Callback for sending messages
def send_message(chat_id, user_input, chat_model):
    if user_input:
        # Save user message
        db_manager.add_message(chat_id, "user", user_input)
        
        # Get context from documents and feeds
        doc_context = doc_processor.search_similar(str(chat_id), user_input, chat_model)
        feed_context = data_manager.get_relevant_context(user_input, str(chat_id), chat_model)
        
        # Combine context
        context = "\n".join(doc_context + [feed_context]) if feed_context else "\n".join(doc_context)
        
        # Get model response with context
        model = ModelFactory.create_model(chat_model)
        prompt = f"Context: {context}\n\nQuestion: {user_input}"
        response = model.predict(prompt)
        
        # Save assistant message
        db_manager.add_message(chat_id, "assistant", response)
        
        # Set message sent flag
        st.session_state.message_sent = True

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
    render_chat_list(chats, db_manager, lambda id: setattr(st.session_state, 'current_chat_id', id))

# Main chat area
if st.session_state.current_chat_id:
    chat_id = st.session_state.current_chat_id
    chat = db_manager.get_chat_by_id(chat_id)
    
    st.title(f"Chat: {chat.name}")
    
    # Display the unique chat endpoint URL
    chat_endpoint_url = f"api/chats/{chat_id}"
    st.markdown(f"**Chat Endpoint:** [Click here]({chat_endpoint_url})")

    # File upload
    uploaded_file = st.file_uploader("Upload Document (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
    if uploaded_file:
        filename, content = doc_processor.process_file(uploaded_file)
        embedding_id = doc_processor.create_embeddings(str(chat_id), content, chat.model)
        db_manager.add_document(chat_id, filename, content, embedding_id)
        st.success(f"Processed and embedded: {filename}")
    
    # Display messages
    messages_container = st.container()
    with messages_container:
        messages = db_manager.get_chat_messages(chat_id)
        for msg in messages:
            render_message(msg)
    
    # Input area with RSS feed button
    st.write("")  # Add some spacing
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        user_input = st.text_area("Your message:", key="user_input", height=100)
    
    with col2:
        if st.button("Send", use_container_width=True):
            send_message(chat_id, user_input, chat.model)
            st.experimental_rerun()
    
    with col3:
        # RSS Feed button that opens a modal-like form
        if st.button("📰 RSS", use_container_width=True):
            st.session_state.show_rss_form = True
    
    # RSS Feed Form
    if st.session_state.show_rss_form:
        with st.form("rss_form"):
            st.subheader("Add RSS Feed")
            feed_category = st.selectbox(
                "Category",
                ["tech", "science", "news"]
            )
            feed_url = st.text_input("Feed URL")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Add")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submit and feed_url:
                if data_manager.data_fetcher.add_rss_feed(feed_category, feed_url):
                    st.success("RSS feed added successfully")
                    asyncio.run(data_manager.update_data(chat_id, chat.model))
                    st.session_state.show_rss_form = False
                    st.experimental_rerun()
                else:
                    st.error("Invalid RSS feed URL")
            
            if cancel:
                st.session_state.show_rss_form = False
                st.experimental_rerun()

else:
    st.title("Welcome to RAG Chat App!")
    st.write("Create a new chat or select an existing one to start conversing.")
