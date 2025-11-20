# 🏢 Enterprise Side - Implementation Guide

**Purpose:** This document explains the enterprise agent architecture, what's currently implemented, and what's needed for production use.

---

## 📊 Current State vs. Production Requirements

### ✅ What's Currently Implemented (POC/Demo)

**Repository:** `enterprise-gov-docs-a2a-capstone`

**Agents:**
- ✅ **IntakeAgent** - Document validation and metadata extraction
- ✅ **ProcessingAgent** - Multi-step pipeline with A2A integration
  - OCR tool (simulated text extraction)
  - Security filter (PII masking with regex patterns)
  - RemoteA2aAgent (A2A client for vendor calls)
  - Post-vendor security verification

**Data Flow (Current POC):**
```
TXT File → OCR (extract text) → Mask PII → Send TEXT to Vendor →
Receive TEXT translation → Verify → Display in memory
```

**Limitations:**
- ❌ Works with plain text files only (not PDFs)
- ❌ Simulated OCR (no real handwriting recognition)
- ❌ Vendor receives/returns TEXT (not PDF)
- ❌ No human approval workflow
- ❌ No long-term memory/logging
- ❌ Translated data stays in memory only (not persisted)
- ❌ No MCP tool integration
- ❌ No guardrails or monitoring beyond basic PII filtering

**What It Proves:**
✅ A2A protocol integration works
✅ RemoteA2aAgent pattern works
✅ Agent card discovery works
✅ Production vendor connection works
✅ PII masking concept works

---

## 🎯 Production Requirements (What Your Colleague Needs)

### Use Case: Government Form Processing with Handwriting Recognition

**Scenario:**
1. Citizen fills out government form by hand
2. Citizen scans form with mobile phone → PDF uploaded to government portal
3. System processes: Handwriting → Digital text → Language detection → Translation
4. Sensitive forms require human approval before A2A call
5. Translated PDF returned to enterprise and stored
6. All A2A transactions logged for audit

### Required Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Mobile Upload (Citizen)                                 │
│ Handwritten form → Mobile scan → PDF upload to gov portal       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Handwriting Recognition (Enterprise OCR)                │
│ PDF with handwriting → OCR MCP Tool → PDF with digital text     │
│ Tool: Document AI / Tesseract / Azure Form Recognizer           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Language Detection (Enterprise)                         │
│ Detect language in PDF → If not target language, proceed        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Classification Check (Enterprise)                       │
│ Is form classified/sensitive?                                   │
│   YES → Human approval required (callback workflow)             │
│   NO  → Proceed automatically                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: PII Masking (Enterprise Security)                       │
│ Mask PII in PDF before sending across A2A boundary             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: A2A Call (Cross-Org Boundary)                          │
│ Enterprise → RemoteA2aAgent → Vendor SaaS                       │
│ Send: PDF (masked)                                              │
│ Receive: PDF (translated)                                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: Storage & Logging (Enterprise)                         │
│ - Store translated PDF in document management system           │
│ - Log A2A transaction to long-term memory                      │
│ - Update form status in database                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: Notification (Enterprise)                              │
│ Notify citizen/case worker that translated form is ready       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Requirements Breakdown

### 1. OCR MCP Tool (Handwriting Recognition)

**Challenge:** Your colleague struggled to "activate" the OCR MCP tool.

**What's Needed:**

#### Option A: MCP Server for OCR (Recommended)
Use Model Context Protocol to integrate external OCR service:

```python
# tools/ocr_mcp_tool.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def create_ocr_mcp_tool():
    """
    Create MCP client for OCR service.

    MCP Server options:
    - Google Document AI MCP server
    - Azure Form Recognizer MCP server
    - Tesseract MCP wrapper
    """
    server_params = StdioServerParameters(
        command="uvx",
        args=["document-ai-mcp-server"]  # Example MCP server
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize and list tools
            await session.initialize()
            tools = await session.list_tools()

            return session  # Return session for agent to use
```

