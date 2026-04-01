#!/bin/bash

# Run the RAG Application
# This script starts the RAG system with Docling and Granite

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting RAG System..."
echo "================================"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Error: Ollama server is not running."
    echo ""
    echo "Please start Ollama first:"
    echo "  ollama serve"
    echo ""
    echo "Then make sure you have the granite3-dense:2b model:"
    echo "  ollama pull granite3-dense:2b"
    echo ""
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed."
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import chromadb" 2>/dev/null; then
    echo "⚠️  Warning: Dependencies not fully installed."
    echo "Installing requirements..."
    pip3 install -r requirements.txt
    echo ""
fi

# Check if sample PDF exists, if not create it
if [ ! -f "documents/granite_overview.pdf" ] && [ -f "documents/sample_document.txt" ]; then
    echo "📄 Creating sample PDF document..."
    python3 create_sample_pdf.py
    echo ""
fi

# Run the RAG application
python3 rag_app.py "$@"

# Made with Bob