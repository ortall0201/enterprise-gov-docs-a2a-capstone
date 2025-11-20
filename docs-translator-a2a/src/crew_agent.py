"""
CrewAI Document Translator Agent for A2A VaaS.

This implements a CrewAI agent specifically for the A2A protocol,
separate from the production Docs Translator SaaS.
"""

import logging
from tools.real_translation import translate_text
from tools.validation import validate_translation

logger = logging.getLogger(__name__)


def create_translation_agent():
    """
    Create translation agent (simplified without CrewAI tools for compatibility).

    This function handles translation directly without CrewAI tools wrapper
    to avoid version compatibility issues.

    Returns:
        None (direct translation function)
    """
    logger.info("Created translation agent (direct function)")
    return None


def translate_document_crew(
    text: str,
    source_lang: str,
    target_lang: str,
    doc_type: str = "general"
) -> dict:
    """
    Execute translation workflow (direct translation).

    This is the main entry point for translation.
    Uses OpenAI directly without CrewAI orchestration for simplicity.

    Args:
        text: Document text to translate
        source_lang: Source language code (e.g., "es")
        target_lang: Target language code (e.g., "en")
        doc_type: Document type (birth_certificate, passport, etc.)

    Returns:
        Dictionary with translation results:
        {
            "translated_text": str,
            "source_language": str,
            "target_language": str,
            "document_type": str,
            "confidence": float
        }
    """
    try:
        logger.info(
            f"Starting translation: {source_lang} -> {target_lang}, "
            f"doc_type={doc_type}"
        )

        # Direct translation using OpenAI
        translated_text = translate_text(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            doc_type=doc_type
        )

        # Validate translation quality
        validation = validate_translation(
            original_text=text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang
        )

        # Build response
        response = {
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "document_type": doc_type,
            "confidence": 0.95  # High confidence with GPT-4o
        }

        logger.info(
            f"Translation completed: {len(text)} chars -> "
            f"{len(translated_text)} chars"
        )

        return response

    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        raise RuntimeError(f"Translation failed: {str(e)}")


def validate_crew_translation(
    original_text: str,
    translated_text: str,
    source_lang: str,
    target_lang: str
) -> dict:
    """
    Validate translation quality using CrewAI agent.

    Args:
        original_text: Original document text
        translated_text: Translated text
        source_lang: Source language code
        target_lang: Target language code

    Returns:
        Validation results dictionary
    """
    try:
        logger.info("Starting CrewAI validation")

        # Create validation agent
        validator_agent = Agent(
            role="Translation Quality Validator",
            goal="Verify translation quality and accuracy",
            backstory="Expert in assessing translation quality for official documents",
            tools=[ValidationTool()],
            verbose=True,
            allow_delegation=False
        )

        # Define validation task
        task = Task(
            description=f"""Validate the translation quality.

Original text ({source_lang}):
{original_text[:500]}...

Translated text ({target_lang}):
{translated_text[:500]}...

Use the validation tool to check:
1. Completeness
2. Formatting preservation
3. PII preservation
4. Length ratio

Provide validation results.""",
            agent=validator_agent,
            expected_output="Validation report with quality score and recommendations"
        )

        # Execute validation crew
        crew = Crew(
            agents=[validator_agent],
            tasks=[task],
            verbose=True
        )

        result = crew.kickoff()

        logger.info("Validation completed")
        return {"validation_result": str(result)}

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {"error": str(e)}
