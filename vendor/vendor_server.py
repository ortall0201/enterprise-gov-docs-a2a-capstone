"""
A2A Vendor Server.

This module exposes the Docs Translator agent as an A2A-compatible service
using the to_a2a() function from Google ADK.
"""

import os
import logging
from adk.a2a import to_a2a
from .docs_translator_agent import create_docs_translator_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_vendor_server(host: str = None, port: int = None):
    """
    Start the A2A vendor server.
    
    This exposes the Docs Translator agent via A2A protocol, making it
    accessible to external consumers via RemoteA2aAgent.
    
    Args:
        host: Server host (default: localhost)
        port: Server port (default: 8001)
    """
    host = host or os.getenv("VENDOR_SERVER_HOST", "localhost")
    port = port or int(os.getenv("VENDOR_SERVER_PORT", "8001"))
    
    logger.info("=" * 60)
    logger.info("Starting Docs Translator A2A Vendor Server")
    logger.info("=" * 60)
    
    # Create the vendor agent
    vendor_agent = create_docs_translator_agent()
    logger.info(f"Agent created: {vendor_agent.name}")
    
    # Convert to A2A service
    # This creates:
    # - Agent card at /.well-known/agent-card.json
    # - Streaming endpoint at /streams
    # - Session management
    logger.info(f"Exposing agent via A2A protocol at http://{host}:{port}")
    
    a2a_app = to_a2a(vendor_agent)
    
    logger.info("=" * 60)
    logger.info("A2A Endpoints:")
    logger.info(f"  Agent Card: http://{host}:{port}/.well-known/agent-card.json")
    logger.info(f"  Streams: http://{host}:{port}/streams")
    logger.info("=" * 60)
    logger.info("Vendor server is ready to accept A2A connections")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Run the A2A server using uvicorn
    import uvicorn
    uvicorn.run(a2a_app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_vendor_server()
