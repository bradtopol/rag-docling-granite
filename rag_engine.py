#!/usr/bin/env python3
"""
RAG Engine Module
Integrates vector search with Granite 4 Micro for question answering
"""

import json
from typing import List, Dict, Optional, Any
import requests


class RAGEngine:
    """RAG engine combining retrieval and generation"""
    
    def __init__(
        self,
        vector_store,
        model: str = "granite3-dense:2b",
        base_url: str = "http://localhost:11434",
        n_results: int = 3
    ):
        """
        Initialize the RAG engine
        
        Args:
            vector_store: VectorStore instance for retrieval
            model: Ollama model name
            base_url: Ollama API base URL
            n_results: Number of chunks to retrieve for context
        """
        self.vector_store = vector_store
        self.model = model
        self.base_url = base_url
        self.chat_url = f"{base_url}/api/chat"
        self.n_results = n_results
        
        # System prompt for RAG
        self.system_prompt = """You are a helpful AI assistant that answers questions based on provided context.

Instructions:
1. Use ONLY the information from the provided context to answer questions
2. If the context doesn't contain enough information, say so clearly
3. Be concise and accurate
4. Cite which document the information comes from when relevant
5. If asked about something not in the context, politely explain you can only answer based on the provided documents"""
    
    def check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def retrieve_context(self, query: str) -> tuple[List[Dict[str, Any]], str]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            
        Returns:
            Tuple of (retrieved chunks, formatted context string)
        """
        # Search vector store
        results = self.vector_store.search(query, n_results=self.n_results)
        
        if not results:
            return [], "No relevant context found."
        
        # Format context
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source', 'unknown')
            text = result['text']
            context_parts.append(f"[Document: {source}]\n{text}")
        
        context = "\n\n---\n\n".join(context_parts)
        return results, context
    
    def generate_answer(
        self,
        query: str,
        context: str,
        stream: bool = True
    ) -> Optional[str]:
        """
        Generate an answer using Granite with retrieved context
        
        Args:
            query: User query
            context: Retrieved context
            stream: Whether to stream the response
            
        Returns:
            Generated answer or None if error
        """
        # Construct the prompt with context
        user_message = f"""Context:
{context}

Question: {query}

Please answer the question based on the context provided above."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": stream
            }
            
            response = requests.post(self.chat_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                full_response = ""
                
                if stream:
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if 'message' in data and 'content' in data['message']:
                                chunk = data['message']['content']
                                print(chunk, end='', flush=True)
                                full_response += chunk
                    print()  # New line after streaming
                else:
                    data = response.json()
                    full_response = data.get('message', {}).get('content', '')
                    print(full_response)
                
                return full_response
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error generating answer: {e}")
            return None
    
    def query(self, question: str, stream: bool = True, show_context: bool = False) -> Optional[Dict[str, Any]]:
        """
        Complete RAG query: retrieve context and generate answer
        
        Args:
            question: User question
            stream: Whether to stream the response
            show_context: Whether to display retrieved context
            
        Returns:
            Dictionary with answer, context, and sources or None if error
        """
        print(f"\n🔍 Searching for relevant information...")
        
        # Retrieve context
        chunks, context = self.retrieve_context(question)
        
        if not chunks:
            print("❌ No relevant information found in the documents.")
            return None
        
        print(f"✓ Found {len(chunks)} relevant passages")
        
        # Show sources
        sources = set(chunk['metadata'].get('source', 'unknown') for chunk in chunks)
        print(f"📚 Sources: {', '.join(sources)}")
        
        # Optionally show context
        if show_context:
            print("\n--- Retrieved Context ---")
            print(context)
            print("--- End Context ---\n")
        
        # Generate answer
        print(f"\n💬 Answer: ", end='', flush=True)
        answer = self.generate_answer(question, context, stream=stream)
        
        if answer:
            return {
                'question': question,
                'answer': answer,
                'context': context,
                'sources': list(sources),
                'num_chunks': len(chunks)
            }
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG engine statistics
        
        Returns:
            Dictionary with statistics
        """
        vector_stats = self.vector_store.get_collection_stats()
        return {
            'model': self.model,
            'base_url': self.base_url,
            'n_results': self.n_results,
            'vector_store': vector_stats
        }


# Made with Bob