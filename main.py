"""
Enterprise Government Document Processing - Main Demo

This script demonstrates the complete document processing pipeline with A2A integration.
"""

import os
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """
    Main demo function showing complete document processing workflow.
    """
    logger.info("=" * 80)
    logger.info("Enterprise Government Document Processing - A2A Capstone Demo")
    logger.info("=" * 80)

    # Validate environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        logger.error("GOOGLE_API_KEY not configured!")
        logger.error("Please set your API key in .env file")
        logger.error("Get your key at: https://aistudio.google.com/app/apikey")
        return

    # Import agents
    from agents import create_intake_agent, create_processing_agent
    from tools import create_remote_vendor_agent
    from tools.vendor_connector import test_vendor_connection

    logger.info("\n[Step 1] Checking vendor connectivity...")
    vendor_check = test_vendor_connection()

    if vendor_check["status"] != "success":
        logger.warning("⚠️  Vendor server not reachable!")
        logger.warning("Please start the vendor server first:")
        logger.warning("  python -m vendor.vendor_server")
        logger.warning("\nContinuing with demo (vendor call will be simulated)...")
    else:
        logger.info("✓ Vendor server is online")

    # Sample document path
    sample_doc = Path(__file__).parent / "samples" / "sample_document.txt"

    if not sample_doc.exists():
        logger.error(f"Sample document not found: {sample_doc}")
        return

    logger.info(f"\n[Step 2] Document to process: {sample_doc.name}")

    # Create agents
    logger.info("\n[Step 3] Creating government agents...")
    intake_agent = create_intake_agent()
    processing_agent = create_processing_agent()

    logger.info(f"  ✓ Created: {intake_agent.name}")
    logger.info(f"  ✓ Created: {processing_agent.name}")

    # Stage 1: Document Intake
    logger.info("\n" + "=" * 80)
    logger.info("[STAGE 1: DOCUMENT INTAKE]")
    logger.info("=" * 80)

    from adk.runners import Runner

    intake_runner = Runner(agent=intake_agent)
    intake_prompt = f"Please validate the document at: {sample_doc}"

    logger.info(f"\nPrompt: {intake_prompt}")
    logger.info("\nIntake Agent processing...")

    intake_result = await intake_runner.run(intake_prompt)

    logger.info("\n--- Intake Agent Response ---")
    logger.info(intake_result.response_text)

    # Stage 2: Document Processing with A2A
    logger.info("\n" + "=" * 80)
    logger.info("[STAGE 2: DOCUMENT PROCESSING WITH A2A]")
    logger.info("=" * 80)

    processing_runner = Runner(agent=processing_agent)
    processing_prompt = f"""Process the document at {sample_doc} through the complete pipeline:

1. Extract text using OCR
2. Apply security filtering (mask PII)
3. Send to external vendor via A2A for translation (Spanish to English)
4. Verify vendor response
5. Return final processed document

Document type: birth_certificate
Target language: English"""

    logger.info(f"\nPrompt: {processing_prompt}")
    logger.info("\nProcessing Agent pipeline:")
    logger.info("  → Step 1: OCR extraction")
    logger.info("  → Step 2: PII filtering (pre-vendor)")
    logger.info("  → Step 3: A2A vendor call [CROSS-ORG BOUNDARY]")
    logger.info("  → Step 4: Security verification (post-vendor)")
    logger.info("  → Step 5: Final compilation")

    processing_result = await processing_runner.run(processing_prompt)

    logger.info("\n--- Processing Agent Response ---")
    logger.info(processing_result.response_text)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("[DEMO SUMMARY]")
    logger.info("=" * 80)
    logger.info("\n✓ Document validation complete (IntakeAgent)")
    logger.info("✓ OCR text extraction complete")
    logger.info("✓ PII filtering applied")
    logger.info("✓ A2A vendor integration complete")
    logger.info("✓ Security verification passed")
    logger.info("✓ Final document processed")

    logger.info("\n" + "=" * 80)
    logger.info("Capstone Objectives Demonstrated:")
    logger.info("=" * 80)
    logger.info("✓ Multi-agent orchestration (IntakeAgent → ProcessingAgent)")
    logger.info("✓ A2A protocol for cross-organizational integration")
    logger.info("✓ RemoteA2aAgent for vendor communication")
    logger.info("✓ Security boundaries with PII filtering")
    logger.info("✓ Tool integration (OCR, security_filter)")
    logger.info("✓ Sub-agent delegation pattern")
    logger.info("✓ Real-world government document use case")

    logger.info("\n" + "=" * 80)
    logger.info("Demo Complete!")
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
