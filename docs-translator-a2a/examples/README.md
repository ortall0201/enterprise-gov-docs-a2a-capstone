# Examples

This directory contains example scripts demonstrating how to use the Docs Translator A2A service.

## Prerequisites

1. **A2A service must be running:**
   ```bash
   cd docs-translator-a2a
   python src/a2a_server.py
   # Service starts on http://localhost:8001
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Examples

### 1. ADK Consumer (`adk_consumer.py`)

**Purpose:** Demonstrates ADK → A2A → CrewAI integration

**What it tests:**
- Connection to A2A service via RemoteA2aAgent
- Simple text translation
- Translation with masked PII (VaaS pattern)
- Full birth certificate translation

**Run:**
```bash
python examples/adk_consumer.py
```

**Expected output:**
```
╔==========================================================╗
║  ADK → A2A → CrewAI Integration Test                    ║
║  Cross-Framework VaaS Demonstration                     ║
╚==========================================================╝

Testing A2A Connection to Docs Translator
✓ Connected to: http://localhost:8001
✓ Agent name: docs_translator

Test 1: Simple Text Translation (Spanish → English)
...
✓ ALL TESTS PASSED!
```

### 2. Direct HTTP Test (`direct_http_test.py`)

**Purpose:** Test A2A endpoints using direct HTTP requests (no ADK required)

**What it tests:**
- GET /.well-known/agent-card.json
- GET /health
- POST /invoke

**Run:**
```bash
python examples/direct_http_test.py
```

**Use case:** Debugging or testing from non-Python environments

## Integration with Enterprise System

To integrate with your enterprise ADK system:

```python
# In your enterprise-gov-docs-a2a-capstone repo
from adk.agents import RemoteA2aAgent

# Connect to Docs Translator A2A service
translator = RemoteA2aAgent(
    name="docs_translator",
    url="http://localhost:8001"  # or your deployment URL
)

# Use in your workflow
result = translator.run(
    capability="translate_document",
    text=filtered_document,  # Already PII-filtered
    source_language="es",
    target_language="en"
)
```

## Troubleshooting

**Connection refused:**
- Make sure A2A service is running on port 8001
- Check firewall settings

**Translation fails:**
- Verify OPENAI_API_KEY is set in .env
- Check service logs for errors

**PII not preserved:**
- Verify masked patterns use ***, ****, or ***** format
- Check that patterns remain unchanged in translation
