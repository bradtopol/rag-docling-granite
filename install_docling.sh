#!/bin/bash

# Install Docling and dependencies
# This script installs Docling without the problematic pyobjc dependency

echo "Installing Docling for RAG System..."
echo "===================================="
echo ""

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip3 install -r requirements.txt

# Install Docling core packages without dependencies
echo ""
echo "📄 Installing Docling core packages..."
pip3 install --no-deps docling docling-core docling-parse docling-ibm-models

# Install Docling dependencies (excluding pyobjc)
echo ""
echo "🔧 Installing Docling dependencies..."
pip3 install pandas beautifulsoup4 lxml python-docx python-pptx openpyxl filetype pypdfium2 rtree marko pylatexenc tabulate

echo ""
echo "🚀 Installing ML dependencies..."
pip3 install accelerate pluggy polyfactory jsonlines jsonref latex2mathml torchvision rapidocr

echo ""
echo "✅ Docling installation complete!"
echo ""
echo "Note: ocrmac (macOS OCR) was skipped due to pyobjc compilation issues."
echo "Docling will work without it for most PDF processing tasks."
echo ""
echo "To test: python3 -c 'from docling.document_converter import DocumentConverter; print(\"Success!\")'"

# Made with Bob