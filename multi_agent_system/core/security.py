"""
Security module for production-ready multi-agent system.

This module provides security utilities including URL validation,
XSS protection, input sanitization, and content filtering.
"""

import re
import html
import urllib.parse
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urljoin
import bleach
import validators
from pydantic import BaseModel, Field, validator
import hashlib
import time

logger = logging.getLogger(__name__)


class SecurityConfig(BaseModel):
    """Security configuration model."""
    max_url_length: int = Field(default=2048, description="Maximum URL length")
    max_content_length: int = Field(default=1000000, description="Maximum content length (1MB)")
    max_request_size: int = Field(default=10485760, description="Maximum request size (10MB)")
    allowed_schemes: List[str] = Field(default=["http", "https"], description="Allowed URL schemes")
    blocked_domains: List[str] = Field(default_factory=list, description="Blocked domains")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    max_requests_per_window: int = Field(default=100, description="Max requests per window")
    enable_content_filtering: bool = Field(default=True, description="Enable content filtering")
    enable_xss_protection: bool = Field(default=True, description="Enable XSS protection")


class URLValidator:
    """URL validation and sanitization utility."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._malicious_patterns = [
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'onclick=',
            r'<script',
            r'</script>',
            r'<iframe',
            r'</iframe>',
            r'<object',
            r'<embed',
            r'<link',
            r'<meta',
            r'<style',
            r'expression\(',
            r'url\(',
            r'@import',
        ]
        self._compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self._malicious_patterns]
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate and sanitize URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Dict with validation result and sanitized URL
        """
        result = {
            'valid': False,
            'sanitized_url': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Basic length check
            if len(url) > self.config.max_url_length:
                result['errors'].append(f"URL too long: {len(url)} > {self.config.max_url_length}")
                return result
            
            # Decode URL
            try:
                decoded_url = urllib.parse.unquote(url)
            except Exception as e:
                result['errors'].append(f"URL decoding failed: {str(e)}")
                return result
            
            # Check for malicious patterns
            for pattern in self._compiled_patterns:
                if pattern.search(decoded_url):
                    result['errors'].append(f"Malicious pattern detected: {pattern.pattern}")
                    return result
            
            # Parse URL
            parsed = urlparse(decoded_url)
            
            # Validate scheme
            if parsed.scheme not in self.config.allowed_schemes:
                result['errors'].append(f"Invalid scheme: {parsed.scheme}")
                return result
            
            # Validate domain
            if not parsed.netloc:
                result['errors'].append("Missing domain")
                return result
            
            # Check blocked domains
            domain = parsed.netloc.lower()
            for blocked in self.config.blocked_domains:
                if blocked.lower() in domain:
                    result['errors'].append(f"Blocked domain: {blocked}")
                    return result
            
            # Validate with validators library
            if not validators.url(decoded_url):
                result['errors'].append("Invalid URL format")
                return result
            
            # Sanitize URL
            sanitized = self._sanitize_url(decoded_url)
            
            result['valid'] = True
            result['sanitized_url'] = sanitized
            result['parsed'] = {
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'query': parsed.query,
                'fragment': parsed.fragment
            }
            
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            result['errors'].append(f"Validation error: {str(e)}")
        
        return result
    
    def _sanitize_url(self, url: str) -> str:
        """Sanitize URL by removing dangerous components."""
        parsed = urlparse(url)
        
        # Remove dangerous query parameters
        query_params = urllib.parse.parse_qs(parsed.query)
        safe_params = {}
        
        dangerous_params = ['javascript', 'data', 'vbscript', 'onload', 'onerror', 'onclick']
        for key, values in query_params.items():
            if key.lower() not in dangerous_params:
                safe_params[key] = values
        
        # Rebuild URL
        safe_query = urllib.parse.urlencode(safe_params, doseq=True)
        sanitized = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            safe_query,
            parsed.fragment
        ))
        
        return sanitized


