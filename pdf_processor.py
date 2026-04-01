#!/usr/bin/env python3
"""
PDF Processor Module
Uses Docling to extract and process text from PDF documents
"""

import os
from typing import List, Dict, Optional
from pathlib import Path


class PDFProcessor:
    """Process PDF documents using Docling"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the PDF processor
        
        Args:
            chunk_size: Maximum size of text chunks in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Try to import docling
        try:
            from docling.document_converter import DocumentConverter
            self.converter = DocumentConverter()
            self.docling_available = True
        except ImportError:
            print("Warning: Docling not available. Using fallback text extraction.")
            self.docling_available = False
    
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if error
        """
        if not os.path.exists(pdf_path):
            print(f"Error: File not found: {pdf_path}")
            return None
        
        try:
            if self.docling_available:
                # Use Docling for advanced PDF processing
                result = self.converter.convert(pdf_path)
                text = result.document.export_to_markdown()
                return text
            else:
                # Fallback: Simple text extraction
                return self._fallback_extract(pdf_path)
                
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def _fallback_extract(self, pdf_path: str) -> Optional[str]:
        """
        Fallback text extraction using PyPDF2
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if error
        """
        try:
            import PyPDF2
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            print("Error: Neither Docling nor PyPDF2 is available.")
            print("Please install: pip install docling")
            return None
        except Exception as e:
            print(f"Error in fallback extraction: {e}")
            return None
    
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'length': len(chunk_text)
                })
                chunk_id += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> Optional[List[Dict[str, any]]]:
        """
        Process a PDF file: extract text and create chunks
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of text chunks with metadata or None if error
        """
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        print(f"Extracted {len(text)} characters")
        
        # Create chunks
        chunks = self.chunk_text(text)
        print(f"Created {len(chunks)} chunks")
        
        # Add source metadata to each chunk
        pdf_name = os.path.basename(pdf_path)
        for chunk in chunks:
            chunk['source'] = pdf_name
            chunk['source_path'] = pdf_path
        
        return chunks
    
    def process_directory(self, directory: str) -> List[Dict[str, any]]:
        """
        Process all PDF files in a directory
        
        Args:
            directory: Path to directory containing PDFs
            
        Returns:
            List of all chunks from all PDFs
        """
        all_chunks = []
        pdf_files = list(Path(directory).glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {directory}")
            return []
        
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_path in pdf_files:
            chunks = self.process_pdf(str(pdf_path))
            if chunks:
                all_chunks.extend(chunks)
        
        print(f"Total chunks created: {len(all_chunks)}")
        return all_chunks


# Made with Bob