import streamlit as st
from ...utils.document_processor import DocumentProcessor
from ...database.db_manager import DatabaseManager

class FileUpload:
    @staticmethod
    def render(chat_id: int, chat_model: str, doc_processor: DocumentProcessor, db_manager: DatabaseManager):
        """Render file upload component"""
        uploaded_file = st.file_uploader("Upload Document (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
        if uploaded_file:
            filename, content = doc_processor.process_file(uploaded_file)
            embedding_id = doc_processor.create_embeddings(str(chat_id), content, chat_model)
            db_manager.add_document(chat_id, filename, content, embedding_id)
            st.success(f"Processed and embedded: {filename}")