**MCP Integration in Agent:**
```python
# agents/processing_agent.py
from google.adk.agents import LlmAgent
from google.adk.mcp import MCPToolkit

# Create MCP toolkit for OCR
ocr_mcp = MCPToolkit(
    server_command="uvx",
    server_args=["document-ai-mcp-server"]
)

processing_agent = LlmAgent(
    model=Gemini(model="gemini-2.0-flash"),
    name="processing_agent",
    tools=[
        ocr_mcp,  # MCP-based OCR tool
        security_filter,
        # ... other tools
    ]
)
```

**Why MCP?**
- ✅ Standard protocol for tool integration
- ✅ Works with external OCR services (Google, Azure, AWS)
- ✅ Handles PDF, images, handwriting
- ✅ Can be swapped without changing agent code

#### Option B: Direct API Integration
```python
# tools/document_ai_tool.py
from google.cloud import documentai_v1 as documentai

def extract_handwriting_from_pdf(pdf_path: str) -> dict:
    """
    Extract handwriting from scanned PDF using Google Document AI.

    Returns:
        {
            "text": "digitized text",
            "confidence": 0.95,
            "language": "es",
            "output_pdf": "path/to/digital.pdf"
        }
    """
    client = documentai.DocumentProcessorServiceClient()

    # Read PDF
    with open(pdf_path, "rb") as pdf_file:
        pdf_content = pdf_file.read()

    # Process with Document AI
    request = documentai.ProcessRequest(
        name="projects/PROJECT/locations/LOCATION/processors/PROCESSOR_ID",
        raw_document=documentai.RawDocument(
            content=pdf_content,
            mime_type="application/pdf"
        )
    )

    result = client.process_document(request=request)

    # Extract text
    text = result.document.text

    # Create PDF with digital text overlay
    output_pdf = create_searchable_pdf(pdf_path, result.document)

    return {
        "text": text,
        "confidence": result.document.confidence,
        "language": detect_language(text),
        "output_pdf": output_pdf
    }
```

**Colleague's Issue:** "Didn't know how to activate this inside the code"
- Likely needs MCP server setup
- Or API credentials configuration
- See ADK MCP documentation: Day 5 materials

---

### 2. PDF Handling (Input and Output)

**Current Implementation:** Works with TXT files only
**Required:** PDF → PDF workflow

#### PDF Input Processing
```python
# tools/pdf_handler.py
import PyPDF2
from pathlib import Path

def validate_pdf(pdf_path: str) -> dict:
    """
    Validate PDF and extract metadata.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        return {
            "valid": True,
            "pages": len(reader.pages),
            "encrypted": reader.is_encrypted,
            "metadata": reader.metadata,
            "file_size": Path(pdf_path).stat().st_size
        }

def pdf_to_images(pdf_path: str) -> list[str]:
    """
    Convert PDF pages to images for OCR processing.
    """
    from pdf2image import convert_from_path

    images = convert_from_path(pdf_path, dpi=300)
    image_paths = []

    for i, image in enumerate(images):
        img_path = f"/tmp/page_{i}.png"
        image.save(img_path, "PNG")
        image_paths.append(img_path)

    return image_paths
```

#### PDF Output from Vendor

**Key Question:** "What about the translated file? Does it go back to the enterprise? How? Where is it stored?"

**Answer:** The vendor returns the translated PDF via A2A response:

```python
# The A2A response structure
{
    "translated_pdf": "base64_encoded_pdf_content",
    "metadata": {
        "source_language": "es",
        "target_language": "en",
        "page_count": 3,
        "confidence": 0.95
    }
}
```

