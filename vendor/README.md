# Vendor Simulation Module

This directory contains the **external vendor simulation** for the Enterprise Government Document Processing Capstone project.

## Overview

In a real enterprise deployment, this vendor would be:
- **Owned by a separate organization** (e.g., Docs Translator Inc.)
- **Deployed in a different infrastructure** (separate servers, networks, security domains)
- **Accessed only via A2A protocol** (no direct code access)

For this capstone demonstration, we simulate the vendor locally to show the complete A2A integration pattern.

## Based on Real Vendor

This simulation is based on the actual **Docs Translator** application:
- GitHub: https://github.com/ortall0201/Docs_Translator
- Real-world translation service for government documents
- Uses CrewAI for multi-agent orchestration
- Supports Spanish to English translation

## Architecture

```
vendor/
├── __init__.py                    # Module exports
├── docs_translator_agent.py      # Vendor agent with translation tools
├── vendor_server.py               # A2A server using to_a2a()
└── README.md                      # This file
```

## Running the Vendor Server

Start the vendor A2A server:

```bash
python -m vendor.vendor_server
```

Or programmatically:

```python
from vendor import start_vendor_server

start_vendor_server(host="localhost", port=8001)
```

The server will expose:
- **Agent Card**: `http://localhost:8001/.well-known/agent-card.json`
- **Streaming Endpoint**: `http://localhost:8001/streams`

## Agent Capabilities

The Docs Translator agent provides:

### Tools

1. **translate_document()**
   - Translates document text between languages
   - Parameters: text, source_language, target_language, document_type
   - Returns: translated_text, metrics, confidence

2. **validate_translation()**
   - Validates translation quality
   - Parameters: original_text, translated_text, languages
   - Returns: quality_score, validation checks

### Supported Features

- Spanish → English translation
- Birth certificate formatting
- PII preservation (keeps masked fields as-is)
- Quality validation
- Professional, official tone

## A2A Integration

The vendor agent is exposed via A2A using:

```python
from adk.a2a import to_a2a
vendor_agent = create_docs_translator_agent()
a2a_app = to_a2a(vendor_agent)
```

Government ministry consumes via:

```python
from adk.a2a import RemoteA2aAgent
remote_vendor = RemoteA2aAgent(
    name="docs_translator_vendor",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)
```

## Security Boundaries

The vendor operates in a **separate security domain**:

- **Input**: Receives PII-filtered documents from government
- **Processing**: Performs translation in isolated environment
- **Output**: Returns translated documents
- **No access to**: Internal government systems, unfiltered PII, policy logic

## Configuration

Set environment variables in `.env`:

```bash
VENDOR_SERVER_HOST=localhost
VENDOR_SERVER_PORT=8001
GOOGLE_API_KEY=your_api_key_here
```

## Testing Vendor Connection

```python
from tools.vendor_connector import test_vendor_connection

# Test if vendor is reachable
result = test_vendor_connection()
if result["status"] == "success":
    print("Vendor is online!")
```

## Real vs. Simulated

| Aspect | Real Vendor | This Simulation |
|--------|-------------|-----------------|
| Deployment | Separate infrastructure | Local process |
| Ownership | External organization | Same project |
| Code Access | None (black box) | Full source available |
| A2A Protocol | ✓ Yes | ✓ Yes |
| Agent Card | ✓ Yes | ✓ Yes |
| Translation | Real APIs (Google, DeepL) | Mock implementation |
| Scaling | Production-grade | Single instance |

## Key Takeaways

This simulation demonstrates:

1. **A2A Protocol**: Standard agent-to-agent communication
2. **Security Boundaries**: Clear separation between government and vendor
3. **RemoteA2aAgent**: Consumer-side proxy for external agents
4. **to_a2a()**: Provider-side A2A service exposure
5. **Agent Cards**: Self-describing agent capabilities

The patterns shown here are **production-ready** and used in real cross-organizational AI agent integrations.
