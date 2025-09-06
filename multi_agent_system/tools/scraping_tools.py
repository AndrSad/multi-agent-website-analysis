"""
Web Scraping Tools for Website Analysis

This module provides comprehensive web scraping capabilities for the multi-agent system.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import time
import re
import logging
from urllib.parse import urljoin, urlparse
import os
try:
    from crewai import Tool
except ImportError:
    # Fallback for different CrewAI versions
    Tool = None

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAX_TEXT_LENGTH = 8000
DEFAULT_TIMEOUT = 30
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def fetch_html_content(url: str, timeout: int = DEFAULT_TIMEOUT, user_agent: str = None) -> str:
    """
    Fetch HTML content from a URL with error handling and timeouts.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        user_agent: Custom user agent string
        
    Returns:
        HTML content as string
        
    Raises:
        requests.RequestException: If request fails
        ValueError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    
    user_agent = user_agent or os.getenv("SCRAPING_USER_AGENT", DEFAULT_USER_AGENT)
    
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        logger.info(f"Fetching HTML content from: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            logger.warning(f"Content type is not HTML: {content_type}")
        
        logger.info(f"Successfully fetched {len(response.content)} bytes from {url}")
        return response.text
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching {url}")
        raise requests.RequestException(f"Request timeout after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching {url}")
        raise requests.RequestException("Connection error")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching {url}: {e}")
        raise requests.RequestException(f"HTTP error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching {url}: {e}")
        raise requests.RequestException(f"Unexpected error: {e}")


def extract_clean_text(html: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    """
    Extract clean text from HTML content with length limitation.
    
    Args:
        html: HTML content as string
        max_length: Maximum length of extracted text
        
    Returns:
        Clean text content
    """
    if not html or not isinstance(html, str):
        return ""
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit text length
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.info(f"Text truncated to {max_length} characters")
        
        logger.info(f"Extracted {len(text)} characters of clean text")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting clean text: {e}")
        return ""


class WebScrapingTool:
    """Tool for scraping website content and extracting relevant data."""
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, user_agent: str = None):
        """
        Initialize the web scraping tool.
        
        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or os.getenv(
            "SCRAPING_USER_AGENT", 
            DEFAULT_USER_AGENT
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape a website and extract comprehensive data.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary containing extracted website data
        """
        try:
            logger.info(f"Starting website scraping for: {url}")
            
            # Fetch HTML content
            html_content = fetch_html_content(url, self.timeout, self.user_agent)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract comprehensive data
            data = {
                'url': url,
                'status_code': 200,  # Success if we got here
                'title': self._extract_title(soup),
                'meta_description': self._extract_meta_description(soup),
                'meta_keywords': self._extract_meta_keywords(soup),
                'content': extract_clean_text(html_content),
                'headers': self._extract_headers(soup),
                'links': self._extract_links(soup, url),
                'images': self._extract_images(soup, url),
                'forms': self._extract_forms(soup),
                'buttons': self._extract_buttons(soup),
                'navigation': self._extract_navigation(soup),
                'colors': self._extract_colors(soup),
                'fonts': self._extract_fonts(soup),
                'layout_elements': self._extract_layout_elements(soup),
                'performance_metrics': self._calculate_performance_metrics(html_content),
                'scraped_at': time.time()
            }
            
            logger.info(f"Successfully scraped website: {url}")
            return data
            
        except Exception as e:
            error_msg = f"Failed to scrape website: {str(e)}"
            logger.error(f"Error scraping {url}: {error_msg}")
            return {
                'url': url,
                'error': error_msg,
                'scraped_at': time.time()
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _extract_meta_keywords(self, soup: BeautifulSoup) -> str:
        """Extract meta keywords."""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '').strip() if meta_keywords else ""
    
    def _extract_headers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all headers (h1-h6)."""
        headers = []
        for i in range(1, 7):
            for header in soup.find_all(f'h{i}'):
                headers.append({
                    'level': i,
                    'text': header.get_text().strip(),
                    'tag': f'h{i}'
                })
        return headers
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append({
                'text': link.get_text().strip(),
                'href': href,
                'absolute_url': absolute_url,
                'is_external': self._is_external_link(href, base_url)
            })
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                absolute_url = urljoin(base_url, src)
                images.append({
                    'src': src,
                    'absolute_url': absolute_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
        return images
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all forms."""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'inputs': []
            }
            
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                form_data['inputs'].append({
                    'type': input_tag.get('type', input_tag.name),
                    'name': input_tag.get('name', ''),
                    'placeholder': input_tag.get('placeholder', ''),
                    'required': input_tag.has_attr('required')
                })
            
            forms.append(form_data)
        return forms
    
    def _extract_buttons(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all buttons."""
        buttons = []
        for button in soup.find_all(['button', 'input']):
            if button.get('type') in ['button', 'submit', 'reset'] or button.name == 'button':
                buttons.append({
                    'text': button.get_text().strip() or button.get('value', ''),
                    'type': button.get('type', 'button'),
                    'class': button.get('class', [])
                })
        return buttons
    
    def _extract_navigation(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract navigation elements."""
        nav_elements = []
        
        # Look for common navigation patterns
        nav_selectors = ['nav', '.navigation', '.nav', '.menu', '.navbar']
        
        for selector in nav_selectors:
            if selector.startswith('.'):
                elements = soup.find_all(class_=selector[1:])
            else:
                elements = soup.find_all(selector)
            
            for element in elements:
                nav_elements.append({
                    'type': selector,
                    'text': element.get_text().strip()[:100],  # Limit text length
                    'links_count': len(element.find_all('a'))
                })
        
        return nav_elements
    
    def _extract_colors(self, soup: BeautifulSoup) -> List[str]:
        """Extract color information from CSS."""
        colors = set()
        
        # Extract from style attributes
        for element in soup.find_all(style=True):
            style = element['style']
            color_matches = re.findall(r'color:\s*([^;]+)', style)
            colors.update(color_matches)
            
            bg_matches = re.findall(r'background-color:\s*([^;]+)', style)
            colors.update(bg_matches)
        
        return list(colors)
    
    def _extract_fonts(self, soup: BeautifulSoup) -> List[str]:
        """Extract font information."""
        fonts = set()
        
        # Extract from style attributes
        for element in soup.find_all(style=True):
            style = element['style']
            font_matches = re.findall(r'font-family:\s*([^;]+)', style)
            fonts.update(font_matches)
        
        return list(fonts)
    
    def _extract_layout_elements(self, soup: BeautifulSoup) -> List[str]:
        """Extract layout-related elements."""
        layout_elements = []
        
        # Common layout elements
        layout_tags = ['header', 'footer', 'main', 'section', 'article', 'aside', 'div']
        
        for tag in layout_tags:
            elements = soup.find_all(tag)
            if elements:
                layout_elements.append(f"{tag}: {len(elements)}")
        
        return layout_elements
    
    def _calculate_performance_metrics(self, html_content: str) -> Dict[str, Any]:
        """Calculate basic performance metrics."""
        return {
            'content_length': len(html_content),
            'estimated_loading_time': len(html_content) / 1000000,  # Rough estimate
        }
    
    def _is_external_link(self, href: str, base_url: str) -> bool:
        """Check if link is external."""
        if href.startswith(('http://', 'https://')):
            return urlparse(href).netloc != urlparse(base_url).netloc
        return False


def create_scraping_tool():
    """Create a web scraping tool instance."""
    if Tool is not None:
        # Create CrewAI Tool if available
        scraper = WebScrapingTool()
        
        def scrape_website_tool(url: str) -> str:
            """
            Scrape a website and return formatted data for CrewAI agents.
            
            Args:
                url: Website URL to scrape
                
            Returns:
                Formatted string with website data
            """
            try:
                data = scraper.scrape_website(url)
                
                if 'error' in data:
                    return f"Error scraping {url}: {data['error']}"
                
                # Format data for agent consumption
                result = f"""
Website Analysis for: {data['url']}

Title: {data['title']}
Description: {data['meta_description']}
Content Length: {len(data['content'])} characters

Content Preview:
{data['content'][:500]}...

Headers Found: {len(data['headers'])}
Links Found: {len(data['links'])}
Images Found: {len(data['images'])}
Forms Found: {len(data['forms'])}

Scraped at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['scraped_at']))}
"""
                return result
                
            except Exception as e:
                return f"Error in scraping tool: {str(e)}"
        
        return Tool(
            name="Web Scraping Tool",
            description="Scrapes website content and extracts comprehensive data including text, links, images, forms, and metadata. Use this tool to analyze any website.",
            func=scrape_website_tool
        )
    else:
        # Return simple tool instance if CrewAI Tool is not available
        return WebScrapingTool()
