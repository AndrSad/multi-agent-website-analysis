"""
Multi-Agent Orchestrator for Website Analysis

This module coordinates the work of multiple agents to provide comprehensive
website analysis including classification, summarization, UX review, and design advice.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import json
import hashlib

# Third-party imports
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import aiohttp

# Local imports
from multi_agent_system.core.config import config
from multi_agent_system.agents.classifier_agent import ClassifierAgent
from multi_agent_system.agents.summary_agent import SummaryAgent
from multi_agent_system.agents.ux_reviewer_agent import UXReviewerAgent
from multi_agent_system.agents.design_advisor_agent import DesignAdvisorAgent
from multi_agent_system.tools.scraping_tools import create_scraping_tool


@dataclass
class AnalysisResult:
    """Data class for analysis results."""
    url: str
    website_data: Dict[str, Any]
    classification: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    ux_review: Optional[Dict[str, Any]] = None
    design_advice: Optional[Dict[str, Any]] = None
    status: str = "pending"
    timestamp: float = 0
    error: Optional[str] = None


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    async def acquire(self, key: str = "default") -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            key: Rate limit key (e.g., user ID, IP address)
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.time_window
        ]
        
        # Check if we can make a new request
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    async def wait_for_slot(self, key: str = "default") -> None:
        """Wait until a request slot is available."""
        while not await self.acquire(key):
            await asyncio.sleep(1)


class CacheManager:
    """Simple in-memory cache manager."""
    
    def __init__(self, ttl: int = 3600):  # 1 hour TTL
        """
        Initialize cache manager.
        
        Args:
            ttl: Time to live in seconds
        """
        self.cache = {}
        self.ttl = ttl
    
    def _generate_key(self, url: str, analysis_type: str = "full") -> str:
        """Generate cache key for URL and analysis type."""
        content = f"{url}:{analysis_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, url: str, analysis_type: str = "full") -> Optional[Dict[str, Any]]:
        """Get cached result."""
        key = self._generate_key(url, analysis_type)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            else:
                del self.cache[key]
        return None
    
    def set(self, url: str, result: Dict[str, Any], analysis_type: str = "full") -> None:
        """Set cached result."""
        key = self._generate_key(url, analysis_type)
        self.cache[key] = (result, time.time())
    
    def clear(self) -> None:
        """Clear all cached results."""
        self.cache.clear()


class CrewOrchestrator:
    """Advanced orchestrator for multi-agent website analysis."""
    
    def __init__(self):
        """Initialize the orchestrator with all agents and tools."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self.classifier_agent = ClassifierAgent()
        self.summary_agent = SummaryAgent()
        self.ux_reviewer_agent = UXReviewerAgent()
        self.design_advisor_agent = DesignAdvisorAgent()
        
        # Initialize tools
        self.scraping_tool = create_scraping_tool()
        
        # Initialize rate limiter and cache
        self.rate_limiter = RateLimiter(
            max_requests=config.rate_limit_per_minute,
            time_window=60
        )
        self.cache = CacheManager()
        
        # Analysis statistics
        self.stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    async def analyze_website(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Perform comprehensive website analysis using all agents.
        
        Args:
            url: Website URL to analyze
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing analysis results from all agents
        """
        self.stats['total_analyses'] += 1
        
        try:
            # Check cache first
            if use_cache:
                cached_result = self.cache.get(url, "full")
                if cached_result:
                    self.stats['cache_hits'] += 1
                    self.logger.info(f"Cache hit for URL: {url}")
                    return cached_result
                self.stats['cache_misses'] += 1
            
            # Apply rate limiting
            await self.rate_limiter.wait_for_slot()
            
            self.logger.info(f"Starting comprehensive analysis of website: {url}")
            
            # Step 1: Load and parse content
            website_data = await self._scrape_website_with_retry(url)
            
            if 'error' in website_data:
                self.stats['failed_analyses'] += 1
                return {
                    'error': f"Failed to scrape website: {website_data['error']}",
                    'url': url,
                    'status': 'failed',
                    'timestamp': time.time()
                }
            
            # Step 2: Run classifier first
            classification_result = await self._run_classifier_with_retry(website_data)
            
            # Step 3: Run summary and UX agents in parallel
            summary_task = asyncio.create_task(
                self._run_summary_with_retry(website_data, classification_result)
            )
            ux_review_task = asyncio.create_task(
                self._run_ux_reviewer_with_retry(website_data, classification_result)
            )
            
            # Wait for parallel tasks to complete
            summary_result, ux_review_result = await asyncio.gather(
                summary_task, ux_review_task, return_exceptions=True
            )
            
            # Handle exceptions from parallel tasks
            if isinstance(summary_result, Exception):
                self.logger.error(f"Summary task failed: {summary_result}")
                summary_result = {'success': False, 'error': str(summary_result)}
            
            if isinstance(ux_review_result, Exception):
                self.logger.error(f"UX review task failed: {ux_review_result}")
                ux_review_result = {'success': False, 'error': str(ux_review_result)}
            
            # Step 4: Conditionally run UI designer (only for landing pages)
            design_advice_result = None
            if (classification_result and 
                classification_result.get('success') and 
                classification_result.get('classification', {}).get('type') == 'landing_page'):
                
                design_advice_result = await self._run_design_advisor_with_retry(
                    website_data, classification_result
                )
            
            # Step 5: Aggregate results
            analysis_result = self._aggregate_results(
                url, website_data, classification_result, 
                summary_result, ux_review_result, design_advice_result
            )
            
            # Cache the result
            if use_cache:
                self.cache.set(url, analysis_result, "full")
            
            self.stats['successful_analyses'] += 1
            self.logger.info(f"Analysis completed for website: {url}")
            return analysis_result
            
        except Exception as e:
            self.stats['failed_analyses'] += 1
            self.logger.error(f"Error analyzing website {url}: {str(e)}")
            return {
                'error': f"Analysis failed: {str(e)}",
                'url': url,
                'status': 'failed',
                'timestamp': time.time()
            }
    
    async def get_quick_analysis(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get a quick analysis using only the classifier and summary agents.
        
        Args:
            url: Website URL to analyze
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing quick analysis results
        """
        self.stats['total_analyses'] += 1
        
        try:
            # Check cache first
            if use_cache:
                cached_result = self.cache.get(url, "quick")
                if cached_result:
                    self.stats['cache_hits'] += 1
                    self.logger.info(f"Cache hit for quick analysis of URL: {url}")
                    return cached_result
                self.stats['cache_misses'] += 1
            
            # Apply rate limiting
            await self.rate_limiter.wait_for_slot()
            
            self.logger.info(f"Starting quick analysis of website: {url}")
            
            # Scrape the website
            website_data = await self._scrape_website_with_retry(url)
            
            if 'error' in website_data:
                self.stats['failed_analyses'] += 1
                return {
                    'error': f"Failed to scrape website: {website_data['error']}",
                    'url': url,
                    'status': 'failed',
                    'timestamp': time.time()
                }
            
            # Run classifier and summary in parallel
            classification_task = asyncio.create_task(
                self._run_classifier_with_retry(website_data)
            )
            summary_task = asyncio.create_task(
                self._run_summary_with_retry(website_data, None)
            )
            
            # Wait for both tasks to complete
            classification_result, summary_result = await asyncio.gather(
                classification_task, summary_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(classification_result, Exception):
                self.logger.error(f"Classification task failed: {classification_result}")
                classification_result = {'success': False, 'error': str(classification_result)}
            
            if isinstance(summary_result, Exception):
                self.logger.error(f"Summary task failed: {summary_result}")
                summary_result = {'success': False, 'error': str(summary_result)}
            
            # Aggregate results
            quick_result = {
                'url': url,
                'website_data': website_data,
                'classification': classification_result,
                'summary': summary_result,
                'status': 'completed',
                'timestamp': time.time(),
                'analysis_type': 'quick'
            }
            
            # Cache the result
            if use_cache:
                self.cache.set(url, quick_result, "quick")
            
            self.stats['successful_analyses'] += 1
            self.logger.info(f"Quick analysis completed for website: {url}")
            return quick_result
            
        except Exception as e:
            self.stats['failed_analyses'] += 1
            self.logger.error(f"Error in quick analysis of website {url}: {str(e)}")
            return {
                'error': f"Quick analysis failed: {str(e)}",
                'url': url,
                'status': 'failed',
                'timestamp': time.time()
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def _scrape_website_with_retry(self, url: str) -> Dict[str, Any]:
        """Scrape website with retry logic."""
        try:
            if hasattr(self.scraping_tool, 'func'):
                # CrewAI Tool
                result = self.scraping_tool.func(url)
                return {
                    'url': url,
                    'content': result,
                    'title': '',
                    'meta_description': '',
                    'scraped_at': time.time()
                }
            else:
                # Direct WebScrapingTool
                return self.scraping_tool.scrape_website(url)
        except Exception as e:
            self.logger.error(f"Scraping failed for {url}: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def _run_classifier_with_retry(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run classifier with retry logic."""
        try:
            return self.classifier_agent.classify_website(website_data)
        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def _run_summary_with_retry(self, website_data: Dict[str, Any], 
                                    classification_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Run summary agent with retry logic."""
        try:
            return self.summary_agent.summarize_website(website_data, classification_context)
        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def _run_ux_reviewer_with_retry(self, website_data: Dict[str, Any], 
                                        classification_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Run UX reviewer with retry logic."""
        try:
            return self.ux_reviewer_agent.review_ux(website_data, classification_context)
        except Exception as e:
            self.logger.error(f"UX review failed: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def _run_design_advisor_with_retry(self, website_data: Dict[str, Any], 
                                           classification_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Run design advisor with retry logic."""
        try:
            return self.design_advisor_agent.advise_design(website_data, classification_context)
        except Exception as e:
            self.logger.error(f"Design advice failed: {e}")
            raise
    
    def _aggregate_results(self, url: str, website_data: Dict[str, Any], 
                          classification_result: Optional[Dict[str, Any]],
                          summary_result: Optional[Dict[str, Any]],
                          ux_review_result: Optional[Dict[str, Any]],
                          design_advice_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from all agents."""
        
        # Determine overall status
        all_results = [classification_result, summary_result, ux_review_result, design_advice_result]
        successful_results = [r for r in all_results if r and r.get('success', False)]
        
        if len(successful_results) == 0:
            status = 'failed'
        elif len(successful_results) == len([r for r in all_results if r is not None]):
            status = 'completed'
        else:
            status = 'partial'
        
        # Create aggregated result
        aggregated_result = {
            'url': url,
            'website_data': website_data,
            'classification': classification_result,
            'summary': summary_result,
            'ux_review': ux_review_result,
            'design_advice': design_advice_result,
            'status': status,
            'timestamp': time.time(),
            'analysis_type': 'full',
            'success_rate': len(successful_results) / len([r for r in all_results if r is not None]) if any(all_results) else 0
        }
        
        # Add metadata
        aggregated_result['metadata'] = {
            'agents_used': len([r for r in all_results if r is not None]),
            'successful_agents': len(successful_results),
            'failed_agents': len([r for r in all_results if r and not r.get('success', False)]),
            'is_landing_page': (classification_result and 
                              classification_result.get('success') and 
                              classification_result.get('classification', {}).get('type') == 'landing_page')
        }
        
        return aggregated_result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            'stats': self.stats.copy(),
            'cache_size': len(self.cache.cache),
            'rate_limiter_requests': {
                key: len(requests) for key, requests in self.rate_limiter.requests.items()
            }
        }
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.logger.info("Cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information."""
        return {
            'cache_size': len(self.cache.cache),
            'cache_ttl': self.cache.ttl,
            'cache_keys': list(self.cache.cache.keys())
        }


# Backward compatibility
class MultiAgentOrchestrator(CrewOrchestrator):
    """Backward compatibility wrapper for the old orchestrator."""
    
    def __init__(self):
        super().__init__()
        self.logger.warning("MultiAgentOrchestrator is deprecated. Use CrewOrchestrator instead.")
    
    def analyze_website(self, url: str) -> Dict[str, Any]:
        """Synchronous wrapper for analyze_website."""
        return asyncio.run(super().analyze_website(url))
    
    def get_quick_analysis(self, url: str) -> Dict[str, Any]:
        """Synchronous wrapper for get_quick_analysis."""
        return asyncio.run(super().get_quick_analysis(url))
