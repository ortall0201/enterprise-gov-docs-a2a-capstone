# Docs Translator A2A VaaS Service

This service wraps the Docs Translator CrewAI agents with Google ADK A2A (Agent-to-Agent) protocol, enabling cross-framework integration as a **Vendor-as-a-Service (VaaS)**.

## Architecture

```
Enterprise System (ADK)
    ↓ A2A Protocol
Docs Translator A2A Service (this)
    ↓ CrewAI orchestration
Translation via OpenAI/GCP
```

## Key Features

- ✅ **A2A Protocol Compliant**: Exposes Agent Card and standard endpoints
- ✅ **CrewAI Integration**: Uses CrewAI for agent orchestration
- ✅ **Multi-language Support**: Spanish, English, Hebrew, Polish, Ukrainian, Russian
- ✅ **Framework Agnostic**: ADK consumers can call CrewAI providers
- ✅ **VaaS Model**: Enterprise controls PII filtering; vendor provides capabilities

## Quick Start

### 1. Installation

```bash
cd docs-translator-a2a
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Service

```bash
python src/a2a_server.py
# Service starts on http://localhost:8001
```

### 4. Verify A2A Agent Card

```bash
curl http://localhost:8001/.well-known/agent-card.json
```

### 5. Test from ADK Consumer

See `examples/adk_consumer.py` for integration example.

## A2A Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/.well-known/agent-card.json` | GET | Agent Card (ADK discovers capabilities here) |
| `/invoke` | POST | Non-streaming translation |
| `/stream` | POST | Streaming translation (SSE) |
| `/health` | GET | Health check |

## API Usage

### Translate Document

```python
# From ADK consumer
from adk.agents import RemoteA2aAgent

translator = RemoteA2aAgent(
    name="docs_translator",
    url="http://localhost:8001"
)

result = translator.run(
    capability="translate_document",
    text="Certificado de Nacimiento...",
    source_language="es",
    target_language="en",
    document_type="birth_certificate"
)
```

### Direct HTTP Request

```bash
curl -X POST http://localhost:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "translate_document",
    "parameters": {
      "text": "Hola mundo",
      "source_language": "es",
      "target_language": "en",
      "document_type": "general"
    }
  }'
```

## VaaS Security Model

This service implements the VaaS pattern:

1. **Enterprise controls PII filtering** (before A2A call)
2. **Vendor receives sanitized data** (across A2A boundary)
3. **Translation happens on sanitized text** (vendor never sees real PII)
4. **Enterprise reconstructs final output** (after A2A response)

## Deployment

### Docker

```bash
docker build -t docs-translator-a2a .
docker run -p 8001:8001 --env-file .env docs-translator-a2a
```

### Docker Compose

```bash
docker-compose up
```

### Cloud Deployment

This service can be deployed to:
- Google Cloud Run
- AWS ECS/Fargate
- Azure Container Instances
- Render.com
- Heroku

See `Dockerfile` for containerization.

## Development

### Run Tests

```bash
pytest tests/
```

### Project Structure

```
docs-translator-a2a/
├── src/
│   ├── a2a_server.py         # FastAPI server with A2A endpoints
│   ├── crew_agent.py         # CrewAI agent implementation
│   ├── agent_card.py         # Agent Card schema
│   ├── transformers.py       # A2A ↔ CrewAI format conversion
│   └── tools/
│       ├── real_translation.py  # OpenAI/GCP translation
│       └── validation.py        # Quality checks
├── tests/                    # Unit and integration tests
├── examples/                 # Usage examples
└── requirements.txt
```

## Relation to Production SaaS

This A2A service is **separate** from the production Docs Translator SaaS:

- **Production SaaS**: `https://docs-translator.onrender.com` (FastAPI + direct OpenAI)
- **A2A VaaS Service**: This repo (FastAPI + CrewAI + A2A protocol)

The production SaaS remains untouched. This service demonstrates cross-framework integration for the VaaS model.

## License

See parent repository license.

## Support

For issues or questions about A2A integration, see the main `enterprise-gov-docs-a2a-capstone` repository.