**Storage Implementation:**
```python
# tools/document_storage.py
import base64
from pathlib import Path
from datetime import datetime

def store_translated_pdf(
    pdf_content: str,  # base64 encoded
    original_filename: str,
    document_id: str
) -> str:
    """
    Store translated PDF in enterprise document management system.

    Returns:
        str: Path to stored PDF
    """
    # Decode base64
    pdf_bytes = base64.b64decode(pdf_content)

    # Generate storage path
    storage_dir = Path("/enterprise/translated_documents")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{document_id}_{timestamp}_translated.pdf"
    output_path = storage_dir / output_filename

    # Write to disk
    output_path.write_bytes(pdf_bytes)

    # Update database record
    update_document_record(
        document_id=document_id,
        translated_path=str(output_path),
        status="translated"
    )

    return str(output_path)
```

---

### 3. Human Approval Workflow (Callbacks)

**Requirement:** Sensitive forms need human approval before A2A call.

**Implementation:** Use ADK callback pattern (Day 4/5)

```python
# agents/processing_agent_with_approval.py
from google.adk.agents import LlmAgent
from google.adk.callbacks import HumanApprovalCallback

def classify_document(document_id: str, content: str) -> dict:
    """
    Classify document to determine if human approval needed.

    Returns:
        {
            "classification": "classified" | "public",
            "requires_approval": True | False,
            "reason": "Contains classified markings"
        }
    """
    # Check for classification markers
    classified_keywords = [
        "CLASSIFIED", "SECRET", "CONFIDENTIAL",
        "TOP SECRET", "RESTRICTED"
    ]

    for keyword in classified_keywords:
        if keyword in content.upper():
            return {
                "classification": "classified",
                "requires_approval": True,
                "reason": f"Contains '{keyword}' marking"
            }

    return {
        "classification": "public",
        "requires_approval": False,
        "reason": "No classification markers found"
    }

# Agent with human approval callback
processing_agent = LlmAgent(
    model=Gemini(model="gemini-2.0-flash"),
    name="processing_agent_with_approval",
    instruction="""
    Before sending any document to external vendor via A2A:

    1. Classify the document using classify_document tool
    2. If requires_approval is True:
       - Call request_human_approval with document details
       - WAIT for approval before proceeding
       - If denied, STOP and log denial
    3. If approved or no approval needed:
       - Proceed with A2A vendor call

    NEVER send classified documents without human approval.
    """,
    tools=[
        classify_document,
        # ... other tools
    ],
    callbacks=[
        HumanApprovalCallback(
            approval_required_condition=lambda state: state.get("requires_approval", False),
            approval_message="Classified document requires approval before A2A call",
            approvers=["security_officer@gov.example"]
        )
    ]
)
```

**Callback UI Integration:**
```python
# For ADK Web UI, callbacks appear as:
# "⏸️ Waiting for approval from security_officer@gov.example"
# User can click "Approve" or "Deny" with reason
```

---

### 4. Long-Term Memory for A2A Transaction Logging

**Requirement:** Log which files were sent via A2A call for audit trail.

**Implementation:** Use ADK Memory Service

```python
# memory/a2a_transaction_logger.py
from google.adk.memory import MemoryService
from datetime import datetime
import json

class A2ATransactionLogger:
    """
    Long-term memory for A2A transaction audit trail.
    """

    def __init__(self, memory_service: MemoryService):
        self.memory = memory_service
        self.namespace = "a2a_transactions"

    async def log_transaction(
        self,
        document_id: str,
        vendor_name: str,
        request_payload: dict,
        response_payload: dict,
        status: str
    ):
        """
        Log A2A transaction for audit.
        """
        transaction_record = {
            "timestamp": datetime.now().isoformat(),
            "document_id": document_id,
            "vendor": vendor_name,
            "vendor_url": "https://docs-translator-a2a.onrender.com",
            "request": {
                "capability": request_payload.get("capability"),
                "parameters": request_payload.get("parameters"),
                "pii_masked": True  # Always true for security
            },
            "response": {
                "status": status,
                "success": status == "success",
                "metadata": response_payload.get("metadata")
            },
            "security_checks": {
                "pre_vendor_filter": "passed",
                "post_vendor_verification": "passed"
            }
        }

        # Store in long-term memory
        await self.memory.store(
            namespace=self.namespace,
            key=f"transaction_{document_id}_{datetime.now().timestamp()}",
            value=json.dumps(transaction_record),
            metadata={
                "document_id": document_id,
                "vendor": vendor_name,
                "timestamp": transaction_record["timestamp"]
            }
        )

    async def get_document_history(self, document_id: str) -> list[dict]:
        """
        Retrieve all A2A transactions for a specific document.
        """
        results = await self.memory.query(
            namespace=self.namespace,
            filter={"document_id": document_id}
        )

        return [json.loads(r.value) for r in results]

    async def get_audit_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """
        Generate audit report of all A2A transactions in date range.
        """
        results = await self.memory.query(
            namespace=self.namespace,
            filter={
                "timestamp": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
        )

        transactions = [json.loads(r.value) for r in results]

        return {
            "total_transactions": len(transactions),
            "successful": sum(1 for t in transactions if t["response"]["success"]),
            "failed": sum(1 for t in transactions if not t["response"]["success"]),
            "vendors_used": list(set(t["vendor"] for t in transactions)),
            "documents_processed": list(set(t["document_id"] for t in transactions)),
            "transactions": transactions
        }
```

