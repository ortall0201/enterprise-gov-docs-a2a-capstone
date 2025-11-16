"""
Docs Translator Vendor Agent.

This simulates an external vendor's translation service that integrates with the
government system via A2A protocol. Based on the real Docs Translator application
at https://github.com/ortall0201/Docs_Translator
"""

import logging
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from adk.models import Gemini
from adk.agents import LlmAgent

logger = logging.getLogger(__name__)


def translate_document(
    text: str,
    source_language: str,
    target_language: str,
    document_type: str = "general"
) -> dict:
    """
    Translate document text from source to target language.
    
    This simulates the translation capabilities of the Docs Translator vendor.
    In production, this would call actual translation APIs (Google Translate, DeepL, etc.)
    
    Args:
        text: Document text to translate
        source_language: Source language code (e.g., "es" for Spanish)
        target_language: Target language code (e.g., "en" for English)
        document_type: Type of document (birth_certificate, passport, general)
        
    Returns:
        Dictionary with translation results
    """
    logger.info(
        f"Translating {document_type} from {source_language} to {target_language}"
    )
    
    # Simulate translation processing
    # In real vendor, this would use Google Translate API, DeepL, or custom models
    
    # For demo purposes, provide a mock translation
    if source_language == "es" and target_language == "en":
        # Mock translation of Spanish birth certificate
        translated_text = """BIRTH CERTIFICATE
Republic of Spain
Madrid Civil Registry

Certificate Number: ES-2024-045678
Issue Date: March 15, 2024

---

PERSONAL DATA

Full Name: María Fernanda García López
Date of Birth: July 23, 1990
Place of Birth: Madrid, Spain
Nationality: Spanish

National Identification Number: ***-**-****-X
Passport Number: ESP-*****4321

---

PARENT DATA

Father: Carlos Alberto García Martínez
Identification Number: ***-**-****-Y
Date of Birth: February 10, 1965

Mother: Isabel María López Rodríguez
Identification Number: ***-**-****-Z
Date of Birth: May 22, 1968

---

CONTACT INFORMATION

Current Address: Calle Mayor 123, Apartment 4B, 28013 Madrid, Spain
Contact Phone: (34) ***-***-567
Email: m*************@ejemplo.es

---

ADDITIONAL INFORMATION

Marital Status: Married
Profession: Software Engineer
Company: Innovative Technology S.L.

Marriage Date: June 12, 2015
Spouse: Juan Pedro Morales Santos
Spouse Identification Number: ***-**-****-W

---

OFFICIAL DECLARATION

This certificate is an official document issued by the Civil Registry of Spain.
Any alteration or falsification of this document is punishable by law.

The bearer of this document is entitled to all consular services
and diplomatic protection of the Spanish State in foreign territory.

---

OFFICIAL SEAL

[CIVIL REGISTRY SEAL]
Authorized Official: Dr. Antonio Ruiz Fernández
Official License Number: RC-2024-567
Signature: [OFFICIAL SIGNATURE]

Issued in Madrid, Spain
March 15, 2024

---

IMPORTANT NOTES:

1. This document must be presented with valid photo identification.
2. For use in foreign countries, may require apostille or legalization.
3. The information contained in this certificate is confidential and protected by law.
4. Any changes to personal information must be reported to the Civil Registry.
5. This certificate is valid indefinitely unless otherwise specified.

For authenticity verification, visit: www.registrocivil.es/verificar
Verification Code: VER-2024-ABCD-1234-EFGH

---

END OF OFFICIAL DOCUMENT"""
    else:
        # Generic mock for other language pairs
        translated_text = f"[Translated from {source_language} to {target_language}]\n\n{text}"
    
    # Calculate mock metrics
    word_count_original = len(text.split())
    word_count_translated = len(translated_text.split())
    
    result = {
        "status": "success",
        "translated_text": translated_text,
        "source_language": source_language,
        "target_language": target_language,
        "document_type": document_type,
        "word_count_original": word_count_original,
        "word_count_translated": word_count_translated,
        "translation_confidence": 0.95,
        "vendor": "Docs Translator",
        "vendor_version": "1.0.0"
    }
    
    logger.info(
        f"Translation completed: {word_count_original} words -> {word_count_translated} words"
    )
    
    return result


def validate_translation(
    original_text: str,
    translated_text: str,
    source_language: str,
    target_language: str
) -> dict:
    """
    Validate translation quality.
    
    This simulates quality assurance checks that the vendor performs.
    
    Args:
        original_text: Original document text
        translated_text: Translated text
        source_language: Source language code
        target_language: Target language code
        
    Returns:
        Dictionary with validation results
    """
    logger.info("Validating translation quality")
    
    # Mock validation checks
    checks = {
        "length_ratio": len(translated_text) / len(original_text) if original_text else 0,
        "completeness": True,  # All sections translated
        "formatting_preserved": True,  # Structure maintained
        "terminology_consistent": True,  # Terminology correct
    }
    
    # Overall quality score
    quality_score = 0.95 if all(checks.values()) else 0.7
    
    return {
        "status": "success",
        "quality_score": quality_score,
        "checks": checks,
        "is_valid": quality_score >= 0.8,
        "recommendations": [] if quality_score >= 0.9 else ["Consider manual review"]
    }


def create_docs_translator_agent() -> LlmAgent:
    """
    Create the Docs Translator vendor agent.
    
    This agent will be exposed via A2A protocol using to_a2a().
    
    Returns:
        LlmAgent configured with translation tools
    """
    agent = LlmAgent(
        model=Gemini(model="gemini-2.0-flash-lite"),
        name="docs_translator",
        description=(
            "Docs Translator vendor agent provides document translation services "
            "for government documents. Supports Spanish to English translation "
            "with quality validation and formatting preservation."
        ),
        instructions="""You are a document translation specialist agent.

Your capabilities:
1. Translate official government documents (birth certificates, passports, etc.)
2. Preserve document structure and formatting
3. Validate translation quality
4. Handle PII-filtered documents appropriately

When translating:
- Maintain the original document structure
- Preserve section headers and formatting
- Keep masked PII (*** patterns) unchanged
- Translate all human-readable text
- Maintain professional, official tone

Always use the translate_document tool for translation tasks.
For quality checks, use validate_translation tool.""",
        tools=[translate_document, validate_translation],
        output_key="translation_result"
    )
    
    logger.info("Created Docs Translator vendor agent")
    return agent
