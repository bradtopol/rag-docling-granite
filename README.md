# RAG System with Docling and Granite 4 Micro

A simple yet powerful Retrieval-Augmented Generation (RAG) system that combines Docling for PDF processing, ChromaDB for vector storage, and Granite 4 Micro for intelligent question answering.

## Features

- **Advanced PDF Processing**: Uses Docling to extract text from complex PDFs (tables, images, layouts)
- **Semantic Search**: ChromaDB with sentence-transformers for accurate document retrieval
- **Intelligent QA**: Granite 4 Micro (2B parameters) for context-aware answers
- **Persistent Storage**: Vector database persists between sessions
- **Interactive CLI**: User-friendly command-line interface
- **Source Tracking**: Answers include source document citations
- **Easy Setup**: Simple installation and configuration

## Architecture

```
┌─────────────┐
│   PDF Docs  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  PDF Processor  │  ← Docling
│  (Text Extract) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Vector Store   │  ← ChromaDB
│  (Embeddings)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐     ┌──────────────┐
│   RAG Engine    │ ←── │  Granite 4   │
│  (Retrieval +   │     │    Micro     │
│   Generation)   │     └──────────────┘
└─────────────────┘
```

## Prerequisites

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)

2. **Pull Granite Model**:
   ```bash
   ollama pull granite3-dense:2b
   ```

3. **Start Ollama Server**:
   ```bash
   ollama serve
   ```

## Installation

1. **Navigate to the project directory**:
   ```bash
   cd rag_example
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `docling` - Advanced PDF processing
   - `chromadb` - Vector database
   - `sentence-transformers` - Text embeddings
   - `requests` - HTTP client for Ollama

## Quick Start

### Option 1: Using the Run Script (Recommended)

```bash
./run_rag.sh
```

The script will:
- Check Ollama connection
- Install dependencies if needed
- Create sample PDF if missing
- Start the interactive RAG system

### Option 2: Manual Execution

```bash
# Create sample PDF (optional)
python3 create_sample_pdf.py

# Run the RAG application
python3 rag_app.py
```

## Usage

### Interactive Mode

Once started, you can:

1. **Ask Questions**:
   ```
   Question: What is Granite 3 Dense 2B?
   ```

2. **List Documents**:
   ```
   Question: sources
   ```

3. **View Statistics**:
   ```
   Question: stats
   ```

4. **Toggle Context Display**:
   ```
   Question: context
   ```

5. **Exit**:
   ```
   Question: quit
   ```

### Example Session

```
======================================================================
RAG System with Docling and Granite 4 Micro
Model: granite3-dense:2b
======================================================================

Checking Ollama connection...
✓ Connected to Ollama

✓ Vector store loaded: 15 chunks

======================================================================
RAG System - Interactive Query Mode
======================================================================

📊 Vector Store: 15 chunks
📚 Documents: granite_overview.pdf

Commands:
  - Ask any question about your documents
  - Type 'sources' to list all documents
  - Type 'stats' to show statistics
  - Type 'context' to toggle context display
  - Type 'quit' or 'exit' to end the session
======================================================================

Question: What are the key features of Granite models?

🔍 Searching for relevant information...
✓ Found 3 relevant passages
📚 Sources: granite_overview.pdf

💬 Answer: Based on the provided context, the key features of Granite models include:

1. **Open Source**: Released under permissive licenses for free commercial use
2. **Enterprise Ready**: Built with safety guardrails and bias mitigation
3. **Efficient Architecture**: Optimized for fast inference and low memory usage
4. **Diverse Training**: Trained on technical docs, code, research papers, and more
5. **Multiple Use Cases**: Excellent for code generation, QA, text generation, and RAG

The models are specifically designed for enterprise deployment with a focus
on efficiency and responsible AI practices.

Question: quit
Goodbye! 👋
```

## Adding Your Own Documents

1. **Add PDF files** to the `documents/` directory:
   ```bash
   cp your_document.pdf rag_example/documents/
   ```

2. **Ingest documents**:
   ```bash
   python3 rag_app.py --ingest
   ```

3. **Force re-ingestion** (if updating documents):
   ```bash
   python3 rag_app.py --ingest --force
   ```

## Command-Line Options

```bash
python3 rag_app.py [OPTIONS]

Options:
  --documents DIR    Directory containing PDF documents (default: ./documents)
  --db DIR          Directory for vector database (default: ./chroma_db)
  --model NAME      Ollama model to use (default: granite3-dense:2b)
  --ingest          Ingest documents and exit
  --force           Force re-ingestion of documents
```

### Examples

```bash
# Use a different model
python3 rag_app.py --model granite3-dense:8b

