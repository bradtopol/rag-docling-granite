#!/usr/bin/env python3
"""
RAG Application
Simple RAG system using Docling and Granite 4 Micro
"""

import sys
import os
from pathlib import Path

# Check for required dependencies
try:
    import requests
except ImportError:
    print("Error: 'requests' module is not installed.")
    print("\nPlease install dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

from pdf_processor import PDFProcessor
from vector_store import VectorStore
from rag_engine import RAGEngine


class RAGApp:
    """Main RAG application"""
    
    def __init__(
        self,
        documents_dir: str = "./documents",
        db_dir: str = "./chroma_db",
        model: str = "granite3-dense:2b"
    ):
        """
        Initialize the RAG application
        
        Args:
            documents_dir: Directory containing PDF documents
            db_dir: Directory for vector database
            model: Ollama model to use
        """
        self.documents_dir = documents_dir
        self.db_dir = db_dir
        self.model = model
        
        # Initialize components
        print("Initializing RAG system...")
        self.pdf_processor = PDFProcessor(chunk_size=500, chunk_overlap=50)
        self.vector_store = VectorStore(persist_directory=db_dir)
        self.rag_engine = RAGEngine(
            vector_store=self.vector_store,
            model=model,
            n_results=3
        )
        print("✓ RAG system initialized\n")
    
    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        if not self.rag_engine.check_connection():
            print("❌ Error: Cannot connect to Ollama server.")
            print("\nPlease make sure:")
            print("  1. Ollama is installed (https://ollama.ai)")
            print("  2. Ollama server is running: ollama serve")
            print(f"  3. Model is installed: ollama pull {self.model}")
            return False
        return True
    
    def ingest_documents(self, force: bool = False) -> bool:
        """
        Ingest PDF documents from the documents directory
        
        Args:
            force: Force re-ingestion even if documents exist
            
        Returns:
            True if successful, False otherwise
        """
        # Check if documents already exist
        stats = self.vector_store.get_collection_stats()
        if stats.get('count', 0) > 0 and not force:
            print(f"Vector store already contains {stats['count']} chunks.")
            print("Use 'ingest --force' to re-ingest documents.\n")
            return True
        
        # Check if documents directory exists
        if not os.path.exists(self.documents_dir):
            print(f"❌ Documents directory not found: {self.documents_dir}")
            print(f"Please create it and add PDF files: mkdir -p {self.documents_dir}")
            return False
        
        # Process documents
        print(f"📄 Processing documents from: {self.documents_dir}")
        chunks = self.pdf_processor.process_directory(self.documents_dir)
        
        if not chunks:
            print("❌ No documents processed. Please add PDF files to the documents directory.")
            return False
        
        # Clear existing data if force
        if force and stats.get('count', 0) > 0:
            print("Clearing existing vector store...")
            self.vector_store.clear_collection()
        
        # Add to vector store
        print("💾 Adding documents to vector store...")
        success = self.vector_store.add_documents(chunks)
        
        if success:
            print(f"✓ Successfully ingested {len(chunks)} chunks")
            return True
        else:
            print("❌ Failed to ingest documents")
            return False
    
    def query_interactive(self):
        """Interactive query mode"""
        print("=" * 70)
        print("RAG System - Interactive Query Mode")
        print("=" * 70)
        print()
        
        # Show statistics
        stats = self.vector_store.get_collection_stats()
        sources = self.vector_store.list_sources()
        
        print(f"📊 Vector Store: {stats.get('count', 0)} chunks")
        if sources:
            print(f"📚 Documents: {', '.join(sources)}")
        print()
        
        print("Commands:")
        print("  - Ask any question about your documents")
        print("  - Type 'sources' to list all documents")
        print("  - Type 'stats' to show statistics")
        print("  - Type 'context' to toggle context display")
        print("  - Type 'quit' or 'exit' to end the session")
        print("=" * 70)
        print()
        
        show_context = False
        
        while True:
            try:
                user_input = input("Question: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit"]:
                    print("\nGoodbye! 👋")
                    break
                
                if user_input.lower() == "sources":
                    sources = self.vector_store.list_sources()
                    if sources:
                        print(f"\n📚 Available documents:")
                        for source in sources:
                            print(f"  - {source}")
                    else:
                        print("\n❌ No documents in vector store")
                    print()
                    continue
                
                if user_input.lower() == "stats":
                    stats = self.rag_engine.get_stats()
                    print(f"\n📊 RAG Engine Statistics:")
                    print(f"  Model: {stats['model']}")
                    print(f"  Retrieval results: {stats['n_results']}")
                    print(f"  Vector store chunks: {stats['vector_store'].get('count', 0)}")
                    print()
                    continue
                
                if user_input.lower() == "context":
                    show_context = not show_context
                    status = "enabled" if show_context else "disabled"
                    print(f"\n✓ Context display {status}\n")
                    continue
                
                # Process query
                result = self.rag_engine.query(
                    user_input,
                    stream=True,
                    show_context=show_context
                )
                
                if not result:
                    print("❌ Could not generate an answer\n")
                else:
                    print()  # Extra newline for readability
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}\n")
    
    def run(self):
        """Run the RAG application"""
        print("=" * 70)
        print("RAG System with Docling and Granite 4 Micro")
        print(f"Model: {self.model}")
        print("=" * 70)
        print()
        
        # Check Ollama connection
        print("Checking Ollama connection...")
        if not self.check_ollama():
            return
        print("✓ Connected to Ollama\n")
        
        # Check if documents are ingested
        stats = self.vector_store.get_collection_stats()
        if stats.get('count', 0) == 0:
            print("📄 No documents found in vector store.")
            print("Ingesting documents...\n")
            if not self.ingest_documents():
                return
        else:
            print(f"✓ Vector store loaded: {stats['count']} chunks\n")
        
        # Start interactive mode
        self.query_interactive()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="RAG System with Docling and Granite 4 Micro"
    )
    parser.add_argument(
        "--documents",
        default="./documents",
        help="Directory containing PDF documents"
    )
    parser.add_argument(
        "--db",
        default="./chroma_db",
        help="Directory for vector database"
    )
    parser.add_argument(
        "--model",
        default="granite3-dense:2b",
        help="Ollama model to use"
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Ingest documents and exit"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion of documents"
    )
    
    args = parser.parse_args()
    
    # Initialize app
    app = RAGApp(
        documents_dir=args.documents,
        db_dir=args.db,
        model=args.model
    )
    
    # Check Ollama
    if not app.check_ollama():
        sys.exit(1)
    
    # Ingest mode
    if args.ingest:
        success = app.ingest_documents(force=args.force)
        sys.exit(0 if success else 1)
    
    # Run interactive mode
    app.run()


if __name__ == "__main__":
    main()


# Made with Bob