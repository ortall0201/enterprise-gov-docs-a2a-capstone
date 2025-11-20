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


def validate_document(document_path: str) -> dict:
    """
    Validate document and extract metadata.

    This is an internal, trusted tool that performs:
    - File existence check
    - Format validation
    - Metadata extraction

    Args:
        document_path: Path to the document file

    Returns:
        dict: Validation result with metadata
            {
                "status": "success" | "error",
                "document_id": str,
                "document_path": str,
                "metadata": {
                    "format": str,
                    "size_bytes": int,
                    "timestamp": str
                },
                "error_message": str (if error)
            }
    """
    print(f"\n[Tool: validate_document] Validating: {document_path}")

    # Check if file exists
    if not os.path.exists(document_path):
        return {
            "status": "error",
            "error_message": f"Document not found: {document_path}"
        }

    # Extract metadata
    try:
        file_stats = os.stat(document_path)
        file_size = file_stats.st_size

        # Determine format from extension
        _, ext = os.path.splitext(document_path)
        file_format = ext.lstrip('.') if ext else "unknown"

        # Generate document ID
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


# Create the IntakeAgent (for ADK Web UI)
agent = LlmAgent(
    model=Gemini(model="gemini-2.0-flash-lite"),
    name="intake_agent",
    description="Government document intake agent responsible for validation and metadata extraction",
    instruction="""
    You are the IntakeAgent for a government ministry's document processing system.

    Your responsibilities:
    1. Validate incoming documents using the validate_document tool
    2. Extract and report document metadata
    3. Ensure documents are ready for processing
    4. Report any validation errors clearly

    When you receive a document path:
    1. Call validate_document(document_path)
    2. If successful, report the document_id and metadata
    3. If failed, explain the error to the user
    4. Always be clear and professional in your responses

    Remember: You are the first line of quality control for government documents.
    """,
    tools=[validate_document],
    output_key="intake_result"
)
