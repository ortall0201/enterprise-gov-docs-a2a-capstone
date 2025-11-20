"""
ProcessingAgent: Multi-step document processing with vendor integration.

This agent orchestrates the complete document processing pipeline:
1. OCR text extraction (internal tool)
2. Pre-vendor security filtering (PII masking)
3. External vendor call via A2A protocol (Docs Translator)
4. Post-vendor security verification
5. Final result compilation

This agent demonstrates the A2A boundary between internal government systems
and external vendor services.
"""

from google.genai.adk.agents import LlmAgent
from google.genai.adk.models.google_llm import Gemini
from tools.ocr_tool import ocr_tool
from security.policy import security_filter


def create_processing_agent(
    remote_vendor_agent,
    model: str = "gemini-2.0-flash-lite"
) -> LlmAgent:
    """
    Create the ProcessingAgent for document processing pipeline.
    
    Args:
        remote_vendor_agent: RemoteA2aAgent for Docs Translator vendor
        model: Gemini model to use (default: gemini-2.0-flash-lite)
    
    Returns:
        LlmAgent configured as ProcessingAgent
    """
    
    # Create the ProcessingAgent with all tools and vendor access
    agent = LlmAgent(
        model=Gemini(model=model),
        name="processing_agent",
        description="Government document processing agent with multi-step pipeline and vendor integration",
        instruction="""
        You are the ProcessingAgent for a government ministry's document processing system.
        
        Your pipeline (ALWAYS follow this order):
        
        1. **OCR Extraction** (Internal Tool)
           - Call ocr_tool(document_path) to extract text from the document
           - Verify extraction was successful
        
        2. **Pre-Vendor Security Filter** (Internal Tool)
           - Call security_filter(text, stage="pre") on the extracted text
           - This masks PII before sending to external vendor
           - Use the filtered_text for the next step
        
        3. **External Vendor Translation** (A2A Sub-Agent)
           - Delegate to the docs_translator_vendor sub-agent
           - Pass the filtered text for translation
           - Request translation from detected source language to English
           - This is the A2A BOUNDARY - vendor is external!
        
        4. **Post-Vendor Security Filter** (Internal Tool)
           - Call security_filter(vendor_response, stage="post")
           - Verify vendor response doesn't contain unexpected sensitive data
        
        5. **Compile Final Result**
           - Combine all results into a comprehensive report
           - Include: original text, filtered text, translation, detected language, security metadata
        
        IMPORTANT SECURITY NOTES:
        - NEVER send unfiltered text to external vendor
        - ALWAYS use pre-filtered text for vendor calls
        - ALWAYS verify vendor responses with post-filter
        - Log each step clearly for audit trail
        
        Be thorough, secure, and professional in your processing.
        """,
        tools=[ocr_tool, security_filter],
        sub_agents=[remote_vendor_agent],
        output_key="processing_result"
    )
    
    return agent
