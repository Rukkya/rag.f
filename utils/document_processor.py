from typing import List, Tuple
import PyPDF2
from docx import Document
from utils.embedding_manager import EmbeddingManager
import os

class DocumentProcessor:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        
    def process_file(self, file) -> Tuple[str, str]:
        filename = file.name
        content = ""
        
        if filename.endswith('.pdf'):
            content = self._process_pdf(file)
        elif filename.endswith('.docx'):
            content = self._process_docx(file)
        elif filename.endswith('.txt'):
            content = self._process_txt(file)
            
        return filename, content
    
    def _process_pdf(self, file) -> str:
        pdf_reader = PyPDF2.PdfReader(file)
        content = ""
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
        return content
    
    def _process_docx(self, file) -> str:
        doc = Document(file)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content
    
    def _process_txt(self, file) -> str:
        content = file.read().decode('utf-8')
        return content
    
    def create_embeddings(self, chat_id: str, content: str, model_name: str) -> str:
        """Create embeddings using the appropriate model"""
        return self.embedding_manager.create_embeddings(chat_id, content, model_name)
    
    def search_similar(self, chat_id: str, query: str, model_name: str, n_results: int = 3) -> List[str]:
        """Search for similar content using the appropriate model"""
        return self.embedding_manager.search_similar(chat_id, query, model_name, n_results)