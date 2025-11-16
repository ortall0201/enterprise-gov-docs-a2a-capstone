"""
Security and policy enforcement layer.

This module implements security controls for cross-organizational data exchange:
- PII masking before external vendor calls
- Response verification after vendor processing
- Policy compliance checks
- Audit logging

These controls protect sensitive government data when integrating with
external vendors via the A2A protocol.
"""

from .policy import security_filter

__all__ = ["security_filter"]
