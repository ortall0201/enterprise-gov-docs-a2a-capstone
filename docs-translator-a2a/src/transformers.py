"""
A2A Protocol <-> CrewAI Format Transformers.

These functions bridge the gap between A2A request/response formats
and CrewAI's internal input/output structures.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def a2a_to_crewai(a2a_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform A2A request parameters to CrewAI crew inputs.

    A2A format (from RemoteA2aAgent):
    {
        "text": "Document text...",
        "source_language": "es",
        "target_language": "en",
        "document_type": "birth_certificate"
    }

    CrewAI format (for crew.kickoff(inputs=...)):
    {
        "text": "Document text...",
        "source_lang": "es",
        "target_lang": "en",
        "doc_type": "birth_certificate"
    }

    Args:
        a2a_params: Parameters from A2A request

    Returns:
        Dictionary formatted for CrewAI crew inputs

    Raises:
        ValueError: If required parameters are missing
    """
    # Validate required parameters
    required = ["text", "source_language", "target_language"]
    missing = [param for param in required if param not in a2a_params]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")

    # Transform to CrewAI format
    crew_inputs = {
        "text": a2a_params["text"],
        "source_lang": a2a_params["source_language"],
        "target_lang": a2a_params["target_language"],
        "doc_type": a2a_params.get("document_type", "general")
    }

    logger.info(
        f"Transformed A2A -> CrewAI: "
        f"{a2a_params['source_language']} -> {a2a_params['target_language']}, "
        f"text_length={len(a2a_params['text'])}"
    )

    return crew_inputs


def crewai_to_a2a(crew_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform CrewAI result to A2A response format.

    CrewAI format (from crew.kickoff()):
    {
        "translated_text": "Translation...",
        "source_language": "es",
        "target_language": "en",
        "document_type": "birth_certificate",
        "confidence": 0.95
    }

    A2A format (for RemoteA2aAgent response):
    {
        "translated_text": "Translation...",
        "source_language": "es",
        "target_language": "en",
        "document_type": "birth_certificate",
        "word_count": 150,
        "confidence": 0.95
    }

    Args:
        crew_result: Result from CrewAI crew execution

    Returns:
        Dictionary formatted for A2A response

    Raises:
        ValueError: If crew result is missing required fields
    """
    if not crew_result or "translated_text" not in crew_result:
        raise ValueError("CrewAI result missing 'translated_text' field")

    translated_text = crew_result["translated_text"]

    # Calculate word count
    word_count = len(translated_text.split()) if translated_text else 0

    # Build A2A response
    a2a_response = {
        "translated_text": translated_text,
        "source_language": crew_result.get("source_language", "unknown"),
        "target_language": crew_result.get("target_language", "unknown"),
        "document_type": crew_result.get("document_type", "general"),
        "word_count": word_count,
        "confidence": crew_result.get("confidence", 0.95)
    }

    logger.info(
        f"Transformed CrewAI -> A2A: "
        f"word_count={word_count}, confidence={a2a_response['confidence']}"
    )

    return a2a_response


def validate_a2a_request(capability: str, parameters: Dict[str, Any]) -> None:
    """
    Validate A2A request before processing.

    Args:
        capability: Requested capability name
        parameters: Request parameters

    Raises:
        ValueError: If request is invalid
    """
    # Validate capability
    valid_capabilities = ["translate_document"]
    if capability not in valid_capabilities:
        raise ValueError(
            f"Unknown capability: {capability}. "
            f"Valid capabilities: {valid_capabilities}"
        )

    # Validate parameters for translate_document
    if capability == "translate_document":
        required = ["text", "source_language", "target_language"]
        missing = [param for param in required if param not in parameters]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

        # Validate text length
        text = parameters.get("text", "")
        if len(text) > 50000:
            raise ValueError(
                f"Text too long: {len(text)} characters. Maximum: 50000"
            )

        # Validate language codes
        valid_langs = ["es", "en", "pl", "he", "uk", "ru", "fr", "de", "it"]
        source_lang = parameters.get("source_language")
        target_lang = parameters.get("target_language")

        if source_lang not in valid_langs:
            raise ValueError(
                f"Invalid source_language: {source_lang}. "
                f"Valid languages: {valid_langs}"
            )

        if target_lang not in valid_langs:
            raise ValueError(
                f"Invalid target_language: {target_lang}. "
                f"Valid languages: {valid_langs}"
            )

    logger.info(f"A2A request validated: {capability}")
