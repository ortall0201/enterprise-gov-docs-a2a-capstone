"""
Internal government ministry agents.

This module contains the ADK agents that run inside the government ministry's
secure environment. These agents process documents with security and policy
controls before integrating with external vendors via A2A protocol.
"""

from .intake_agent import create_intake_agent
from .processing_agent import create_processing_agent

__all__ = [
    "create_intake_agent",
    "create_processing_agent",
]
