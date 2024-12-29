import chromadb
from typing import List, Optional
from ...models.embedding_factory import EmbeddingFactory
from ..text import TextChunker
from ...config import get_chroma_settings

class EmbeddingManager:
    def __init__(self):
        self.chroma_client = chromadb.Client(get_chroma_settings())
        self.text_chunker = TextChunker()
    
    def create_embeddings(self, chat_id: str, content: str, model_name: str) -> str:
        """Create embeddings for content"""
        collection_name = f"chat_{chat_id}"
        embedding_model = EmbeddingFactory.create_embeddings(model_name)
        
        collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"model": model_name}
        )
        
        chunks = self.text_chunker.chunk_text(content)
        embeddings = embedding_model.embed_documents(chunks)
        
        metadatas = [{"chunk_index": i, "source": "document"} 
                    for i in range(len(chunks))]
        
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=[f"{chat_id}_chunk_{i}" for i in range(len(chunks))]
        )
        
        return collection_name
    
    def search_similar(self, chat_id: str, query: str, model_name: str,
                      n_results: int = 3) -> List[str]:
        """Search for similar content"""
        try:
            collection_name = f"chat_{chat_id}"
            collection = self.chroma_client.get_collection(name=collection_name)
            
            embedding_model = EmbeddingFactory.create_embeddings(model_name)
            query_embedding = embedding_model.embed_query(query)
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            return [doc for doc in results['documents'][0]]
            
        except Exception as e:
            print(f"Error during similarity search: {str(e)}")
            return []