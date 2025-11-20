"""
Tests for A2A <-> CrewAI transformers.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transformers import a2a_to_crewai, crewai_to_a2a, validate_a2a_request


class TestA2AToCrewAI:
    """Test A2A to CrewAI transformation."""

    def test_basic_transformation(self):
        """Test basic parameter transformation."""
        a2a_params = {
            "text": "Test document",
            "source_language": "es",
            "target_language": "en",
            "document_type": "general"
        }

        result = a2a_to_crewai(a2a_params)

        assert result["text"] == "Test document"
        assert result["source_lang"] == "es"
        assert result["target_lang"] == "en"
        assert result["doc_type"] == "general"

    def test_default_document_type(self):
        """Test default document type when not provided."""
        a2a_params = {
            "text": "Test",
            "source_language": "es",
            "target_language": "en"
        }

        result = a2a_to_crewai(a2a_params)

        assert result["doc_type"] == "general"

    def test_missing_required_parameter(self):
        """Test error when required parameter is missing."""
        a2a_params = {
            "text": "Test",
            "source_language": "es"
            # Missing target_language
        }

        with pytest.raises(ValueError) as exc_info:
            a2a_to_crewai(a2a_params)

        assert "Missing required parameters" in str(exc_info.value)


class TestCrewAIToA2A:
    """Test CrewAI to A2A transformation."""

    def test_basic_transformation(self):
        """Test basic result transformation."""
        crew_result = {
            "translated_text": "Translated document",
            "source_language": "es",
            "target_language": "en",
            "document_type": "birth_certificate",
            "confidence": 0.95
        }

        result = crewai_to_a2a(crew_result)

        assert result["translated_text"] == "Translated document"
        assert result["source_language"] == "es"
        assert result["target_language"] == "en"
        assert result["document_type"] == "birth_certificate"
        assert result["confidence"] == 0.95
        assert "word_count" in result

    def test_word_count_calculation(self):
        """Test word count is calculated correctly."""
        crew_result = {
            "translated_text": "Hello world test document",
            "source_language": "es",
            "target_language": "en"
        }

        result = crewai_to_a2a(crew_result)

        assert result["word_count"] == 4

    def test_missing_translated_text(self):
        """Test error when translated_text is missing."""
        crew_result = {}

        with pytest.raises(ValueError) as exc_info:
            crewai_to_a2a(crew_result)

        assert "translated_text" in str(exc_info.value)


class TestValidateA2ARequest:
    """Test A2A request validation."""

    def test_valid_request(self):
        """Test validation passes for valid request."""
        # Should not raise exception
        validate_a2a_request(
            "translate_document",
            {
                "text": "Test document",
                "source_language": "es",
                "target_language": "en"
            }
        )

    def test_unknown_capability(self):
        """Test validation fails for unknown capability."""
        with pytest.raises(ValueError) as exc_info:
            validate_a2a_request("unknown_capability", {})

        assert "Unknown capability" in str(exc_info.value)

    def test_missing_parameters(self):
        """Test validation fails for missing parameters."""
        with pytest.raises(ValueError) as exc_info:
            validate_a2a_request(
                "translate_document",
                {"text": "Test"}  # Missing languages
            )

        assert "Missing required parameters" in str(exc_info.value)

    def test_text_too_long(self):
        """Test validation fails for text exceeding limit."""
        with pytest.raises(ValueError) as exc_info:
            validate_a2a_request(
                "translate_document",
                {
                    "text": "x" * 60000,  # Exceeds 50000 limit
                    "source_language": "es",
                    "target_language": "en"
                }
            )

        assert "Text too long" in str(exc_info.value)

    def test_invalid_language_code(self):
        """Test validation fails for invalid language code."""
        with pytest.raises(ValueError) as exc_info:
            validate_a2a_request(
                "translate_document",
                {
                    "text": "Test",
                    "source_language": "invalid",
                    "target_language": "en"
                }
            )

        assert "Invalid source_language" in str(exc_info.value)
