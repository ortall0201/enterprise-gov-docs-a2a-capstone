"""
Internal tools for government document processing.

This module contains trusted, internal tools used by government agents:
- ocr_tool: Text extraction from documents
- vendor_connector: A2A connection to external vendor

These tools run in the secure government environment and are not exposed externally.
"""

from .ocr_tool import ocr_tool
from .vendor_connector import create_remote_vendor_agent, test_vendor_connection

__all__ = [
    "ocr_tool",
    "create_remote_vendor_agent",
    "test_vendor_connection",
]
