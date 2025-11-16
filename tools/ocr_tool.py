"""
OCR Tool: Text extraction from documents.

This internal tool simulates OCR (Optical Character Recognition) for extracting
text from scanned documents or images. In production, this would integrate with
Google Cloud Vision API or similar services.

For the Capstone POC, it reads from a sample document file to demonstrate the workflow.
"""

import os


def ocr_tool(document_path: str) -> dict:
    """
    Extract text from a document using OCR.
    
    In production, this would:
    - Connect to Google Cloud Vision API
    - Process images/PDFs with OCR
    - Handle multiple pages
    - Extract text with confidence scores
    
    For this POC, it:
    - Reads text from the sample document file
    - Returns realistic OCR-like output
    
    Args:
        document_path: Path to the document to process
    
    Returns:
        dict: OCR result
            {
                "status": "success" | "error",
                "extracted_text": str,
                "detected_language": str,
                "page_count": int,
                "error_message": str (if error)
            }
    """
    print(f"\n[Tool: ocr_tool] Extracting text from: {document_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(document_path):
            return {
                "status": "error",
                "error_message": f"Document not found: {document_path}"
            }
        
        # Read the document content
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simulate language detection (simple heuristic)
        # In production, use langdetect or Cloud Translation API
        detected_lang = "es"  # Assuming Spanish for our sample
        
        # Count "pages" (simulate - in reality would be from PDF/image analysis)
        page_count = 1
        
        word_count = len(content.split())
        
        print(f"    ✓ Extracted {word_count} words")
        print(f"    ✓ Detected language: {detected_lang}")
        print(f"    ✓ Pages processed: {page_count}")
        
        return {
            "status": "success",
            "extracted_text": content,
            "detected_language": detected_lang,
            "page_count": page_count,
            "word_count": word_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"OCR extraction failed: {str(e)}"
        }
