# 🔍 Observability Testing Guide - A2A Flow Verification

**Purpose:** Hands-on testing to verify the A2A protocol integration and answer critical observability questions.

**Prerequisites:**
- ✅ ADK Web UI running: `python -m google.adk.cli web --log_level DEBUG --a2a --port 8000 agents_web_ui`
- ✅ Browser open to: http://localhost:8000
- ✅ `.env` file configured with `GOOGLE_API_KEY`
- ✅ Sample document available at: `samples/sample_document.txt`

---

## 🎯 Critical Questions to Answer

### Primary Questions:
1. ✅ **Is the enterprise actually calling via A2A to the SaaS app (Docs Translator)?**
2. ✅ **How does it handle the translated file?**
3. ✅ **Is the translation sent back to the enterprise?**
4. ✅ **Where does the translated data live?**
5. ✅ **Can we see PII masking working?**

This guide provides **specific prompts** to answer each question through the ADK Web UI.

---

## 🚀 Test Suite: ADK Web UI Prompts

### Test 1: Complete A2A Flow Verification ⭐ START HERE

**Objective:** Answer ALL primary questions in one test

**Agent to use:** `processing_agent`

**Prompt:**
```
Process the document at C:\Users\user\Desktop\enterprise-gov-docs-a2a-capstone\samples\sample_document.txt

Please follow the complete pipeline:
1. Extract text with OCR
2. Apply pre-vendor security filtering
3. Send filtered text to external vendor for translation (Spanish to English)
4. Verify the vendor response
5. Show me exactly WHERE the translated text ends up

Document type: birth_certificate
```

**What to observe in the Web UI:**

✅ **Tool Call 1: `ocr_tool`**
- Input: Document file path
- Output: Extracted Spanish text
- Location: Internal enterprise system
- Data: Raw text with PII

✅ **Tool Call 2: `security_filter` (stage="pre")**
- Input: Spanish text with PII
- Output: Masked text ([PERSON_1], [SSN_1], etc.)
- **This proves PII masking before A2A boundary**

✅ **🔥 Sub-Agent Call: `docs_translator_vendor`**
- **THIS IS THE A2A CALL!**
- Agent type: RemoteA2aAgent
- Protocol: A2A over HTTPS
- Endpoint: https://docs-translator-a2a.onrender.com/invoke
- Input: Masked Spanish text (no real PII)
- **Check terminal logs for:**
  ```
  DEBUG - Starting new HTTPS connection (1): docs-translator-a2a.onrender.com:443
  DEBUG - "POST /invoke HTTP/1.1" 200
  ```

✅ **Tool Call 3: `security_filter` (stage="post")**
- Input: Vendor translation response
- Output: Verification result (PII check)

✅ **Final Response**
- The English translation appears in the chat
- **This is how enterprise receives the translation**
- Data location: In memory (chat interface, session state)
- NOT written to disk

**Expected Outcome:**
- ✅ Confirms A2A HTTPS call to production Render server
- ✅ Shows PII masking working (pre-vendor)
- ✅ Shows translation returned to enterprise (in chat)
- ✅ Demonstrates data stays in memory

---

### Test 2: A2A Protocol Details Deep Dive

**Objective:** Get explicit proof of A2A protocol usage

**Agent to use:** `processing_agent`

**Prompt:**
```
I need proof that you're using A2A protocol to call the external vendor.

Process the sample document and explicitly tell me:
1. The agent card URL you fetched
2. The HTTP endpoint you're calling
3. The request format you're sending
4. The response structure you received
5. What protocol is being used (REST, gRPC, JSON-RPC)?

Be specific about the A2A boundary crossing.

Document path: C:\Users\user\Desktop\enterprise-gov-docs-a2a-capstone\samples\sample_document.txt
```

**What to look for:**
- Agent card: `https://docs-translator-a2a.onrender.com/.well-known/agent-card.json`
- Invoke endpoint: `https://docs-translator-a2a.onrender.com/invoke`
- Protocol: A2A over REST (HTTPS POST)
- Request format: JSON with capability name and parameters
- Response format: JSON with translated_text, metadata

**Terminal verification:**
```bash
# Look for these logs in the terminal running ADK Web UI
GET /.well-known/agent-card.json HTTP/1.1" 200
POST /invoke HTTP/1.1" 200
```

---

### Test 3: Data Flow Tracking

**Objective:** Understand where data lives at each stage

**Agent to use:** `processing_agent`

**Prompt:**
```
Process the sample document and explain the complete data journey:

1. Where does the original Spanish text live?
2. Where does the masked text go?
3. How does it reach the external vendor (what protocol)?
4. Where does the English translation get stored?
5. Who has access to what data at each stage?
6. Is anything written to disk?

Document path: C:\Users\user\Desktop\enterprise-gov-docs-a2a-capstone\samples\sample_document.txt
```

