"""
Tests for Agent Card schema.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_card import get_agent_card, AGENT_CARD


class TestAgentCard:
    """Test Agent Card structure and content."""

    def test_agent_card_structure(self):
        """Test Agent Card has required fields."""
        card = get_agent_card()

        # Required A2A protocol fields
        assert "schema_version" in card
        assert "name" in card
        assert "version" in card
        assert "description" in card
        assert "capabilities" in card
        assert "endpoints" in card

    def test_capabilities_structure(self):
        """Test capabilities are properly structured."""
        card = get_agent_card()

        assert len(card["capabilities"]) > 0

        # Check translate_document capability
        translate_cap = next(
            cap for cap in card["capabilities"]
            if cap["name"] == "translate_document"
        )

        assert "description" in translate_cap
        assert "parameters" in translate_cap
        assert "returns" in translate_cap

        # Check parameters
        params = translate_cap["parameters"]
        assert params["type"] == "object"
        assert "properties" in params
        assert "required" in params

        # Check required parameters
        required = params["required"]
        assert "text" in required
        assert "source_language" in required
        assert "target_language" in required

    def test_endpoints_structure(self):
        """Test endpoints are defined."""
        card = get_agent_card()

        endpoints = card["endpoints"]
        assert "invoke" in endpoints
        assert "stream" in endpoints

        assert endpoints["invoke"] == "/invoke"
        assert endpoints["stream"] == "/stream"

    def test_vendor_information(self):
        """Test vendor information is present."""
        card = get_agent_card()

        assert "vendor" in card
        vendor = card["vendor"]

        assert "name" in vendor
        assert "url" in vendor
        assert "framework" in vendor
        assert vendor["framework"] == "CrewAI"

    def test_supported_languages(self):
        """Test supported languages are defined."""
        card = get_agent_card()

        translate_cap = next(
            cap for cap in card["capabilities"]
            if cap["name"] == "translate_document"
        )

        source_lang_enum = translate_cap["parameters"]["properties"]["source_language"]["enum"]
        target_lang_enum = translate_cap["parameters"]["properties"]["target_language"]["enum"]

        # Check key languages are supported
        for lang in ["es", "en", "pl", "he", "uk", "ru"]:
            assert lang in source_lang_enum
            assert lang in target_lang_enum

    def test_vaas_metadata(self):
        """Test VaaS-specific metadata."""
        card = get_agent_card()

        assert "metadata" in card
        metadata = card["metadata"]

        assert metadata["vaas_enabled"] is True
        assert "pii_handling" in metadata
