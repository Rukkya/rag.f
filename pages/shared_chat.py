import streamlit as st
from database.db_manager import DatabaseManager
from models.model_factory import ModelFactory
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize database manager
db_manager = DatabaseManager()

def main():
    st.title("Shared Chat")
    
    # Get API key from URL parameters
    params = st.experimental_get_query_params()
    api_key = params.get("key", [None])[0]
    
    if not api_key:
        st.error("No API key provided")
        return
    
    # Get chat by API key
    chat = db_manager.get_chat_by_api_key(api_key)
    if not chat:
        st.error("Invalid or expired API key")
        return
    
    st.header(f"Chat: {chat.name}")
    
    # Display messages
    messages = db_manager.get_chat_messages(chat.id)
    for msg in messages:
        if msg.role == "user":
            st.write(
                f'<div style="text-align: right; margin: 10px; padding: 10px; '
                f'background-color: #e6f3ff; border-radius: 10px; '
                f'display: inline-block; float: right; max-width: 80%; '
                f'word-wrap: break-word;">{msg.content}</div><div style="clear: both;"></div>',
                unsafe_allow_html=True
            )
        else:
            st.write(
                f'<div style="text-align: left; margin: 10px; padding: 10px; '
                f'background-color: #f0f0f0; border-radius: 10px; '
                f'display: inline-block; max-width: 80%; '
                f'word-wrap: break-word;">{msg.content}</div>',
                unsafe_allow_html=True
            )
    
    # Input area
    user_input = st.text_area("Your message:", key="shared_input")
    if st.button("Send"):
        if user_input:
            # Save user message
            db_manager.add_message(chat.id, "user", user_input)
            
            # Get model response
            model = ModelFactory.create_model(chat.model)
            response = model.predict(user_input)
            
            # Save assistant message
            db_manager.add_message(chat.id, "assistant", response)
            
            # Clear input and refresh
            st.session_state.shared_input = ""
            st.experimental_rerun()

if __name__ == "__main__":
    main()