**Integration with Processing Agent:**
```python
# agents/processing_agent.py (enhanced)
from memory.a2a_transaction_logger import A2ATransactionLogger

processing_agent = LlmAgent(
    # ... agent config

    # Add memory service
    memory_service=MemoryService(
        provider="sqlite",  # or "postgresql", "bigquery"
        connection_string="sqlite:///a2a_audit.db"
    )
)

# In the agent's instruction:
"""
After every A2A vendor call:
1. Call log_a2a_transaction with all request/response details
2. Include document_id, vendor name, status
3. This creates audit trail for compliance
"""
```

---

### 5. Monitoring and Guardrails

**Requirements:**
- Monitor A2A calls (latency, errors, rate limits)
- Guardrails to prevent data leaks
- Alert on suspicious activity

#### Monitoring Setup
```python
# monitoring/a2a_monitor.py
from google.adk.telemetry import TelemetryService
from opentelemetry import trace, metrics

class A2AMonitor:
    """
    Monitor A2A calls for performance and security.
    """

    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)

        # Metrics
        self.a2a_call_counter = self.meter.create_counter(
            "a2a_calls_total",
            description="Total A2A calls made"
        )
        self.a2a_latency = self.meter.create_histogram(
            "a2a_latency_seconds",
            description="A2A call latency"
        )
        self.pii_leaks = self.meter.create_counter(
            "pii_leaks_detected",
            description="PII leaks detected in vendor responses"
        )

    async def monitor_a2a_call(
        self,
        vendor_name: str,
        request_data: dict,
        response_data: dict,
        duration: float
    ):
        """
        Monitor A2A call and record metrics.
        """
        # Record metrics
        self.a2a_call_counter.add(
            1,
            {"vendor": vendor_name, "status": "success"}
        )
        self.a2a_latency.record(
            duration,
            {"vendor": vendor_name}
        )

        # Check for PII leaks
        pii_found = self.check_pii_in_response(response_data)
        if pii_found:
            self.pii_leaks.add(1, {"vendor": vendor_name})
            await self.alert_security_team(
                f"PII leak detected in response from {vendor_name}"
            )

    def check_pii_in_response(self, response: dict) -> bool:
        """
        Check if vendor response contains unexpected PII.
        """
        from security.policy import PII_PATTERNS

        response_text = str(response)

        for pattern_name, pattern in PII_PATTERNS.items():
            if pattern.search(response_text):
                return True  # PII found!

        return False
```

