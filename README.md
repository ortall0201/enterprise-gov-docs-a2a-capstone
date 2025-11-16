# Enterprise Government Document Processing with A2A

**Capstone Project**: Multi-agent document processing system demonstrating Agent2Agent (A2A) protocol for cross-organizational integration using Google Agent Development Kit (ADK).

## Overview

This project demonstrates an **enterprise-grade government document processing system** that integrates with external vendors via the **Agent2Agent (A2A) protocol**. It showcases:

- **Multi-agent orchestration** using Google ADK
- **Cross-organizational boundaries** with A2A protocol
- **Security controls** with PII filtering at organizational boundaries
- **Real-world use case**: Spanish birth certificate translation service

### Based On

- **Course**: Kaggle 5-Day AI Agents Intensive (Day 5: A2A Communication)
- **Vendor**: [Docs Translator](https://github.com/ortall0201/Docs_Translator) - Real translation service
- **Framework**: Google Agent Development Kit (ADK) v0.8.0+
- **License**: Apache 2.0

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  GOVERNMENT MINISTRY (Internal Secure Environment)           │
│                                                               │
│  ┌────────────────┐                                          │
│  │ IntakeAgent    │  Validates documents,                    │
│  │                │  extracts metadata                       │
│  └───────┬────────┘                                          │
│          │                                                    │
│          ▼                                                    │
│  ┌────────────────┐                                          │
│  │ProcessingAgent │  Multi-step pipeline:                    │
│  │                │  1. OCR extraction                       │
│  │  Tools:        │  2. PII filtering (pre-vendor)           │
│  │  - ocr_tool    │  3. A2A vendor call ─────────────┐       │
│  │  - security    │  4. Security verification        │       │
│  │    _filter     │  5. Final compilation            │       │
│  │                │                                  │       │
│  │  Sub-agents:   │                                  │       │
│  │  - RemoteA2a   │                                  │       │
│  │    Agent       │                                  │       │
│  └────────────────┘                                  │       │
│                                                      │       │
│                      [PII FILTERED DATA ONLY]       │       │
└──────────────────────────────────────────────────────┼───────┘
                                                       │
                                          A2A PROTOCOL │
                                                       │
┌──────────────────────────────────────────────────────┼───────┐
│  EXTERNAL VENDOR (Separate Organization)            │       │
│                                                      ▼       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Docs Translator Vendor Agent                          │ │
│  │                                                        │ │
│  │  Exposed via to_a2a():                                 │ │
│  │  - Agent Card: /.well-known/agent-card.json           │ │
│  │  - Streaming: /streams                                 │ │
│  │                                                        │ │
│  │  Tools:                                                │ │
│  │  - translate_document()                                │ │
│  │  - validate_translation()                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Project Structure

```
enterprise-gov-docs-a2a-capstone/
├── agents/                      # Internal government agents
│   ├── __init__.py
│   ├── intake_agent.py         # Document validation & metadata extraction
│   └── processing_agent.py     # Multi-step processing with A2A integration
│
├── tools/                       # Agent tools
│   ├── __init__.py
│   ├── ocr_tool.py             # OCR text extraction
│   └── vendor_connector.py     # RemoteA2aAgent creation for vendor
│
├── security/                    # Security & PII filtering
│   ├── __init__.py
│   └── policy.py               # PII detection, masking, verification
│
├── vendor/                      # External vendor simulation
│   ├── __init__.py
│   ├── docs_translator_agent.py  # Vendor agent with translation tools
│   ├── vendor_server.py          # A2A server using to_a2a()
│   └── README.md                 # Vendor documentation
│
├── samples/                     # Sample documents
│   └── sample_document.txt     # Spanish birth certificate with PII
│
├── main.py                      # Main demo script
├── demo_notebook.ipynb          # Interactive Jupyter demo
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── LICENSE                      # Apache 2.0 license
└── README.md                    # This file
```

## Setup

### Prerequisites

- Python 3.11+
- Google API Key ([Get one here](https://aistudio.google.com/app/apikey))
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ortall0201/enterprise-gov-docs-a2a-capstone.git
   cd enterprise-gov-docs-a2a-capstone
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set your GOOGLE_API_KEY
   ```

## Usage

### Option 1: Run Main Demo Script

```bash
python main.py
```

This runs the complete workflow:
1. Document intake validation
2. Multi-step processing with A2A integration
3. Full security and translation pipeline

### Option 2: Interactive Jupyter Notebook

```bash
jupyter notebook demo_notebook.ipynb
```

Step-by-step walkthrough with code cells for each stage.

### Option 3: Run with Vendor Server (Full A2A)

**Terminal 1** - Start vendor server:
```bash
python -m vendor.vendor_server
```

**Terminal 2** - Run demo:
```bash
python main.py
```

The vendor server exposes:
- Agent Card: `http://localhost:8001/.well-known/agent-card.json`
- Streaming: `http://localhost:8001/streams`

## Key Components

### 1. IntakeAgent

**Purpose**: First stage document validation

**Tools**:
- `validate_document()`: Checks file existence, extracts metadata, generates document ID

**Output**: Validation result with document metadata

```python
from agents import create_intake_agent
intake_agent = create_intake_agent()
```

### 2. ProcessingAgent

**Purpose**: Multi-step processing pipeline with A2A vendor integration

**Tools**:
- `ocr_tool`: Extract text from documents
- `security_filter`: Mask PII before vendor calls, verify after

**Sub-agents**:
- `RemoteA2aAgent`: A2A client connecting to external vendor

**Pipeline**:
1. OCR extraction (internal)
2. Pre-vendor security filtering (PII masking)
3. **A2A vendor call** (cross-organizational boundary)
4. Post-vendor security verification
5. Final result compilation

```python
from agents import create_processing_agent
processing_agent = create_processing_agent()
```

### 3. Security Layer

**Purpose**: PII detection and filtering at organizational boundaries

**Capabilities**:
- Detect: National IDs, SSN, phone, email, credit cards, DOB, passports
- Mask: Replace PII with secure placeholders
- Verify: Check vendor responses don't leak PII

```python
from security import security_filter

# Mask PII
result = security_filter(text, mode="mask")

# Verify no PII
result = security_filter(text, mode="verify")
```

### 4. A2A Integration

**Consumer Side** (Government):
```python
from tools import create_remote_vendor_agent

# Create RemoteA2aAgent pointing to vendor
remote_vendor = create_remote_vendor_agent(
    vendor_host="localhost",
    vendor_port=8001
)

# Use as sub-agent in ProcessingAgent
agent = LlmAgent(
    ...,
    sub_agents=[remote_vendor]
)
```

**Provider Side** (Vendor):
```python
from adk.a2a import to_a2a
from vendor import create_docs_translator_agent

# Create vendor agent
vendor_agent = create_docs_translator_agent()

# Expose via A2A
a2a_app = to_a2a(vendor_agent)

# Run server
import uvicorn
uvicorn.run(a2a_app, host="localhost", port=8001)
```

## A2A Protocol Details

### What is A2A?

**Agent2Agent (A2A)** is a standard protocol for **cross-organizational agent communication**. It enables:
- Agents from different organizations to collaborate
- Secure boundaries between security domains
- Self-describing agent capabilities via Agent Cards
- Standard REST/streaming interfaces

### Why A2A for This Project?

In government/enterprise scenarios:
- **Government ministry** and **external vendor** are separate organizations
- **Security boundaries** require clear separation
- **PII filtering** must happen before data crosses organizational lines
- **Vendor capabilities** must be discoverable (Agent Card)

### A2A Components Used

| Component | Purpose | Location |
|-----------|---------|----------|
| `RemoteA2aAgent` | Consumer-side proxy for external agents | `tools/vendor_connector.py` |
| `to_a2a()` | Converts ADK agent to A2A service | `vendor/vendor_server.py` |
| Agent Card | JSON metadata at `/.well-known/agent-card.json` | Auto-generated by `to_a2a()` |
| Streaming API | `/streams` endpoint for agent communication | Auto-generated by `to_a2a()` |

## Security

### PII Protection

The security layer provides comprehensive PII protection:

**Detected PII Types**:
- National IDs (Spanish format: 123-45-6789-X)
- Social Security Numbers
- Phone numbers (international formats)
- Email addresses
- Credit card numbers
- Dates of birth
- Passport numbers

**Masking Strategy**:
- Emails: Show first char + domain (e.g., `m*************@ejemplo.es`)
- National IDs: Show last 4 chars (e.g., `***-**-****-X`)
- Dates: Mask day/month, keep year (e.g., `XX de XXXX, 1990`)

**Verification**:
- Post-vendor responses checked for PII leakage
- Threshold-based safety checks
- Logging of all security events

### Security Boundaries

```
┌─────────────┐         ┌─────────────┐
│  Government │  A2A    │   Vendor    │
│             ├────────→│             │
│   [Agent]   │         │   [Agent]   │
│             │←────────┤             │
└─────────────┘         └─────────────┘
     ↑   ↓                   ↑   ↓
  PII Filter              No Direct
  Pre/Post                Access to
  Vendor                  Gov Data
```

## Capstone Objectives

This project demonstrates all key Day 5 concepts:

✅ **Multi-agent orchestration**: IntakeAgent → ProcessingAgent workflow
✅ **A2A protocol integration**: RemoteA2aAgent + to_a2a()
✅ **Cross-organizational boundaries**: Government ↔ Vendor separation
✅ **Agent Cards**: Self-describing agent capabilities
✅ **Security controls**: PII filtering at boundaries
✅ **Tool integration**: OCR, security_filter, translation
✅ **Sub-agent delegation**: ProcessingAgent → RemoteA2aAgent
✅ **Real-world use case**: Government document translation
✅ **Production patterns**: Proper error handling, logging, validation

## Development

### Running Tests

```bash
# Test vendor connectivity
python -c "from tools.vendor_connector import test_vendor_connection; print(test_vendor_connection())"

# Test PII filtering
python -c "from security import security_filter; print(security_filter('SSN: 123-45-6789', mode='mask'))"
```

### Adding New Tools

1. Create tool function in `tools/` directory
2. Add to agent's `tools` parameter in `agents/`
3. Document in agent's instructions

### Adding New Agents

1. Create agent module in `agents/`
2. Define `create_<agent_name>_agent()` factory function
3. Export from `agents/__init__.py`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key (required) | - |
| `VENDOR_SERVER_HOST` | Vendor A2A server host | `localhost` |
| `VENDOR_SERVER_PORT` | Vendor A2A server port | `8001` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Troubleshooting

### "Vendor server not reachable"

**Solution**: Start the vendor server first:
```bash
python -m vendor.vendor_server
```

### "GOOGLE_API_KEY not configured"

**Solution**: Set your API key in `.env`:
```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

Get a key at: https://aistudio.google.com/app/apikey

### Import errors

**Solution**: Ensure you're in the project root and dependencies are installed:
```bash
pip install -r requirements.txt
```

## References

- [Google ADK Documentation](https://googleapis.github.io/python-genai/adk/)
- [A2A Protocol Specification](https://github.com/googleapis/python-genai/tree/main/google/genai/adk/a2a)
- [Kaggle AI Agents Intensive](https://www.kaggle.com/)
- [Docs Translator (Real Vendor)](https://github.com/ortall0201/Docs_Translator)

## Contributing

This is a capstone project for educational purposes. For improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Kaggle**: AI Agents Intensive course materials
- **Google**: Agent Development Kit (ADK) framework
- **Docs Translator**: Real-world vendor inspiration

---

**Built with** ❤️ **for the Kaggle AI Agents Intensive Capstone**