# Use custom directories
python3 rag_app.py --documents /path/to/pdfs --db /path/to/db

# Just ingest documents
python3 rag_app.py --ingest

# Re-ingest all documents
python3 rag_app.py --ingest --force
```

## Project Structure

```
rag_example/
├── pdf_processor.py          # PDF text extraction with Docling
├── vector_store.py           # ChromaDB vector storage
├── rag_engine.py             # RAG query engine
├── rag_app.py               # Main CLI application
├── create_sample_pdf.py     # Helper to create sample PDF
├── requirements.txt          # Python dependencies
├── run_rag.sh               # Execution script
├── README.md                # This file
├── documents/               # PDF documents directory
│   ├── sample_document.txt  # Sample text content
│   └── granite_overview.pdf # Sample PDF (auto-generated)
└── chroma_db/              # Vector database (auto-created)
```

## How It Works

### 1. Document Ingestion

```python
# Extract text from PDFs using Docling
processor = PDFProcessor(chunk_size=500, chunk_overlap=50)
chunks = processor.process_pdf("document.pdf")

# Store in vector database
vector_store = VectorStore()
vector_store.add_documents(chunks)
```

### 2. Query Processing

```python
# Retrieve relevant chunks
results = vector_store.search(query, n_results=3)

# Generate answer with Granite
rag_engine = RAGEngine(vector_store)
answer = rag_engine.query(question)
```

### 3. Answer Generation

The system:
1. Converts your question to embeddings
2. Finds the most relevant document chunks
3. Provides context to Granite 4 Micro
4. Generates an accurate, context-aware answer
5. Cites source documents

## Customization

### Adjust Chunk Size

Edit `rag_app.py`:
```python
self.pdf_processor = PDFProcessor(
    chunk_size=1000,  # Larger chunks
    chunk_overlap=100  # More overlap
)
```

### Change Retrieval Count

Edit `rag_app.py`:
```python
self.rag_engine = RAGEngine(
    vector_store=self.vector_store,
    n_results=5  # Retrieve more chunks
)
```

### Use Different Model

```bash
# Larger, more capable model
python3 rag_app.py --model granite3-dense:8b

# Or edit rag_app.py default
```

## Troubleshooting

### "Cannot connect to Ollama server"

1. Check if Ollama is running: `ollama list`
2. Start Ollama: `ollama serve`
3. Verify port 11434 is accessible

### "Model not found"

Pull the model:
```bash
ollama pull granite3-dense:2b
```

### "No documents processed"

1. Check PDF files exist in `documents/` directory
2. Verify PDFs are readable (not encrypted)
3. Try the sample document first

### Slow Performance

- Use smaller model: `granite3-dense:2b` (faster)
- Reduce chunk retrieval: `n_results=2`
- Reduce chunk size: `chunk_size=300`

### Import Errors

Reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
```

## Advanced Features

### Programmatic Usage

```python
from rag_app import RAGApp

# Initialize
app = RAGApp(
    documents_dir="./my_docs",
    db_dir="./my_db",
    model="granite3-dense:2b"
)

# Ingest documents
app.ingest_documents()

# Query
result = app.rag_engine.query(
    "What is the main topic?",
    stream=False,
    show_context=True
)

print(result['answer'])
print(result['sources'])
```

### Batch Processing

```python
questions = [
    "What is Granite?",
    "What are the model sizes?",
    "What are the use cases?"
]

for q in questions:
    result = app.rag_engine.query(q, stream=False)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

## Performance Tips

1. **First Run**: Initial embedding generation takes time
2. **Subsequent Runs**: Vector DB persists, queries are fast
3. **Model Choice**: 2B model is faster, 8B is more accurate
4. **Chunk Size**: Balance between context and precision
5. **Hardware**: GPU acceleration available with proper setup

## Requirements

- Python 3.7+
- Ollama with Granite model
- 4GB+ RAM (for 2B model)
- 8GB+ RAM (for 8B model)
- Internet connection (first-time setup)

## License

Created with Bob - Feel free to use and modify!

## Resources

- [Ollama](https://ollama.ai) - Local LLM runtime
- [Docling](https://github.com/DS4SD/docling) - Document processing
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Granite Models](https://huggingface.co/ibm-granite) - IBM's LLMs

## Contributing

Suggestions and improvements welcome! This is a simple example to get started with RAG systems.

## Next Steps

- Add support for more document types (DOCX, TXT, MD)
- Implement conversation history
- Add web interface
- Support multiple languages
- Add document summarization
- Implement hybrid search (keyword + semantic)

---

Made with Bob 🤖 | Powered by Docling 📄 + Granite 🪨 + ChromaDB 🔍