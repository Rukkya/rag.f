import streamlit as st
from ...database.db_manager import DatabaseManager

class ChatList:
    @staticmethod
    def render(chats, db_manager: DatabaseManager, on_chat_selected):
        """Render the list of chats with settings"""
        for chat in chats:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📝 {chat.name} ({chat.model})", key=f"chat_{chat.id}"):
                    on_chat_selected(chat.id)
            
            with col2:
                settings_key = f"settings_{chat.id}"
                action = st.selectbox(
                    "Settings",
                    ["Select", "Share", "Delete"],
                    key=settings_key,
                    label_visibility="collapsed"
                )
                
                if action == "Delete":
                    db_manager.delete_chat(chat.id)
                    if st.session_state.current_chat_id == chat.id:
                        st.session_state.current_chat_id = None
                    st.experimental_rerun()
                elif action == "Share":
                    api_key = db_manager.toggle_chat_sharing(chat.id)
                    if api_key:
                        share_url = f"{st.get_option('server.baseUrlPath')}/chat/{api_key}"
                        st.code(share_url, language="text")