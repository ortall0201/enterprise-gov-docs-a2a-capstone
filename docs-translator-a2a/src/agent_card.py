"""
Agent Card for Docs Translator A2A Service.

The Agent Card is the "front door" for A2A protocol - ADK RemoteA2aAgent
reads this JSON to discover the agent's capabilities.

Based on Day 5a: Agent-to-Agent Communication from Kaggle AI Agents Intensive.
"""

import os
from typing import Dict, Any

def get_agent_card() -> Dict[str, Any]:
    """
    Generate Agent Card JSON for A2A protocol.

    This is served at /.well-known/agent-card.json and tells ADK consumers:
    - What capabilities this agent provides
    - What parameters each capability accepts
    - Which endpoints to call

    Returns:
        Agent Card dictionary (JSON serializable)
    """
    return {
        "schema_version": "1.0",
        "name": "docs_translator",
        "version": "1.0.0",
        "description": (
            "Professional document translation service for government and official documents. "
            "Supports multiple languages including Spanish, English, Hebrew, Polish, Ukrainian, "
            "and Russian. Preserves document formatting and handles PII-filtered content appropriately."
        ),

        "capabilities": [
            {
                "name": "translate_document",
                "description": (
                    "Translate a document from source language to target language while "
                    "preserving formatting, structure, and masked PII patterns. Suitable for "
                    "official government documents like birth certificates, passports, and forms."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": (
                                "Document text to translate. Can include masked PII "
                                "(e.g., ***-**-****-X) which will be preserved unchanged."
                            )
                        },
                        "source_language": {
                            "type": "string",
                            "description": "Source language code (ISO 639-1)",
                            "enum": ["es", "en", "pl", "he", "uk", "ru", "fr", "de", "it"]
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code (ISO 639-1)",
                            "enum": ["es", "en", "pl", "he", "uk", "ru", "fr", "de", "it"]
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Type of document being translated",
                            "enum": [
                                "birth_certificate",
                                "passport",
                                "visa",
                                "tax_form",
                                "medical_record",
                                "legal_document",
                                "general"
                            ],
                            "default": "general"
                        }
                    },
                    "required": ["text", "source_language", "target_language"]
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "translated_text": {
                            "type": "string",
                            "description": "Translated document text with preserved formatting"
                        },
                        "source_language": {
                            "type": "string",
                            "description": "Source language code"
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code"
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Document type"
                        },
                        "word_count": {
                            "type": "integer",
                            "description": "Word count of translated text"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Translation confidence score (0.0-1.0)"
                        }
                    }
                }
            }
        ],

        "endpoints": {
            "invoke": "/invoke",
            "stream": "/stream"
        },

        "authentication": {
            "type": "none",
            "description": "No authentication required for MVP. Will add API key in production."
        },

        "vendor": {
            "name": os.getenv("VENDOR_NAME", "Docs Translator"),
            "url": os.getenv("VENDOR_URL", "https://docs-translator.onrender.com"),
            "contact": os.getenv("VENDOR_CONTACT", "support@docs-translator.com"),
            "framework": "CrewAI"
        },

        "metadata": {
            "vaas_enabled": True,
            "pii_handling": "Preserves masked PII patterns unchanged",
            "supported_formats": ["text"],
            "max_text_length": 50000,
            "typical_response_time_ms": 3000
        }
    }


# Export for easy access
AGENT_CARD = get_agent_card()
