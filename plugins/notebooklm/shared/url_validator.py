"""
URL Validation for NotebookLM URLs

Validates NotebookLM URLs to prevent SSRF and other security vulnerabilities.
Only allows HTTPS URLs to notebooklm.google.com with valid notebook paths.
"""

import re
import logging
from urllib.parse import urlparse
from typing import Optional


class URLValidationError(ValueError):
    """Raised when URL fails validation"""
    pass


class NotebookLMURLValidator:
    """
    Validates NotebookLM URLs to prevent SSRF and other attacks

    Only allows HTTPS URLs to notebooklm.google.com with valid notebook paths
    """

    ALLOWED_SCHEME = 'https'
    ALLOWED_DOMAIN = 'notebooklm.google.com'
    VALID_PATH_PATTERN = re.compile(r'^/notebook/[a-f0-9-]+(/.*)?$')

    @classmethod
    def validate(cls, url: str) -> str:
        """
        Validate and normalize a NotebookLM URL

        Args:
            url: URL string to validate

        Returns:
            Normalized URL string

        Raises:
            URLValidationError: If URL is invalid or potentially malicious
        """
        if not url or not url.strip():
            raise URLValidationError("URL cannot be empty")

        url = url.strip()

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise URLValidationError(f"Invalid URL format: {e}")

        # CRITICAL: Only allow HTTPS
        if parsed.scheme != cls.ALLOWED_SCHEME:
            raise URLValidationError(
                f"Only HTTPS URLs allowed. Got: {parsed.scheme}://"
            )

        # CRITICAL: Validate domain
        if parsed.netloc != cls.ALLOWED_DOMAIN:
            raise URLValidationError(
                f"Only {cls.ALLOWED_DOMAIN} URLs allowed. Got: {parsed.netloc}"
            )

        # Validate path format: /notebook/{uuid}
        if not cls.VALID_PATH_PATTERN.match(parsed.path):
            raise URLValidationError(
                f"Invalid NotebookLM path format. Expected: /notebook/{{uuid}}"
            )

        # SECURITY: Reject any fragments or unusual components
        if parsed.fragment:
            raise URLValidationError("URL fragments not allowed")

        # SECURITY: Warn on query parameters (unusual for NotebookLM)
        if parsed.query:
            # Log warning but allow (some NotebookLM features use query params)
            logging.warning(f"NotebookLM URL has query parameters: {parsed.query}")

        # Return normalized URL
        return parsed.geturl()

    @classmethod
    def is_valid(cls, url: str) -> bool:
        """
        Check if URL is valid without raising exception

        Args:
            url: URL to check

        Returns:
            True if valid, False otherwise
        """
        try:
            cls.validate(url)
            return True
        except URLValidationError:
            return False
