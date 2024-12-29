import streamlit as st
import asyncio
from typing import Optional
from ...utils.data_manager import DataManager

class RSSForm:
    @staticmethod
    async def update_feed_data(data_manager: DataManager, chat_id: int, chat_model: str) -> None:
        """Update feed data asynchronously"""
        try:
            await data_manager.update_data(chat_id, chat_model)
        except Exception as e:
            print(f"Error updating feed data: {str(e)}")

    @staticmethod
    def render(chat_id: int, chat_model: str, data_manager: DataManager):
        """Render RSS feed form"""
        if st.session_state.show_rss_form:
            with st.form("rss_form", clear_on_submit=True):
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
                        
                        # Create new event loop for async operation
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(
                                RSSForm.update_feed_data(data_manager, chat_id, chat_model)
                            )
                            st.session_state.show_rss_form = False
                            st.experimental_rerun()
                        finally:
                            loop.close()
                    else:
                        st.error("Invalid RSS feed URL")
                
                if cancel:
                    st.session_state.show_rss_form = False
                    st.experimental_rerun()