"""
Translation validation tool.

Provides quality assurance checks for translated documents.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ValidationTool:
    """
    Tool for validating translation quality.
    """

    name: str = "Validation Tool"
    description: str = (
        "Validates translation quality by checking completeness, "
        "formatting preservation, and consistency. "
        "Use this tool to verify translation accuracy."
    )

    def run(
        self,
        original_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Validate translation quality.

        Args:
            original_text: Original document text
            translated_text: Translated text
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Dictionary with validation results
        """
        try:
            logger.info("Validating translation quality")

            # Length ratio check (translations typically 0.5-2.0x original)
            length_ratio = (
                len(translated_text) / len(original_text)
                if original_text else 0
            )
            length_ok = 0.5 <= length_ratio <= 2.0

            # Completeness check (non-empty translation)
            completeness = bool(translated_text and len(translated_text) > 10)

            # PII preservation check (masked patterns should remain)
            pii_patterns = ["***", "****", "*****"]
            original_has_pii = any(pattern in original_text for pattern in pii_patterns)
            translated_has_pii = any(pattern in translated_text for pattern in pii_patterns)
            pii_preserved = (
                (original_has_pii == translated_has_pii)
                or not original_has_pii  # If no PII in original, it's fine
            )

            # Line break preservation (approximate)
            original_lines = original_text.count('\n')
            translated_lines = translated_text.count('\n')
            formatting_preserved = abs(original_lines - translated_lines) <= 5

            # Overall quality score
            checks = {
                "length_ratio_ok": length_ok,
                "completeness": completeness,
                "pii_preserved": pii_preserved,
                "formatting_preserved": formatting_preserved
            }

            passed_checks = sum(checks.values())
            quality_score = passed_checks / len(checks)

            result = {
                "is_valid": quality_score >= 0.75,
                "quality_score": quality_score,
                "checks": checks,
                "length_ratio": length_ratio,
                "recommendations": []
            }

            # Add recommendations if needed
            if not length_ok:
                result["recommendations"].append(
                    f"Length ratio {length_ratio:.2f} is unusual - review translation"
                )
            if not completeness:
                result["recommendations"].append("Translation appears incomplete")
            if not pii_preserved:
                result["recommendations"].append("Masked PII may not be preserved")
            if not formatting_preserved:
                result["recommendations"].append("Document structure may have changed")

            if not result["recommendations"]:
                result["recommendations"].append("Translation looks good!")

            logger.info(
                f"Validation complete: quality_score={quality_score:.2f}, "
                f"valid={result['is_valid']}"
            )

            return result

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "is_valid": False,
                "quality_score": 0.0,
                "checks": {},
                "error": str(e)
            }


# Standalone function for direct use
def validate_translation(
    original_text: str,
    translated_text: str,
    source_lang: str,
    target_lang: str
) -> Dict[str, Any]:
    """
    Standalone validation function.

    Args:
        original_text: Original document text
        translated_text: Translated text
        source_lang: Source language code
        target_lang: Target language code

    Returns:
        Validation results dictionary
    """
    tool = ValidationTool()
    return tool.run(original_text, translated_text, source_lang, target_lang)
