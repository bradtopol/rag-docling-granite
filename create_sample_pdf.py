#!/usr/bin/env python3
"""
Create a sample PDF from the text document
This is a helper script to generate a test PDF
"""

def create_pdf_from_text(text_file: str, pdf_file: str):
    """Create a simple PDF from text file"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        # Read text file
        with open(text_file, 'r') as f:
            content = f.read()
        
        # Create PDF
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12
        )
        
        # Process content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.2*inch))
            elif line.startswith('# '):
                story.append(Paragraph(line[2:], title_style))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], styles['Heading2']))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], styles['Heading3']))
            else:
                story.append(Paragraph(line, styles['Normal']))
        
        doc.build(story)
        print(f"✓ Created PDF: {pdf_file}")
        return True
        
    except ImportError:
        print("reportlab not installed. Creating a simple text-based PDF...")
        # Fallback: just copy as text (user can manually convert)
        import shutil
        shutil.copy(text_file, pdf_file.replace('.pdf', '_fallback.txt'))
        print(f"⚠️  Please install reportlab: pip install reportlab")
        print(f"   Or manually convert {text_file} to PDF")
        return False
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False


if __name__ == "__main__":
    import os
    
    text_file = "documents/sample_document.txt"
    pdf_file = "documents/granite_overview.pdf"
    
    if not os.path.exists(text_file):
        print(f"Error: {text_file} not found")
    else:
        create_pdf_from_text(text_file, pdf_file)

# Made with Bob
