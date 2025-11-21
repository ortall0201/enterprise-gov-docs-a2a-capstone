"""
IntakeAgent: Document validation and metadata extraction.

This agent is responsible for:
1. Receiving document input (path or ID)
2. Validating document exists and is accessible
3. Extracting basic metadata (size, format, timestamp)
4. Preparing document for processing pipeline

This is the entry point for all documents entering the government system.
"""

import os
from datetime import datetime, timezone
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

def create_intake_agent(model: str = "gemini-2.0-flash-lite") -> LlmAgent:
    
    def validate_document(document_path: str) -> dict:
        
        print(f"\n[Tool: validate_document] Validating: {document_path}")
        
        if not os.path.exists(document_path):
            return {
                "status": "error",
                "error_message": f"Document not found: {document_path}"
            }
        
        try:
            file_stats = os.stat(document_path)
            file_size = file_stats.st_size
            
            _, ext = os.path.splitext(document_path)
            file_format = ext.lstrip('.') if ext else "unknown"
            
            doc_id = f"doc_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
            print(f"    ✓ File exists: {file_size} bytes")
            print(f"    ✓ Format: {file_format}")
            print(f"    ✓ Document ID: {doc_id}")
            
            return {
                "status": "success",
                "document_id": doc_id,
                "document_path": document_path,
                "metadata": {
                    "format": file_format,
                    "size_bytes": file_size,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Failed to extract metadata: {str(e)}"
            }

    agent = LlmAgent(
        model=Gemini(model=model),
        name="intake_agent",
        description="Government document intake agent responsible for validation and metadata extraction",
        instruction="""
        You are the IntakeAgent for a government ministry's document processing system.

        Your responsibilities:
        1. Validate incoming documents using the validate_document tool
        2. Extract and report document metadata
        3. Ensure documents are ready for processing
        4. Report any validation errors clearly
        """,
        tools=[validate_document],
        output_key="intake_result"
    )
    
    return agent