#### Guardrails Implementation
```python
# security/guardrails.py
from typing import Any

class A2AGuardrails:
    """
    Enforce security policies on A2A calls.
    """

    def __init__(self):
        self.max_document_size = 10 * 1024 * 1024  # 10MB
        self.allowed_vendors = [
            "docs-translator-a2a.onrender.com"
        ]
        self.rate_limit = 100  # calls per hour

    def validate_request(self, request: dict) -> tuple[bool, str]:
        """
        Validate A2A request before sending.

        Returns:
            (allowed, reason)
        """
        # Check vendor whitelist
        vendor_url = request.get("vendor_url")
        if vendor_url not in self.allowed_vendors:
            return False, f"Vendor {vendor_url} not whitelisted"

        # Check document size
        document_size = len(str(request.get("data", "")))
        if document_size > self.max_document_size:
            return False, f"Document too large: {document_size} bytes"

        # Check PII masking applied
        if not request.get("pii_masked"):
            return False, "PII masking not applied"

        # Check rate limit
        if self.check_rate_limit_exceeded():
            return False, "Rate limit exceeded (100/hour)"

        return True, "Request validated"

    def validate_response(self, response: dict) -> tuple[bool, str]:
        """
        Validate A2A response before accepting.
        """
        # Check for PII leaks
        if self.contains_pii(response):
            return False, "PII detected in vendor response"

        # Check response size
        if len(str(response)) > self.max_document_size:
            return False, "Response too large"

        return True, "Response validated"
```

---

## 🏗️ Recommended Architecture for Production

```
┌──────────────────────────────────────────────────────────────────┐
│ ENTERPRISE AGENT SYSTEM (Production)                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. IntakeAgent                                             │ │
│  │    - Receive PDF from citizen portal                       │ │
│  │    - Validate PDF format and size                          │ │
│  │    - Extract metadata                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 2. OCRAgent (with MCP)                                     │ │
│  │    - MCP Tool: Document AI / Tesseract                     │ │
│  │    - Extract handwriting → digital text                    │ │
│  │    - Output: PDF with searchable text layer                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 3. ClassificationAgent                                     │ │
│  │    - Detect language                                       │ │
│  │    - Classify sensitivity (public/classified)              │ │
│  │    - Determine if human approval needed                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 4. ApprovalAgent (with Callback)                           │ │
│  │    - If classified: Request human approval                 │ │
│  │    - Wait for security officer decision                    │ │
│  │    - Log approval/denial                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 5. SecurityAgent                                           │ │
│  │    - Mask PII in PDF before A2A                           │ │
│  │    - Apply guardrails                                      │ │
│  │    - Validate vendor whitelist                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 6. TranslationAgent (with RemoteA2aAgent)                  │ │
│  │    - Call vendor via A2A                                   │ │
│  │    - Send: PDF (masked)                                    │ │
│  │    - Receive: PDF (translated)                             │ │
│  │    - Monitor call (latency, errors)                        │ │
│  │    - Log transaction to long-term memory                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 7. StorageAgent                                            │ │
│  │    - Store translated PDF in DMS                           │ │
│  │    - Update database records                               │ │
│  │    - Generate audit logs                                   │ │
│  │    - Notify citizen/case worker                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Supporting Services:                                             │
│  - Long-term Memory (SQLite/PostgreSQL/BigQuery)                 │
│  - Monitoring (OpenTelemetry → Cloud Monitoring)                 │
│  - Document Storage (GCS/S3/Azure Blob)                          │
│  - Callback UI (ADK Web UI or custom portal)                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📝 Implementation Roadmap

### Phase 1: Core Functionality (Your Colleague's Priority)
1. ✅ **OCR MCP Integration**
   - Set up Document AI MCP server
   - Test handwriting recognition
   - PDF → Digital PDF conversion

2. ✅ **PDF Handling**
   - Input: Validate and process scanned PDFs
   - Output: Store translated PDFs
   - Base64 encoding for A2A transfer

3. ✅ **Language Detection**
   - Detect source language in PDF
   - Trigger translation workflow if needed

### Phase 2: Security & Compliance
4. ✅ **Classification System**
   - Detect classified markings
   - Route to appropriate approval workflow

5. ✅ **Human Approval Callbacks**
   - Implement ADK callback pattern
   - UI for security officer review
   - Approval/denial logging

6. ✅ **Guardrails**
   - Vendor whitelist
   - Document size limits
   - Rate limiting
   - PII leak detection

### Phase 3: Observability & Audit
7. ✅ **Long-term Memory**
   - A2A transaction logging
   - Audit trail generation
   - Document history tracking

8. ✅ **Monitoring**
   - OpenTelemetry integration
   - Latency tracking
   - Error alerting
   - Dashboard creation

### Phase 4: Production Hardening
9. ✅ **Document Storage**
   - Enterprise DMS integration
   - Backup and retention policies
   - Access controls

10. ✅ **Error Handling**
    - Retry logic for A2A failures
    - Fallback workflows
    - User notifications

---

## 🆚 Current POC vs. Production Needs

| Feature | Current POC | Production Needed |
|---------|-------------|-------------------|
| **Input Format** | TXT files | PDF (scanned with handwriting) |
| **OCR** | Simulated text extraction | Real handwriting recognition (MCP tool) |
| **Language** | Hardcoded Spanish | Auto-detect any language |
| **Vendor Communication** | Send/receive TEXT | Send/receive PDF (base64) |
| **Human Approval** | ❌ None | ✅ Callback for classified docs |
| **Storage** | ❌ Memory only | ✅ Persistent DMS storage |
| **Logging** | ❌ Console only | ✅ Long-term memory audit trail |
| **Monitoring** | ❌ Basic logs | ✅ OpenTelemetry + dashboards |
| **Guardrails** | ❌ Basic PII filter | ✅ Multi-layer security |
| **Error Handling** | ❌ Fails on error | ✅ Retry + fallback workflows |

---

## 🚀 Quick Start for Your Colleague

### 1. Review Current POC
```bash
# Clone and test existing POC
cd enterprise-gov-docs-a2a-capstone
python main.py  # See how A2A works
```

### 2. Study Key Patterns
- **RemoteA2aAgent usage**: `tools/vendor_connector.py`
- **Agent structure**: `agents/processing_agent.py`
- **Security filter**: `security/policy.py`

### 3. Start Building Production Features

**Priority 1: OCR MCP Tool**
```bash
# Install MCP tools
pip install mcp

