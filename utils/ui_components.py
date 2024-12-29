import streamlit as st

def render_message(msg):
    """Render a chat message with dynamic sizing"""
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

def render_chat_list(chats, db_manager, on_chat_selected):
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