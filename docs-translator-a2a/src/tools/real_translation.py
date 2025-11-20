"""
Real Translation Tool using OpenAI API.

This tool provides actual translation capabilities (not mocked) for CrewAI agents.
Uses the same OpenAI GPT-4o model as the production Docs Translator SaaS.
"""

import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class RealTranslationTool:
    """
    Translation tool that uses OpenAI API for real translations.

    This replaces the mocked translation tool from the original Docs Translator.
    """

    name: str = "Translation Tool"
    description: str = (
        "Translates text from source language to target language using OpenAI GPT-4o. "
        "Preserves formatting, structure, and masked PII patterns. "
        "Use this tool when you need to translate documents."
    )

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")

    def run(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        doc_type: str = "general"
    ) -> str:
        """
        Translate text from source to target language.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., "es" for Spanish)
            target_lang: Target language code (e.g., "en" for English)
            doc_type: Document type (birth_certificate, passport, etc.)

        Returns:
            Translated text with preserved formatting
        """
        try:
            logger.info(
                f"Translating {doc_type} from {source_lang} to {target_lang}, "
                f"length={len(text)} chars"
            )

            # Map language codes to full names for better prompt clarity
            lang_names = {
                "es": "Spanish",
                "en": "English",
                "pl": "Polish",
                "he": "Hebrew",
                "uk": "Ukrainian",
                "ru": "Russian",
                "fr": "French",
                "de": "German",
                "it": "Italian"
            }

            source_name = lang_names.get(source_lang, source_lang)
            target_name = lang_names.get(target_lang, target_lang)

            # Build translation prompt
            system_prompt = f"""You are a professional document translator specializing in official government documents.

Your task:
- Translate the document from {source_name} to {target_name}
- Preserve ALL formatting, structure, section headers, and line breaks
- Keep masked PII patterns EXACTLY as they appear (e.g., ***-**-****-X, ESP-*****4321)
- Maintain professional, official tone appropriate for {doc_type}
- Do NOT add explanations or comments
- Return ONLY the translated document text"""

            user_prompt = f"""Translate this {doc_type} from {source_name} to {target_name}:

{text}"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent, accurate translation
                max_tokens=4096
            )

            translated_text = response.choices[0].message.content.strip()

            logger.info(
                f"Translation completed: {len(text)} -> {len(translated_text)} chars"
            )

            return translated_text

        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise RuntimeError(f"Translation failed: {str(e)}")


# Standalone function for direct use (non-CrewAI contexts)
def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
    doc_type: str = "general",
    api_key: Optional[str] = None
) -> str:
    """
    Standalone translation function.

    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        doc_type: Document type
        api_key: Optional OpenAI API key (uses env var if not provided)

    Returns:
        Translated text
    """
    tool = RealTranslationTool()
    if api_key:
        tool.client = OpenAI(api_key=api_key)

    return tool.run(text, source_lang, target_lang, doc_type)
