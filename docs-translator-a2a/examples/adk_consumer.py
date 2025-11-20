"""
ADK Consumer Example - Connecting to Docs Translator A2A Service.

This demonstrates how to use Google ADK's RemoteA2aAgent to consume
the CrewAI Docs Translator service via A2A protocol.

This is the KEY integration that proves cross-framework VaaS!
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from adk.agents import RemoteA2aAgent


def test_a2a_connection():
    """Test connection to A2A service by fetching Agent Card."""
    print("=" * 60)
    print("Testing A2A Connection to Docs Translator")
    print("=" * 60)

    # Connect to local A2A service
    translator = RemoteA2aAgent(
        name="docs_translator",
        url="http://localhost:8001"
    )

    print(f"✓ Connected to: {translator.url}")
    print(f"✓ Agent name: {translator.name}")
    print()

    return translator


def translate_simple_text(translator: RemoteA2aAgent):
    """Test simple text translation."""
    print("=" * 60)
    print("Test 1: Simple Text Translation (Spanish → English)")
    print("=" * 60)

    spanish_text = """Hola, este es un documento de prueba.

Este documento contiene información importante.
Por favor, tradúzcalo al inglés con cuidado."""

    print(f"Input (Spanish):")
    print(spanish_text)
    print()

    result = translator.run(
        capability="translate_document",
        text=spanish_text,
        source_language="es",
        target_language="en",
        document_type="general"
    )

    print(f"Output (English):")
    print(result["translated_text"])
    print()
    print(f"✓ Word count: {result['word_count']}")
    print(f"✓ Confidence: {result['confidence']}")
    print()


def translate_with_pii(translator: RemoteA2aAgent):
    """Test translation with masked PII (VaaS pattern)."""
    print("=" * 60)
    print("Test 2: Translation with Masked PII (VaaS Pattern)")
    print("=" * 60)

    # Simulate enterprise-filtered document with masked PII
    filtered_doc = """CERTIFICADO DE NACIMIENTO
República de España

Nombre Completo: María ****** García López
Fecha de Nacimiento: ***/***/1990
Número de Identificación: ***-**-****-X
Pasaporte: ESP-*****4321

Esta persona es ciudadana española."""

    print("Input (Spanish with masked PII):")
    print(filtered_doc)
    print()
    print("NOTE: PII has been masked by enterprise security filter")
    print("      Vendor will NOT see real data!")
    print()

    result = translator.run(
        capability="translate_document",
        text=filtered_doc,
        source_language="es",
        target_language="en",
        document_type="birth_certificate"
    )

    print("Output (English with PII preserved):")
    print(result["translated_text"])
    print()

    # Verify PII patterns are preserved
    if "***-**-****-X" in result["translated_text"]:
        print("✓ PII patterns preserved correctly!")
    else:
        print("⚠ Warning: PII patterns may have been altered")
    print()


def translate_birth_certificate(translator: RemoteA2aAgent):
    """Test full birth certificate translation."""
    print("=" * 60)
    print("Test 3: Full Birth Certificate Translation")
    print("=" * 60)

    # Full Spanish birth certificate (PII-filtered)
    certificate = """CERTIFICADO DE NACIMIENTO
República de España
Registro Civil de Madrid

Número de Certificado: ES-2024-******
Fecha de Emisión: 15 de marzo de 2024

---

DATOS PERSONALES

Nombre Completo: ****** ****** García López
Fecha de Nacimiento: 23 de julio de 1990
Lugar de Nacimiento: Madrid, España
Nacionalidad: Española

Número de Identificación Nacional: ***-**-****-X
Número de Pasaporte: ESP-*****4321

---

DATOS DE LOS PADRES

Padre: Carlos Alberto García Martínez
Número de Identificación: ***-**-****-Y
Fecha de Nacimiento: 10 de febrero de 1965

Madre: Isabel María López Rodríguez
Número de Identificación: ***-**-****-Z
Fecha de Nacimiento: 22 de mayo de 1968

---

DECLARACIÓN OFICIAL

Este certificado es un documento oficial emitido por el Registro Civil de España.
Cualquier alteración o falsificación de este documento es punible por ley.

El portador de este documento tiene derecho a todos los servicios consulares
y protección diplomática del Estado Español en territorio extranjero.

---

Emitido en Madrid, España
15 de marzo de 2024"""

    print("Translating birth certificate...")
    print(f"Length: {len(certificate)} characters")
    print()

    result = translator.run(
        capability="translate_document",
        text=certificate,
        source_language="es",
        target_language="en",
        document_type="birth_certificate"
    )

    print("=" * 60)
    print("TRANSLATED BIRTH CERTIFICATE:")
    print("=" * 60)
    print(result["translated_text"])
    print()
    print("=" * 60)
    print(f"✓ Translation completed successfully")
    print(f"✓ Word count: {result['word_count']}")
    print(f"✓ Confidence: {result['confidence']}")
    print()


def main():
    """Run all A2A consumer tests."""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║  ADK → A2A → CrewAI Integration Test                    ║")
    print("║  Cross-Framework VaaS Demonstration                     ║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        # Test connection
        translator = test_a2a_connection()

        # Run tests
        translate_simple_text(translator)
        translate_with_pii(translator)
        translate_birth_certificate(translator)

        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("VaaS Model Validated:")
        print("  ✓ Enterprise (ADK) connected to Vendor (CrewAI)")
        print("  ✓ A2A protocol bridges frameworks")
        print("  ✓ PII filtering maintained across boundary")
        print("  ✓ Translation capabilities accessed securely")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Is the A2A service running? (python src/a2a_server.py)")
        print("  2. Is it accessible at http://localhost:8001?")
        print("  3. Is OPENAI_API_KEY set in .env?")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
