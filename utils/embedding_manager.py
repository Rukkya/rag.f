import chromadb
from .chroma_settings import get_chroma_settings
from models.embedding_factory import EmbeddingFactory
from .text_chunker import TextChunker

class EmbeddingManager:
    def __init__(self):
        self.chroma_client = chromadb.Client(get_chroma_settings())
        self.text_chunker = TextChunker()
    
    def create_embeddings(self, chat_id: str, content: str, model_name: str) -> str:
        collection_name = f"chat_{chat_id}"
        embedding_model = EmbeddingFactory.create_embeddings(model_name)
        
        collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"model": model_name}
        )
        
        chunks = self.text_chunker.chunk_text(content)
        embeddings = embedding_model.embed_documents(chunks)
        
        metadatas = [{"chunk_index": i, "source": "document"} for i in range(len(chunks))]
        
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=[f"{chat_id}_chunk_{i}" for i in range(len(chunks))]
        )
        
        return collection_name
    
    def search_similar(self, chat_id: str, query: str, model_name: str, n_results: int = 3) -> list[str]:
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
            
            documents = results['documents'][0]
            distances = results['distances'][0]
            
            chunks_with_scores = list(zip(documents, distances))
            chunks_with_scores.sort(key=lambda x: x[1])
            
            return [chunk for chunk, _ in chunks_with_scores]
            
        except Exception as e:
            print(f"Error during similarity search: {str(e)}")
            return []