"""
Security policy and PII filtering implementation.

This module provides PII detection and filtering capabilities for government documents
before they are sent to external vendors via A2A protocol.
"""

import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# PII Detection Patterns
PII_PATTERNS = {
    "national_id_spain": r"\b\d{3}-\d{2}-\d{4}-[A-Z]\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "date_of_birth": r"\b\d{1,2}\s+de\s+\w+,?\s+\d{4}\b",  # Spanish date format
    "passport": r"\b[A-Z]{3}-\d{9}\b",
}

# Masking templates
MASK_CHAR = "X"


def detect_pii(text: str) -> Dict[str, List[str]]:
    """
    Detect PII in text using regex patterns.

    Args:
        text: Text to scan for PII

    Returns:
        Dictionary mapping PII types to list of detected values
    """
    detected = {}

    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            # Flatten matches if they're tuples (from capture groups)
            flat_matches = [
                m if isinstance(m, str) else "".join(m).strip()
                for m in matches
            ]
            detected[pii_type] = flat_matches
            logger.info(f"Detected {len(flat_matches)} instances of {pii_type}")

    return detected


def mask_pii(text: str, detected_pii: Dict[str, List[str]] = None) -> Dict[str, Any]:
    """
    Mask PII in text by replacing with placeholder values.

    Args:
        text: Original text containing PII
        detected_pii: Optional pre-detected PII dictionary. If None, will detect automatically.

    Returns:
        Dictionary containing:
            - masked_text: Text with PII replaced
            - pii_summary: Summary of what was masked
            - original_pii_count: Number of PII instances found
    """
    if detected_pii is None:
        detected_pii = detect_pii(text)

    masked_text = text
    total_masked = 0

    # Mask each type of PII
    for pii_type, matches in detected_pii.items():
        for match in matches:
            # Create mask preserving length but hiding content
            if pii_type == "email":
                # For emails, show first char and domain
                parts = match.split("@")
                if len(parts) == 2:
                    mask = f"{parts[0][0]}{'*' * (len(parts[0]) - 1)}@{parts[1]}"
                else:
                    mask = "*" * len(match)
            elif pii_type in ["phone", "ssn", "national_id_spain", "credit_card"]:
                # Show last 4 digits
                visible_chars = min(4, len(match) // 3)
                mask = "*" * (len(match) - visible_chars) + match[-visible_chars:]
            elif pii_type == "passport":
                # Show country code only
                mask = match[:3] + "-" + "*" * 9
            elif pii_type == "date_of_birth":
                # Mask day and month, keep year
                parts = match.split()
                if len(parts) >= 3:
                    mask = f"XX de XXXX, {parts[-1]}"
                else:
                    mask = "XX de XXXX, XXXX"
            else:
                mask = "*" * len(match)

            masked_text = masked_text.replace(match, mask)
            total_masked += 1

    pii_summary = {
        pii_type: len(matches)
        for pii_type, matches in detected_pii.items()
    }

    logger.info(f"Masked {total_masked} PII instances across {len(detected_pii)} categories")

    return {
        "masked_text": masked_text,
        "pii_summary": pii_summary,
        "original_pii_count": total_masked,
        "detected_categories": list(detected_pii.keys())
    }


def verify_pii_removal(text: str, threshold: int = 0) -> Dict[str, Any]:
    """
    Verify that PII has been properly removed from text.

    Args:
        text: Text to verify
        threshold: Maximum allowed PII instances (default 0 = no PII allowed)

    Returns:
        Dictionary containing:
            - is_safe: Whether text meets safety threshold
            - detected_pii: Any PII still found
            - violation_count: Number of PII instances detected
    """
    detected = detect_pii(text)
    violation_count = sum(len(matches) for matches in detected.values())
    is_safe = violation_count <= threshold

    if not is_safe:
        logger.warning(
            f"PII verification failed: {violation_count} instances detected "
            f"(threshold: {threshold})"
        )
    else:
        logger.info("PII verification passed: No sensitive data detected")

    return {
        "is_safe": is_safe,
        "detected_pii": detected,
        "violation_count": violation_count,
        "threshold": threshold
    }


def security_filter(
    text: str,
    mode: str = "mask",
    verify: bool = True
) -> dict:
    """
    Main security filter tool for ADK agents.

    This tool is called by ProcessingAgent to filter PII before sending to vendor
    and to verify vendor responses don't leak PII.

    Args:
        text: Text to filter
        mode: "mask" to mask PII, "detect" to only detect, "verify" to check removal
        verify: Whether to verify PII removal after masking

    Returns:
        Dictionary with filtered text and security metadata
    """
    result = {
        "status": "success",
        "mode": mode,
        "original_text_length": len(text)
    }

    try:
        if mode == "detect":
            detected = detect_pii(text)
            result["detected_pii"] = detected
            result["pii_count"] = sum(len(v) for v in detected.values())

        elif mode == "mask":
            detected = detect_pii(text)
            mask_result = mask_pii(text, detected)
            result["filtered_text"] = mask_result["masked_text"]
            result["pii_summary"] = mask_result["pii_summary"]
            result["masked_count"] = mask_result["original_pii_count"]

            # Optional verification
            if verify:
                verification = verify_pii_removal(mask_result["masked_text"])
                result["verification"] = verification
                if not verification["is_safe"]:
                    result["status"] = "warning"
                    result["warning"] = "Some PII may remain after masking"

        elif mode == "verify":
            verification = verify_pii_removal(text)
            result.update(verification)
            result["status"] = "safe" if verification["is_safe"] else "unsafe"

        else:
            result["status"] = "error"
            result["error"] = f"Invalid mode: {mode}"

    except Exception as e:
        logger.error(f"Security filter error: {e}")
        result["status"] = "error"
        result["error"] = str(e)

    return result


# Pre-defined security policies for different document types
SECURITY_POLICIES = {
    "birth_certificate": {
        "allowed_pii": ["date_of_birth"],  # DOB is expected in birth certificates
        "mask_required": ["national_id_spain", "ssn", "phone", "email"],
        "strict_mode": True
    },
    "passport": {
        "allowed_pii": ["passport", "date_of_birth"],
        "mask_required": ["national_id_spain", "ssn", "phone", "email", "credit_card"],
        "strict_mode": True
    },
    "general": {
        "allowed_pii": [],
        "mask_required": list(PII_PATTERNS.keys()),
        "strict_mode": True
    }
}


def apply_policy(text: str, document_type: str = "general") -> dict:
    """
    Apply document-type-specific security policy.

    Args:
        text: Text to filter
        document_type: Type of document (birth_certificate, passport, general)

    Returns:
        Filtered text with policy metadata
    """
    policy = SECURITY_POLICIES.get(document_type, SECURITY_POLICIES["general"])

    # Detect all PII
    detected = detect_pii(text)

    # Separate allowed vs. mask-required PII
    pii_to_mask = {}
    allowed_pii_found = {}

    for pii_type, matches in detected.items():
        if pii_type in policy["allowed_pii"]:
            allowed_pii_found[pii_type] = matches
        else:
            pii_to_mask[pii_type] = matches

    # Mask only the required PII
    mask_result = mask_pii(text, pii_to_mask)

    return {
        "status": "success",
        "filtered_text": mask_result["masked_text"],
        "policy_applied": document_type,
        "pii_masked": mask_result["pii_summary"],
        "pii_allowed": {k: len(v) for k, v in allowed_pii_found.items()},
        "strict_mode": policy["strict_mode"]
    }
