#!/usr/bin/env python3
"""
Vector Store Module
Uses ChromaDB for storing and retrieving document embeddings
"""

import os
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings


class VectorStore:
    """Manage document embeddings and semantic search using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "documents"):
        """
        Initialize the vector store
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            print(f"Created new collection: {collection_name}")
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of chunk dictionaries with 'text', 'id', and metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not chunks:
            print("No chunks to add")
            return False
        
        try:
            # Prepare data for ChromaDB
            ids = [f"chunk_{chunk['source']}_{chunk['id']}" for chunk in chunks]
            documents = [chunk['text'] for chunk in chunks]
            metadatas = [
                {
                    'source': chunk.get('source', 'unknown'),
                    'chunk_id': chunk['id'],
                    'start_pos': chunk.get('start_pos', 0),
                    'length': chunk.get('length', 0)
                }
                for chunk in chunks
            ]
            
            # Add to collection (ChromaDB will automatically generate embeddings)
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"Added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i] if results['ids'] else ''
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'count': count,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the collection
            self.client.delete_collection(name=self.collection_name)
            
            # Recreate it
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            print(f"Cleared collection: {self.collection_name}")
            return True
            
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
    
    def delete_by_source(self, source: str) -> bool:
        """
        Delete all chunks from a specific source document
        
        Args:
            source: Source document name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all documents with this source
            results = self.collection.get(
                where={"source": source}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted {len(results['ids'])} chunks from {source}")
                return True
            else:
                print(f"No chunks found for source: {source}")
                return False
                
        except Exception as e:
            print(f"Error deleting by source: {e}")
            return False
    
    def list_sources(self) -> List[str]:
        """
        List all unique source documents in the collection
        
        Returns:
            List of source document names
        """
        try:
            # Get all documents
            results = self.collection.get()
            
            if results['metadatas']:
                sources = set(meta.get('source', 'unknown') for meta in results['metadatas'])
                return sorted(list(sources))
            
            return []
            
        except Exception as e:
            print(f"Error listing sources: {e}")
            return []


# Made with Bob