**Expected Answer:**
1. Original text: In memory (OCR tool output)
2. Masked text: In memory (security_filter output)
3. Reaches vendor: HTTPS POST via A2A protocol
4. Translation stored: In memory (session state, chat UI)
5. Access:
   - Enterprise: Has everything (original, masked, translation)
   - Vendor: Only sees masked text (NO PII)
6. Disk: Nothing written unless explicitly saved

---

### Test 4: PII Masking Verification (Security Test)

**Objective:** Verify security boundary protection

**Agent to use:** `processing_agent`

**Prompt:**
```
I want to verify the security boundary. Process the sample document and explicitly tell me:

1. What PII was masked BEFORE sending to vendor?
2. Did the vendor receive any real names, SSNs, or sensitive data?
3. What exact text did you send across the A2A boundary?
4. What came back in the translation?
5. Is there any PII leakage in the vendor response?

Document path: C:\Users\user\Desktop\enterprise-gov-docs-a2a-capstone\samples\sample_document.txt
```

**What to verify:**
- ✅ Names replaced with [PERSON_1], [PERSON_2]
- ✅ SSNs replaced with [SSN_1]
- ✅ Birth dates replaced with [DATE_1]
- ✅ Addresses replaced with [LOCATION_1]
- ✅ Vendor response contains NO real PII
- ✅ Post-vendor security filter passes

---

### Test 5: Edge Case - Empty Document

**Objective:** Test error handling

**Agent to use:** `processing_agent`

**Prompt:**
```
Process an empty text document. Show me how the system handles this edge case.

Create a temporary empty file or process a document with no text content.
```

**Expected behavior:**
- OCR returns empty or minimal text
- Security filter handles gracefully
- A2A call may still happen (with empty text)
- System doesn't crash

---

### Test 6: Edge Case - Already English Text

**Objective:** Test language detection and adaptation

**Agent to use:** `processing_agent`

**Prompt:**
```
What if I give you an English document instead of Spanish?

Process a document that contains: "Hello, this is already in English. Name: John Doe. SSN: 123-45-6789"

Show how the system adapts when source language is already the target language.
```

**What to observe:**
- Security filter still masks PII (language-agnostic)
- Vendor may detect English → English
- Translation may be identical to input
- A2A call still happens (protocol works regardless)

---

### Test 7: Output Location Verification

**Objective:** Confirm translation storage behavior

**Agent to use:** `processing_agent`

**Prompt:**
```
After processing the sample document:

1. Show me the final translated text
2. Confirm it's stored ONLY in memory (not written to disk)
3. List all the places this translation exists right now
4. What happens to it when I close this session?
5. How would I save it to disk if I wanted to?

Document path: C:\Users\user\Desktop\enterprise-gov-docs-a2a-capstone\samples\sample_document.txt
```

**Expected Answer:**
1. Translation shown in chat response
2. Confirmed: Not on disk
3. Exists in:
   - Session state (InMemorySessionService)
   - Chat history (UI display)
   - Agent response object (in memory)
4. Lost when session ends (ephemeral)
5. Save requires explicit code:
   ```python
   Path("output.txt").write_text(translation)
   ```

---

### Test 8: Vendor Availability Check

**Objective:** Test A2A connection resilience

**Agent to use:** `processing_agent`

**Prompt:**
```
Before processing the document, can you verify that the external translation vendor is available?

1. Check if the agent card is accessible
2. Verify the A2A server is responding
3. Then process the sample document

Document path: C:\Users\user\Desktop\enterprise-gov-docs-a2a-capstone\samples\sample_document.txt
```

**What to verify:**
- Agent attempts to fetch agent card first
- Reports vendor status (online/offline)
- Proceeds with processing if available
- **Bonus:** See what happens if vendor is unreachable

---

### Test 9: Multi-Document Processing

**Objective:** Verify repeatability and consistency

**Agent to use:** `processing_agent`

**Prompt:**
```
Process the same document twice in a row to show:

1. The A2A flow is consistent and repeatable
2. Each call is independent (stateless)
3. No cached translation is returned (fresh call each time)

Document path: C:\Users\user\Desktop\enterprise-gov-docs-a2a-capstone\samples\sample_document.txt
```

**What to observe:**
- Two separate A2A calls
- Terminal shows two POST requests
- Responses may vary slightly (LLM non-determinism)
- Each call is independent (no caching)

---

### Test 10: Session State Inspection

**Objective:** Understand session management

**Agent to use:** `processing_agent`

**Prompt:**
```
After processing the sample document:

1. What information is stored in the session?
2. Can you access the previous translation from this session?
3. Show me the session conversation history
4. What happens if I ask you about the translation again?

Document path: C:\Users\user\Desktop\enterprise-gov-docs-a2a-capstone\samples\sample_document.txt
```

