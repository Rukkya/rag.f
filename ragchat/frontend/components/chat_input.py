import streamlit as st
import asyncio
import aiohttp
from typing import Optional

class ChatInput:
    @staticmethod
    async def send_message(chat_id: int, content: str) -> Optional[dict]:
        """Send message to backend API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:8000/api/chat/{chat_id}/messages",
                    json={"content": content, "role": "user"}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return None

    @staticmethod
    def render(chat_id: int):
        """Render chat input component"""
        col1, col2, col3 = st.columns([6, 1, 1])
        
        with col1:
            user_input = st.text_area("Your message:", key="user_input", height=100)
        
        with col2:
            if st.button("Send", use_container_width=True):
                if user_input:
                    # Create new event loop for async operation
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response = loop.run_until_complete(
                            ChatInput.send_message(chat_id, user_input)
                        )
                        if response:
                            st.session_state.user_input = ""  # Clear input after successful send
                            st.experimental_rerun()
                    finally:
                        loop.close()
        
        with col3:
            if st.button("📰 RSS", use_container_width=True):
                st.session_state.show_rss_form = True