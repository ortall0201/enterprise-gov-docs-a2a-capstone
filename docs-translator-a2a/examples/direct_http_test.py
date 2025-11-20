"""
Direct HTTP Test - Testing A2A endpoints without ADK.

This script tests the A2A service using direct HTTP requests,
useful for debugging or testing from non-ADK environments.
"""

import requests
import json


def test_agent_card():
    """Test Agent Card endpoint."""
    print("=" * 60)
    print("Test 1: Agent Card (/.well-known/agent-card.json)")
    print("=" * 60)

    response = requests.get("http://localhost:8001/.well-known/agent-card.json")

    if response.status_code == 200:
        agent_card = response.json()
        print(f"✓ Agent Card retrieved successfully")
        print(f"  Name: {agent_card['name']}")
        print(f"  Version: {agent_card['version']}")
        print(f"  Capabilities: {[cap['name'] for cap in agent_card['capabilities']]}")
        print(f"  Endpoints: {agent_card['endpoints']}")
        print()
        return True
    else:
        print(f"✗ Failed to retrieve Agent Card: {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def test_invoke():
    """Test /invoke endpoint."""
    print("=" * 60)
    print("Test 2: Invoke Endpoint (POST /invoke)")
    print("=" * 60)

    request_data = {
        "capability": "translate_document",
        "parameters": {
            "text": "Hola mundo. Este es un documento de prueba.",
            "source_language": "es",
            "target_language": "en",
            "document_type": "general"
        }
    }

    print("Sending request:")
    print(json.dumps(request_data, indent=2))
    print()

    response = requests.post(
        "http://localhost:8001/invoke",
        json=request_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Translation successful")
        print(f"  Status: {result['status']}")
        print(f"  Translated text: {result['result']['translated_text']}")
        print(f"  Word count: {result['result']['word_count']}")
        print()
        return True
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def test_health():
    """Test health endpoint."""
    print("=" * 60)
    print("Test 3: Health Check (GET /health)")
    print("=" * 60)

    response = requests.get("http://localhost:8001/health")

    if response.status_code == 200:
        health = response.json()
        print(f"✓ Service is healthy")
        print(f"  Status: {health['status']}")
        print(f"  Service: {health['service']}")
        print(f"  A2A enabled: {health['a2a_enabled']}")
        print(f"  OpenAI configured: {health['openai_configured']}")
        print()
        return True
    else:
        print(f"✗ Health check failed: {response.status_code}")
        return False


def main():
    """Run all HTTP tests."""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║  Direct HTTP A2A Endpoint Test                          ║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        # Run tests
        results = []
        results.append(test_health())
        results.append(test_agent_card())
        results.append(test_invoke())

        # Summary
        print("=" * 60)
        if all(results):
            print("✓ ALL TESTS PASSED")
        else:
            print("✗ SOME TESTS FAILED")
        print("=" * 60)
        print()

    except requests.exceptions.ConnectionError:
        print()
        print("=" * 60)
        print("✗ CONNECTION ERROR")
        print("=" * 60)
        print("Could not connect to http://localhost:8001")
        print()
        print("Make sure the A2A service is running:")
        print("  cd docs-translator-a2a")
        print("  python src/a2a_server.py")
        print()


if __name__ == "__main__":
    main()