**What to verify:**
- Session maintains conversation history
- Previous responses accessible
- Follow-up questions work (context retained)
- Session is in-memory (not persistent)

---

## 📊 Observation Checklist

Use this checklist while running the tests:

### A2A Protocol Verification
- [ ] Agent card fetched from `/.well-known/agent-card.json`
- [ ] POST request to `/invoke` endpoint
- [ ] HTTPS protocol used
- [ ] Production Render server reached (docs-translator-a2a.onrender.com)
- [ ] Terminal logs show HTTP 200 responses

### Security Boundary Verification
- [ ] PII masked before A2A call (pre-vendor filter)
- [ ] Vendor receives only masked data
- [ ] Translation contains no leaked PII
- [ ] Post-vendor filter verifies response

### Data Flow Verification
- [ ] Original text extracted via OCR
- [ ] Masked text created by security_filter
- [ ] Translation returned via A2A
- [ ] Final response visible in UI chat
- [ ] Nothing written to disk

### UI Observation
- [ ] Tool calls displayed in UI
- [ ] Sub-agent call clearly marked
- [ ] Request/response visible
- [ ] Session state maintained
- [ ] Conversation history accessible

---

## 🎓 Understanding the Results

### What Proves A2A Integration?

✅ **Direct Evidence:**
1. RemoteA2aAgent sub-agent call in UI
2. HTTP logs showing Render server connection
3. Agent card fetch at `/.well-known/agent-card.json`
4. POST to `/invoke` endpoint

✅ **Indirect Evidence:**
1. Translation quality (OpenAI GPT-4o)
2. Response metadata (word_count, confidence)
3. Latency (network call vs local)
4. Different agent capabilities (from agent card)

### What Proves Security?

✅ **PII Protection:**
1. Pre-vendor filter masks sensitive data
2. Vendor never receives real names/SSNs
3. Post-vendor filter validates response
4. A2A boundary clearly marked

✅ **Data Isolation:**
1. Translation stays in memory
2. Not persisted to disk automatically
3. Session-scoped (ephemeral)
4. Enterprise controls data retention

---

## 🔧 Troubleshooting

### Issue: Sub-agent call not visible

**Check:**
- Is `agents_web_ui/processing_agent/agent.py` correctly configured?
- Does it include `sub_agents=[remote_vendor_agent]`?
- Is RemoteA2aAgent properly imported?

### Issue: No HTTP logs in terminal

**Solution:**
- Restart ADK Web UI with `--log_level DEBUG`
- Check terminal running the web server (not browser console)
- Look for `urllib3.connectionpool` logs

### Issue: A2A call fails

**Check:**
1. Render server status: https://dashboard.render.com
2. Agent card accessible: https://docs-translator-a2a.onrender.com/.well-known/agent-card.json
3. Network connectivity (firewall, VPN)
4. `.env` has valid `GOOGLE_API_KEY`

### Issue: PII not masked

**Check:**
- `security/policy.py` patterns configured correctly
- `security_filter` tool called with `stage="pre"`
- Sample document contains recognizable PII patterns

---

## 📝 Documenting Results

After completing the tests, document your findings:

### Test Results Template

```markdown
## Observability Test Results

**Date:** 2025-11-20
**Tester:** [Your Name]
**System:** Enterprise Gov Docs A2A Capstone

### Test 1: Complete A2A Flow
- Status: ✅ PASS / ❌ FAIL
- A2A call observed: YES / NO
- PII masked: YES / NO
- Translation received: YES / NO
- Notes: [observations]

### Test 2: A2A Protocol Details
- Agent card URL: [url]
- Invoke endpoint: [url]
- Protocol: A2A REST
- Status: ✅ PASS / ❌ FAIL
- Notes: [observations]

[Continue for all tests...]

### Summary
- Total tests: 10
- Passed: X
- Failed: Y
- Key findings: [summary]
```

---

## 🎯 Success Criteria

Your observability testing is **COMPLETE** when you can answer:

✅ **YES** to all of these:
1. I can see the A2A HTTP call in the terminal logs
2. I can see the sub-agent call in the Web UI
3. I verified PII is masked before the vendor call
4. I confirmed the translation is returned to enterprise
5. I understand where the data lives (memory, not disk)
6. I tested at least 3 edge cases
7. I documented my observations

---

## 🔗 Related Documentation

- [OBSERVABILITY_GUIDE.md](OBSERVABILITY_GUIDE.md) - Complete observability reference
- [README.md](README.md) - Project overview and setup
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Security verification
- [docs/overview.md](docs/overview.md) - Architecture and A2A protocol details

---

**Last Updated:** 2025-11-20
**Status:** ✅ Ready for testing
**ADK Version:** 1.19.0 with A2A support
