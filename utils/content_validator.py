from typing import List, Dict, Optional, Any
import re
from urllib.parse import urlparse
from mimetypes import guess_type

class ContentValidator:
    def __init__(self):
        self.allowed_content_types = [
            "text/html",
            "text/plain",
            "application/pdf",
            "application/json"
        ]
        
        self.blocked_domains = set()
        self.max_content_size = 10 * 1024 * 1024  # 10MB
        
    def is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def is_allowed_content_type(self, content_type: str) -> bool:
        return content_type in self.allowed_content_types
    
    def is_allowed_size(self, content_size: int) -> bool:
        return content_size <= self.max_content_size
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        # Check for potentially malicious content
        if re.search(r"<script.*?>", content, re.I):
            return {"valid": False, "reason": "Contains script tags"}
            
        # Check for minimum content length
        if len(content.strip()) < 10:
            return {"valid": False, "reason": "Content too short"}
            
        return {"valid": True, "reason": "Content passed validation"}