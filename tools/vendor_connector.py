"""
Vendor Connector: A2A connection to external Docs Translator vendor.

This module creates the RemoteA2aAgent that connects to the external
Docs Translator vendor agent via the Agent2Agent (A2A) protocol.

This is the A2A BOUNDARY between:
- Internal: Government ministry's secure environment
- External: Docs Translator vendor (3rd party service)

In production, the agent_card URL would point to the real vendor deployment:
  https://docs-translator.onrender.com/.well-known/agent-card.json

For this POC, it points to a local simulation running on localhost:8001.
"""

import os
from google.genai.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH
)


def create_remote_vendor_agent(
    vendor_host: str = None,
    vendor_port: int = None
) -> RemoteA2aAgent:
    """
    Create a RemoteA2aAgent connected to Docs Translator vendor.
    
    This function establishes the A2A connection to the external vendor agent.
    The RemoteA2aAgent acts as a client-side proxy that:
    - Reads the vendor's agent card (capabilities, skills)
    - Translates sub-agent calls into A2A protocol requests
    - Handles HTTP communication transparently
    - Returns responses in ADK format
    
    Args:
        vendor_host: Vendor server hostname (default: from env or localhost)
        vendor_port: Vendor server port (default: from env or 8001)
    
    Returns:
        RemoteA2aAgent: Configured connection to Docs Translator vendor
    """
    # Get vendor configuration from environment or use defaults
    host = vendor_host or os.getenv("VENDOR_SERVER_HOST", "localhost")
    port = vendor_port or int(os.getenv("VENDOR_SERVER_PORT", "8001"))

    # Construct vendor URL (use HTTPS for port 443, HTTP otherwise)
    protocol = "https" if port == 443 else "http"

    # For HTTPS (port 443), don't include port in URL
    if port == 443:
        vendor_url = f"{protocol}://{host}"
    else:
        vendor_url = f"{protocol}://{host}:{port}"

    agent_card_url = f"{vendor_url}{AGENT_CARD_WELL_KNOWN_PATH}"
    
    print(f"\n[A2A Connector] Configuring remote vendor connection:")
    print(f"    Vendor URL: {vendor_url}")
    print(f"    Agent Card: {agent_card_url}")
    print(f"    Protocol: A2A over {protocol.upper()}")
    
    # Create RemoteA2aAgent
    # This is the A2A boundary - all calls to this agent go over the network
    remote_vendor = RemoteA2aAgent(
        name="docs_translator_vendor",
        description="""
        External Docs Translator vendor agent accessed via A2A protocol.
        
        This vendor provides document translation services with:
        - Multi-language support (Spanish, Hebrew, Polish, Arabic, etc.)
        - Bureaucratic term annotation
        - Format preservation
        - RTL language handling
        
        Security Note: This is an EXTERNAL vendor. All data sent must be
        pre-filtered for PII. All responses must be post-verified.
        """,
        agent_card=agent_card_url
    )
    
    print(f"    ✓ Remote agent configured: {remote_vendor.name}")
    
    return remote_vendor


def test_vendor_connection(vendor_agent: RemoteA2aAgent) -> bool:
    """
    Test if the vendor A2A server is reachable.
    
    Args:
        vendor_agent: RemoteA2aAgent to test
    
    Returns:
        bool: True if vendor is reachable, False otherwise
    """
    import requests
    
    try:
        # Extract agent card URL from the agent
        agent_card_url = vendor_agent.agent_card
        
        print(f"\n[A2A Test] Checking vendor availability...")
        print(f"    Testing: {agent_card_url}")
        
        # Try to fetch the agent card
        response = requests.get(agent_card_url, timeout=5)
        
        if response.status_code == 200:
            print(f"    ✓ Vendor is reachable")
            print(f"    ✓ Agent card retrieved successfully")
            return True
        else:
            print(f"    ✗ Vendor returned status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Vendor not reachable: {str(e)}")
        print(f"    → Make sure vendor server is running:")
        print(f"       python vendor/vendor_server.py")
        return False
