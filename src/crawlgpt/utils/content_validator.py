from typing import List, Dict, Optional, Any
import re
from urllib.parse import urlparse
from mimetypes import guess_type

class ContentValidator:
    """
    A validator class for content and URLs in the web crawler.

    This class provides methods to validate URLs, content types, and content size
    to ensure they meet the requirements for processing.

    Attributes:
        allowed_content_types (List[str]): List of acceptable MIME types
        blocked_domains (set): Set of domains that are blocked
        max_content_size (int): Maximum allowed content size in bytes (10MB)

    Example:
        >>> validator = ContentValidator()
        >>> validator.is_valid_url("https://example.com")
        True
    """
    def __init__(self):
        """Initialize the ContentValidator with default settings."""
        self.allowed_content_types = [
            "text/html",
            "text/plain",
            "application/pdf",
            "application/json"
        ]
        
        self.blocked_domains = set()
        self.max_content_size = 10 * 1024 * 1024  # 10MB MAX SIZE LIMIT OF GROQ API IS 25MB We are using 10MB
        
    def is_valid_url(self, url: str) -> bool:
        """
        Validate if the given URL is properly formatted.

        Args:
            url (str): The URL to validate

        Returns:
            bool: True if URL is valid, False otherwise

        Example:
            >>> validator.is_valid_url("https://example.com")
            True
            >>> validator.is_valid_url("not-a-url")
            False
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def is_allowed_content_type(self, content_type: str) -> bool:
        """
        Check if the content type is in the allowed list.

        Args:
            content_type (str): MIME type to check

        Returns:
            bool: True if content type is allowed, False otherwise

        Example:
            >>> validator.is_allowed_content_type("text/html")
            True
            >>> validator.is_allowed_content_type("image/jpeg")
            False
        """
        return content_type in self.allowed_content_types
    
    def is_allowed_size(self, content_size: int) -> bool:
        """
        Check if the content size is within the allowed limit.
        
        Args:
            content_size (int): Size of the content in bytes
        
        Returns:
            bool: True if content size is within limit, False otherwise

        Example:
            >>> validator.is_allowed_size(1024)
            True
            >>> validator.is_allowed_size(1024 * 1024 * 20)  # 20MB
            False
        """
        return content_size <= self.max_content_size
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        Validate the content for potential issues.

        This method checks the content for malicious content, length, etc.
        and returns a dictionary with validation results.

        Args:
            content (str): The content to validate
        
        Returns:
            Dict[str, Any]: A dictionary with validation results

        Example:
            >>> validator.validate_content("<p>Hello, World!</p>")
            {'valid': True, 'reason': 'Content passed validation'}
            >>> validator.validate_content("<script>alert('XSS')</script>")
            {'valid': False, 'reason': 'Contains script tags'}
        """
        # Check for potentially malicious content
        if re.search(r"<script.*?>", content, re.I):
            return {"valid": False, "reason": "Contains script tags"}
            
        # Check for minimum content length
        if len(content.strip()) < 10:
            return {"valid": False, "reason": "Content too short"}
            
        return {"valid": True, "reason": "Content passed validation"}