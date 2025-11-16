"""
External vendor simulation module.

This module simulates the external Docs Translator vendor service that the government
ministry integrates with via A2A protocol. In production, this would be a separate
service owned by a different organization.
"""

from .docs_translator_agent import create_docs_translator_agent
from .vendor_server import start_vendor_server

__all__ = [
    "create_docs_translator_agent",
    "start_vendor_server",
]
