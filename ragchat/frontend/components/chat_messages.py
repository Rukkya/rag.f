import streamlit as st

class ChatMessages:
    @staticmethod
    def render(messages):
        """Render chat messages"""
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