class ContentFilter:
    """Content filtering and sanitization utility."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre'
        ]
        self._allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }
    
    def sanitize_content(self, content: str) -> Dict[str, Any]:
        """
        Sanitize content to prevent XSS and injection attacks.
        
        Args:
            content: Content to sanitize
            
        Returns:
            Dict with sanitization result
        """
        result = {
            'sanitized': None,
            'original_length': len(content),
            'sanitized_length': 0,
            'removed_tags': [],
            'warnings': []
        }
        
        try:
            # Length check
            if len(content) > self.config.max_content_length:
                result['warnings'].append(f"Content too long: {len(content)} > {self.config.max_content_length}")
                content = content[:self.config.max_content_length]
            
            if self.config.enable_xss_protection:
                # HTML escape
                escaped_content = html.escape(content)
                
                # Use bleach for additional sanitization
                sanitized = bleach.clean(
                    escaped_content,
                    tags=self._allowed_tags,
                    attributes=self._allowed_attributes,
                    strip=True
                )
                
                result['sanitized'] = sanitized
                result['sanitized_length'] = len(sanitized)
                
                # Check for removed content
                if len(sanitized) < len(escaped_content) * 0.8:  # More than 20% removed
                    result['warnings'].append("Significant content was removed during sanitization")
            else:
                result['sanitized'] = content
                result['sanitized_length'] = len(content)
            
        except Exception as e:
            logger.error(f"Content sanitization error: {str(e)}")
            result['sanitized'] = ""
            result['warnings'].append(f"Sanitization error: {str(e)}")
        
        return result
    
    def detect_malicious_content(self, content: str) -> List[str]:
        """
        Detect potentially malicious content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of detected threats
        """
        threats = []
        
        # Check for script tags
        if re.search(r'<script[^>]*>', content, re.IGNORECASE):
            threats.append("Script tag detected")
        
        # Check for iframe tags
        if re.search(r'<iframe[^>]*>', content, re.IGNORECASE):
            threats.append("Iframe tag detected")
        
        # Check for javascript: URLs
        if re.search(r'javascript:', content, re.IGNORECASE):
            threats.append("JavaScript URL detected")
        
        # Check for data: URLs
        if re.search(r'data:', content, re.IGNORECASE):
            threats.append("Data URL detected")
        
        # Check for event handlers
        event_handlers = ['onload', 'onerror', 'onclick', 'onmouseover', 'onfocus']
        for handler in event_handlers:
            if re.search(f'{handler}\\s*=', content, re.IGNORECASE):
                threats.append(f"Event handler detected: {handler}")
        
        return threats


class RateLimiter:
    """Advanced rate limiter with sliding window."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._requests = {}  # {key: [timestamps]}
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
    
    def is_allowed(self, key: str) -> Dict[str, Any]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Rate limit key (e.g., IP address, user ID)
            
        Returns:
            Dict with rate limit status
        """
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_entries(now)
            self._last_cleanup = now
        
        # Get or create request list for key
        if key not in self._requests:
            self._requests[key] = []
        
        # Remove old requests outside the window
        window_start = now - self.config.rate_limit_window
        self._requests[key] = [req_time for req_time in self._requests[key] if req_time > window_start]
        
        # Check if under limit
        if len(self._requests[key]) < self.config.max_requests_per_window:
            self._requests[key].append(now)
            return {
                'allowed': True,
                'remaining': self.config.max_requests_per_window - len(self._requests[key]),
                'reset_time': window_start + self.config.rate_limit_window
            }
        else:
            return {
                'allowed': False,
                'remaining': 0,
                'reset_time': window_start + self.config.rate_limit_window,
                'error': 'Rate limit exceeded'
            }
    
    def _cleanup_old_entries(self, now: float):
        """Clean up old rate limit entries."""
        cutoff = now - self.config.rate_limit_window * 2
        keys_to_remove = []
        
        for key, requests in self._requests.items():
            self._requests[key] = [req_time for req_time in requests if req_time > cutoff]
            if not self._requests[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._requests[key]


class SecurityManager:
    """Main security manager that coordinates all security components."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.url_validator = URLValidator(config)
        self.content_filter = ContentFilter(config)
        self.rate_limiter = RateLimiter(config)
        self.logger = logging.getLogger(__name__)
    
    def validate_request(self, url: str, content: str = "", client_ip: str = "unknown") -> Dict[str, Any]:
        """
        Comprehensive request validation.
        
        Args:
            url: Request URL
            content: Request content
            client_ip: Client IP address
            
        Returns:
            Dict with validation results
        """
        result = {
            'valid': False,
            'url_validation': None,
            'content_validation': None,
            'rate_limit': None,
            'threats': [],
            'warnings': []
        }
        
        try:
            # Rate limiting
            rate_result = self.rate_limiter.is_allowed(client_ip)
            result['rate_limit'] = rate_result
            
            if not rate_result['allowed']:
                result['threats'].append("Rate limit exceeded")
                return result
            
            # URL validation
            url_result = self.url_validator.validate_url(url)
            result['url_validation'] = url_result
            
            if not url_result['valid']:
                result['threats'].extend(url_result['errors'])
                return result
            
            # Content validation
            if content:
                content_result = self.content_filter.sanitize_content(content)
                result['content_validation'] = content_result
                
                # Check for malicious content
                threats = self.content_filter.detect_malicious_content(content)
                if threats:
                    result['threats'].extend(threats)
                    return result
                
                result['warnings'].extend(content_result['warnings'])
            
            result['valid'] = True
            
        except Exception as e:
            self.logger.error(f"Security validation error: {str(e)}")
            result['threats'].append(f"Validation error: {str(e)}")
        
        return result
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses."""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }


# Global security manager instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get global security manager instance."""
    global _security_manager
    if _security_manager is None:
        config = SecurityConfig()
        _security_manager = SecurityManager(config)
    return _security_manager