# Set up Document AI MCP server
# Follow: ADK Day 5 - MCP Integration guide
```

**Priority 2: PDF Handling**
```bash
pip install PyPDF2 pdf2image pytesseract
# Implement pdf_handler.py
```

**Priority 3: Callbacks**
```python
# Study ADK callback documentation
# Implement human approval workflow
```

---

## 📚 References

**ADK Documentation:**
- Day 4: Memory & State Management
- Day 5: MCP Tool Integration, Callbacks

**External Services:**
- Google Document AI (handwriting OCR)
- Azure Form Recognizer (alternative)
- Tesseract (open-source OCR)

**Security:**
- OWASP Top 10 for API security
- PII detection patterns
- Classification handling best practices

---

## 🤝 Collaboration Notes

**What Already Works:**
- ✅ A2A protocol integration (proven with production vendor)
- ✅ RemoteA2aAgent pattern (reusable)
- ✅ Security filter concept (extend for PDFs)
- ✅ ADK Web UI for testing (keep using this!)

**What Your Colleague Should Build:**
- 🔨 OCR MCP tool (priority!)
- 🔨 PDF input/output handling
- 🔨 Human approval callback
- 🔨 Long-term memory logging
- 🔨 Document storage integration

**Avoid Duplication:**
- Don't rebuild RemoteA2aAgent (use existing `vendor_connector.py`)
- Don't rebuild basic agent structure (extend existing)
- Don't rebuild A2A connection logic (it works!)

**Extend & Enhance:**
- Add OCR MCP on top of existing IntakeAgent
- Enhance ProcessingAgent with PDF support
- Add new agents (ClassificationAgent, StorageAgent)
- Integrate callbacks into existing workflow

---

**Last Updated:** 2025-11-20
**Status:** Production roadmap defined
**Next Steps:** Implement OCR MCP tool and PDF handling
