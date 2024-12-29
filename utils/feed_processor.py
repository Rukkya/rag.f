from typing import Dict, Any, List
from .data_cleaner import DataCleaner
from .text_chunker import TextChunker
from models.embedding_factory import EmbeddingFactory
import chromadb
from .chroma_settings import get_chroma_settings

class FeedProcessor:
    def __init__(self):
        self.cleaner = DataCleaner()
        self.chunker = TextChunker()
        self.chroma_client = chromadb.Client(get_chroma_settings())
    
    def process_and_embed_feeds(self, chat_id: str, model_name: str, 
                              rss_data: Dict[str, List[Dict]], 
                              api_data: Dict[str, Dict]) -> None:
        """Process and embed both RSS and API data"""
        try:
            collection_name = f"chat_{chat_id}_feeds"
            embedding_model = EmbeddingFactory.create_embeddings(model_name)
            
            # Get or create collection
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"model": model_name}
            )
            
            # Process RSS data
            for category, entries in rss_data.items():
                for i, entry in enumerate(entries):
                    # Clean entry
                    cleaned_text = self.cleaner.clean_rss_entry(entry)
                    
                    # Skip if no meaningful content
                    if not cleaned_text.strip():
                        continue
                    
                    # Chunk text
                    chunks = self.chunker.chunk_text(cleaned_text)
                    
                    # Generate embeddings
                    embeddings = embedding_model.embed_documents(chunks)
                    
                    # Prepare metadata
                    metadatas = [{
                        "chunk_index": j,
                        "source": "rss",
                        "category": category,
                        "entry_index": i,
                        "title": entry.get("title", ""),
                        "published": entry.get("published", ""),
                        "link": entry.get("link", "")
                    } for j in range(len(chunks))]
                    
                    # Add to collection
                    try:
                        collection.add(
                            documents=chunks,
                            embeddings=embeddings,
                            metadatas=metadatas,
                            ids=[f"{chat_id}_rss_{category}_{i}_{j}" 
                                 for j in range(len(chunks))]
                        )
                    except Exception as e:
                        print(f"Error adding RSS chunks to collection: {str(e)}")
                        continue
            
            # Process API data
            for source, data in api_data.items():
                # Clean data
                cleaned_text = self.cleaner.clean_api_data(data, source)
                
                # Skip if no meaningful content
                if not cleaned_text.strip():
                    continue
                
                # Chunk text
                chunks = self.chunker.chunk_text(cleaned_text)
                
                # Generate embeddings
                embeddings = embedding_model.embed_documents(chunks)
                
                # Prepare metadata
                metadatas = [{
                    "chunk_index": i,
                    "source": "api",
                    "api_name": source,
                    "timestamp": data.get("timestamp", "")
                } for i in range(len(chunks))]
                
                # Add to collection
                try:
                    collection.add(
                        documents=chunks,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        ids=[f"{chat_id}_api_{source}_{i}" 
                             for i in range(len(chunks))]
                    )
                except Exception as e:
                    print(f"Error adding API chunks to collection: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error processing and embedding feeds: {str(e)}")
    
    def search_feed_data(self, chat_id: str, query: str, 
                        model_name: str, n_results: int = 3) -> List[str]:
        """Search embedded feed data"""
        try:
            collection_name = f"chat_{chat_id}_feeds"
            collection = self.chroma_client.get_collection(name=collection_name)
            
            # Get embedding for query
            embedding_model = EmbeddingFactory.create_embeddings(model_name)
            query_embedding = embedding_model.embed_query(query)
            
            # Search with metadata
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Sort and format results
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            formatted_results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                source_type = meta.get('source', 'unknown')
                if source_type == 'rss':
                    category = meta.get('category', 'unknown')
                    title = meta.get('title', '')
                    published = meta.get('published', '')
                    link = meta.get('link', '')
                    formatted_results.append(
                        f"RSS ({category}) - {title}\n"
                        f"Published: {published}\n"
                        f"Content: {doc}\n"
                        f"Source: {link}"
                    )
                else:
                    api_name = meta.get('api_name', 'unknown')
                    timestamp = meta.get('timestamp', '')
                    formatted_results.append(
                        f"API ({api_name})\n"
                        f"Time: {timestamp}\n"
                        f"Content: {doc}"
                    )
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching feed data: {str(e)}")
            return []