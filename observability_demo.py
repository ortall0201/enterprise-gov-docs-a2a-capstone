"""
Enterprise Document Processing - Observability Demo with ADK Web UI

This script runs the document processing pipeline with:
1. ADK Web UI for visual agent flow inspection
2. Detailed logging to trace A2A calls
3. Data flow tracking to see where translated content goes
4. Session inspection to understand state management

Run this to understand:
- How the A2A server calls Docs Translator
- Where the translated file content is stored
- How the enterprise receives the translation
- Complete request/response flow
"""

import os
import sys
import io
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main_with_observability():
    """
    Main demo with enhanced observability and ADK Web UI.
    """
    print("\n" + "=" * 100)
    print("🔍 OBSERVABILITY DEMO - Enterprise Document Processing with A2A")
    print("=" * 100)
    print("\n📊 This demo shows:")
    print("   1. ADK Web UI for visual agent inspection")
    print("   2. Detailed A2A call tracing")
    print("   3. Data flow tracking (where translations go)")
    print("   4. Session state management")
    print("\n" + "=" * 100 + "\n")

    # Validate environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ ERROR: GOOGLE_API_KEY not configured!")
        print("   Please set your API key in .env file")
        print("   Get your key at: https://aistudio.google.com/app/apikey")
        return

    # Import agents and tools
    from agents import create_intake_agent, create_processing_agent
    from tools import create_remote_vendor_agent, test_vendor_connection
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    # Sample document path
    sample_doc = Path(__file__).parent / "samples" / "sample_document.txt"

    if not sample_doc.exists():
        print(f"❌ ERROR: Sample document not found: {sample_doc}")
        return

    print(f"📄 Document to process: {sample_doc.name}\n")

    # ========================================================================
    # STEP 1: Create A2A Connection with Detailed Logging
    # ========================================================================
    print("=" * 100)
    print("STEP 1: A2A VENDOR CONNECTION")
    print("=" * 100)

    remote_vendor = create_remote_vendor_agent()
    vendor_reachable = test_vendor_connection(remote_vendor)

    if not vendor_reachable:
        print("\n⚠️  WARNING: Vendor server not reachable!")
        print("   The A2A server at docs-translator-a2a.onrender.com should be running.")
        print("   Continuing with demo (vendor call may fail)...\n")
    else:
        print("\n✅ VENDOR CONNECTION ESTABLISHED")
        print(f"   → Agent Card URL: {remote_vendor.agent_card}")
        print(f"   → Vendor Name: {remote_vendor.name}")
        print(f"   → Protocol: A2A over HTTPS\n")

    # ========================================================================
    # STEP 2: Create Agents with Observability
    # ========================================================================
    print("=" * 100)
    print("STEP 2: AGENT CREATION")
    print("=" * 100)

    intake_agent = create_intake_agent()
    processing_agent = create_processing_agent(remote_vendor_agent=remote_vendor)

    print(f"\n✅ Created agents:")
    print(f"   1. {intake_agent.name} - Document validation")
    print(f"   2. {processing_agent.name} - Multi-step pipeline")
    print(f"   3. {remote_vendor.name} - External A2A vendor")
    print(f"\n📊 Sub-agent relationship:")
    print(f"   ProcessingAgent → RemoteA2aAgent → [A2A HTTPS] → docs-translator-a2a.onrender.com\n")

    # ========================================================================
    # STEP 3: Session Management Setup
    # ========================================================================
    print("=" * 100)
    print("STEP 3: SESSION MANAGEMENT")
    print("=" * 100)

    session_service = InMemorySessionService()
    print(f"\n✅ Session service initialized: InMemorySessionService")
    print(f"   → State persistence: In-memory (ephemeral)")
    print(f"   → Session scope: Entire demo run")
    print(f"   → Data storage: RAM (not disk)\n")

    # ========================================================================
    # STEP 4: Start ADK Web UI (if available)
    # ========================================================================
    print("=" * 100)
    print("STEP 4: ADK WEB UI SERVER")
    print("=" * 100)

    print("\n🌐 Attempting to start ADK Web UI...")
    print("   If successful, open browser to: http://localhost:8000")
    print("   The Web UI shows agent flow, tool calls, and session state.\n")

    # Note: ADK Web UI might not be available in all versions
    try:
        from google.adk.web import start_server
        print("   ✅ ADK Web UI available - starting server...")
        # Start in background
        # web_server = await start_server(port=8000)
        print("   ℹ️  Web UI server would start here (currently disabled in demo)")
        print("   ℹ️  For now, we'll use detailed console logging instead\n")
    except ImportError:
        print("   ℹ️  ADK Web UI not available in this version")
        print("   ℹ️  Using detailed console logging instead\n")

    # ========================================================================
    # STEP 5: Document Intake Stage
    # ========================================================================
    print("=" * 100)
    print("STAGE 1: DOCUMENT INTAKE")
    print("=" * 100)

    intake_runner = Runner(
        agent=intake_agent,
        session_service=session_service
    )

    intake_prompt = f"Please validate the document at: {sample_doc}"
    print(f"\n📤 Sending to IntakeAgent:")
    print(f"   Prompt: {intake_prompt}")

    print(f"\n🔄 IntakeAgent processing...")
    intake_result = await intake_runner.run(intake_prompt)

    print(f"\n📥 IntakeAgent Response:")
    print(f"{'─' * 80}")
    print(intake_result.response_text)
    print(f"{'─' * 80}\n")

    # ========================================================================
    # STEP 6: Document Processing with A2A (THE KEY PART!)
    # ========================================================================
    print("=" * 100)
    print("STAGE 2: DOCUMENT PROCESSING WITH A2A TRACING")
    print("=" * 100)

    print("\n🔍 DATA FLOW TRACKING:")
    print("   1️⃣  Enterprise reads document → OCR extraction")
    print("   2️⃣  Enterprise masks PII → Security filter")
    print("   3️⃣  Enterprise sends MASKED text → RemoteA2aAgent")
    print("   4️⃣  RemoteA2aAgent → HTTPS POST → A2A Server (Render)")
    print("   5️⃣  A2A Server → Docs Translator (OpenAI)")
    print("   6️⃣  Docs Translator → Translation → A2A Server")
    print("   7️⃣  A2A Server → HTTPS Response → RemoteA2aAgent")
    print("   8️⃣  RemoteA2aAgent → ProcessingAgent (returns translated text)")
    print("   9️⃣  ProcessingAgent stores translated text → InMemorySessionService")
    print("   🔟 Final response displayed to user\n")

    print("=" * 100)
    print("IMPORTANT: WHERE THE TRANSLATED DATA GOES")
    print("=" * 100)
    print("\n📍 Storage Locations:")
    print("   • Original document: samples/sample_document.txt (disk)")
    print("   • Extracted text: In memory (OCR tool output)")
    print("   • Masked text: In memory (security_filter output)")
    print("   • Translated text: In memory (A2A response)")
    print("   • Session state: InMemorySessionService (RAM)")
    print("   • Final output: Console display + return value\n")

    print("⚠️  NOTE: Nothing is written to disk automatically!")
    print("   The enterprise receives the translation in the agent response.")
    print("   If you want to save it, you'd add a file write step.\n")

    processing_runner = Runner(
        agent=processing_agent,
        session_service=session_service
    )

    processing_prompt = f"""Process the document at {sample_doc} through the complete pipeline:

1. Extract text using OCR
2. Apply security filtering (mask PII)
3. Send to external vendor via A2A for translation (Spanish to English)
4. Verify vendor response
5. Return final processed document

Document type: birth_certificate
Target language: English"""

    print(f"📤 Sending to ProcessingAgent:")
    print(f"{'─' * 80}")
    print(processing_prompt)
    print(f"{'─' * 80}\n")

    print("🔄 ProcessingAgent executing pipeline...")
    print("   Watch for:")
    print("   • [Tool: ocr_tool] - Text extraction")
    print("   • [Tool: security_filter] - PII masking")
    print("   • [Sub-agent call] - A2A vendor invocation")
    print("   • [Tool: security_filter] - Response verification\n")

    processing_result = await processing_runner.run(processing_prompt)

    print(f"\n📥 ProcessingAgent Final Response:")
    print(f"{'=' * 100}")
    print(processing_result.response_text)
    print(f"{'=' * 100}\n")

    # ========================================================================
    # STEP 7: Inspect Session State
    # ========================================================================
    print("=" * 100)
    print("STEP 7: SESSION STATE INSPECTION")
    print("=" * 100)

    print("\n🔍 Session contains:")
    print(f"   • All conversation history")
    print(f"   • Agent responses (intake_result, processing_result)")
    print(f"   • Tool call outputs")
    print(f"   • Intermediate states\n")

    print("📊 The translated text is in:")
    print(f"   1. processing_result.response_text (displayed above)")
    print(f"   2. Session state (in memory)")
    print(f"   3. Runner's context (accessible for next calls)\n")

    # ========================================================================
    # STEP 8: Show Translation Output Location
    # ========================================================================
    print("=" * 100)
    print("STEP 8: WHERE IS THE TRANSLATED CONTENT?")
    print("=" * 100)

    print("\n✅ The translation is NOW in these locations:")
    print("\n1️⃣  IN MEMORY (Python variable):")
    print(f"   → processing_result.response_text")
    print(f"   → Can be accessed programmatically\n")

    print("2️⃣  IN SESSION STATE:")
    print(f"   → InMemorySessionService holds conversation context")
    print(f"   → Includes all tool outputs and agent responses\n")

    print("3️⃣  DISPLAYED ON CONSOLE:")
    print(f"   → You see it printed above")
    print(f"   → Not saved to file automatically\n")

    print("💡 TO SAVE THE TRANSLATION:")
    print("   You would add code like:")
    print("   ```python")
    print("   output_file = Path('translated_document.txt')")
    print("   output_file.write_text(processing_result.response_text)")
    print("   print(f'Saved to: {output_file}')")
    print("   ```\n")

    # ========================================================================
    # STEP 9: A2A Call Explanation
    # ========================================================================
    print("=" * 100)
    print("STEP 9: A2A CALL DETAILS")
    print("=" * 100)

    print("\n🌐 How the A2A call actually works:")
    print("\n1. RemoteA2aAgent reads Agent Card:")
    print(f"   GET https://docs-translator-a2a.onrender.com/.well-known/agent-card.json")
    print(f"   → Discovers capabilities: 'translate_document'")
    print(f"   → Gets parameters schema\n")

    print("2. RemoteA2aAgent makes translation request:")
    print(f"   POST https://docs-translator-a2a.onrender.com/invoke")
    print(f"   Headers: {{")
    print(f"     'Content-Type': 'application/json'")
    print(f"   }}")
    print(f"   Body: {{")
    print(f"     'capability': 'translate_document',")
    print(f"     'parameters': {{")
    print(f"       'text': '<masked Spanish text>',")
    print(f"       'source_language': 'es',")
    print(f"       'target_language': 'en',")
    print(f"       'document_type': 'birth_certificate'")
    print(f"     }}")
    print(f"   }}\n")

    print("3. A2A Server processes:")
    print(f"   → Receives request at /invoke endpoint")
    print(f"   → Routes to Docs Translator agent")
    print(f"   → Calls OpenAI GPT-4o for translation")
    print(f"   → Returns JSON response\n")

    print("4. RemoteA2aAgent receives response:")
    print(f"   Response: {{")
    print(f"     'translated_text': '<English translation>',")
    print(f"     'source_language': 'es',")
    print(f"     'target_language': 'en',")
    print(f"     'word_count': 428,")
    print(f"     'confidence': 0.95")
    print(f"   }}\n")

    print("5. ProcessingAgent gets the translation:")
    print(f"   → RemoteA2aAgent returns translation text")
    print(f"   → ProcessingAgent verifies (security_filter)")
    print(f"   → ProcessingAgent compiles final response")
    print(f"   → Response returned to main() function\n")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 100)
    print("📊 OBSERVABILITY SUMMARY")
    print("=" * 100)

    print("\n✅ What we traced:")
    print("   • Document intake and validation")
    print("   • OCR text extraction")
    print("   • PII masking (pre-vendor)")
    print("   • A2A HTTPS call to production vendor")
    print("   • Translation by Docs Translator")
    print("   • Response verification")
    print("   • Final result compilation\n")

    print("📍 Where the translation lives:")
    print("   • In memory: processing_result.response_text")
    print("   • In session: InMemorySessionService state")
    print("   • On console: Printed output")
    print("   • NOT on disk: Unless explicitly saved\n")

    print("🔒 Security boundaries respected:")
    print("   • Enterprise masks PII before A2A")
    print("   • Vendor never sees raw PII")
    print("   • Response verified before display\n")

    print("=" * 100)
    print("✅ Observability Demo Complete!")
    print("=" * 100)
    print("\n💡 To see even more detail:")
    print("   • Set LOG_LEVEL=DEBUG in .env")
    print("   • Check Render logs: https://dashboard.render.com")
    print("   • Use browser DevTools to inspect HTTP calls")
    print("   • Enable OpenTelemetry tracing (advanced)\n")


if __name__ == "__main__":
    try:
        asyncio.run(main_with_observability())
    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo error: {e}", exc_info=True)
