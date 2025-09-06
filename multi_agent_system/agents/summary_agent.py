"""
Summary Agent for Website Content Summarization

This agent creates concise summaries of website content with focus on:
- Key information extraction
- Content structure analysis
- Main topics and themes
- Integration with classifier results
"""

from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from multi_agent_system.core.config import config
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
import os
import logging
import time
import re

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAX_WORD_COUNT = 150
MAX_SENTENCES = 5
MIN_SENTENCES = 3


class SummaryResult(BaseModel):
    """Pydantic model for summary results validation."""
    summary: str = Field(..., description="The main summary text")
    word_count: int = Field(..., description="Number of words in the summary")
    sentence_count: int = Field(..., description="Number of sentences in the summary")
    key_points: list[str] = Field(default_factory=list, description="Key points extracted")
    
    @validator('summary')
    def summary_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 20:
            raise ValueError('Summary must be at least 20 characters long')
        return v.strip()
    
    @validator('word_count')
    def word_count_must_be_valid(cls, v, values):
        if 'summary' in values:
            actual_word_count = len(values['summary'].split())
            if abs(v - actual_word_count) > 5:  # Allow small discrepancy
                logger.warning(f"Word count mismatch: declared {v}, actual {actual_word_count}")
        return v
    
    @validator('sentence_count')
    def sentence_count_must_be_valid(cls, v):
        if v < MIN_SENTENCES or v > MAX_SENTENCES:
            raise ValueError(f'Sentence count must be between {MIN_SENTENCES} and {MAX_SENTENCES}')
        return v


class SummaryAgent:
    """Agent responsible for creating concise website summaries."""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview", max_retries: int = 3):
        """
        Initialize the Summary Agent.
        
        Args:
            model_name: OpenAI model to use
            max_retries: Maximum number of retry attempts
        """
        self.model_name = model_name
        self.max_retries = max_retries
        
        # Initialize LLM using centralized config
        openai_cfg = config.get_openai_config()
        self.llm = ChatOpenAI(
            model=model_name or openai_cfg["model"],
            temperature=0.2 if 0.2 is not None else openai_cfg["temperature"],
            api_key=openai_cfg["api_key"],
            base_url=openai_cfg.get("base_url")
        )
        
        # Initialize CrewAI Agent
        self.agent = Agent(
            role="Content Analysis Specialist",
            goal="Create concise 3-5 sentence summary of website content",
            backstory="""Ты опытный аналитик контента. Создай краткое резюме из 3-5 предложений, которое отражает основную суть и ключевые моменты веб-сайта. Будь лаконичным и информативным.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3
        )
    
    def get_agent(self) -> Agent:
        """Return the configured CrewAI agent."""
        return self.agent
    
    def _create_summary_task(self, website_data: Dict[str, Any], classification_context: Optional[Dict[str, Any]] = None) -> Task:
        """
        Create a CrewAI task for website summarization.
        
        Args:
            website_data: Dictionary containing website content and metadata
            classification_context: Optional classification results from classifier agent
            
        Returns:
            CrewAI Task object
        """
        # Prepare content for analysis
        content_preview = website_data.get('content', '')[:3000]  # Limit content length
        title = website_data.get('title', 'N/A')
        description = website_data.get('meta_description', 'N/A')
        url = website_data.get('url', 'N/A')
        
        # Build context from classification if available
        classification_info = ""
        if classification_context and classification_context.get('success'):
            classification = classification_context.get('classification', {})
            classification_info = f"""
        Контекст классификации:
        - Тип сайта: {classification.get('type', 'неизвестно')}
        - Индустрия: {classification.get('industry', 'неизвестно')}
        - Целевая аудитория: {classification.get('target_audience', 'неизвестно')}
        - Бизнес-модель: {classification.get('business_model', 'неизвестно')}
        """
        
        task_description = f"""
        Создай краткое резюме веб-сайта из 3-5 предложений:
        
        URL: {url}
        Заголовок: {title}
        Описание: {description}
        {classification_info}
        Контент: {content_preview}
        
        Требования к резюме:
        - От 3 до 5 предложений
        - Максимум {MAX_WORD_COUNT} слов
        - Отрази основную суть и ключевые моменты
        - Будь лаконичным и информативным
        - Используй русский язык
        
        Верни ответ в формате:
        РЕЗЮМЕ: [твой текст резюме]
        КЛЮЧЕВЫЕ_МОМЕНТЫ: [список ключевых моментов через запятую]
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output=f"Краткое резюме из 3-5 предложений (максимум {MAX_WORD_COUNT} слов)"
        )
    
    def _parse_summary_result(self, result: str) -> SummaryResult:
        """
        Parse and validate summary result.
        
        Args:
            result: Raw result from the agent
            
        Returns:
            Validated SummaryResult object
            
        Raises:
            ValueError: If result cannot be parsed or validated
        """
        try:
            # Extract summary from result
            summary_match = re.search(r'РЕЗЮМЕ:\s*(.+?)(?=КЛЮЧЕВЫЕ_МОМЕНТЫ:|$)', result, re.DOTALL)
            if summary_match:
                summary_text = summary_match.group(1).strip()
            else:
                # Fallback: use the entire result as summary
                summary_text = result.strip()
            
            # Extract key points
            key_points_match = re.search(r'КЛЮЧЕВЫЕ_МОМЕНТЫ:\s*(.+)', result, re.DOTALL)
            key_points = []
            if key_points_match:
                key_points_text = key_points_match.group(1).strip()
                key_points = [point.strip() for point in key_points_text.split(',') if point.strip()]
            
            # Count words and sentences
            word_count = len(summary_text.split())
            sentence_count = len(re.findall(r'[.!?]+', summary_text))
            
            # Validate word count
            if word_count > MAX_WORD_COUNT:
                logger.warning(f"Summary exceeds word limit: {word_count} > {MAX_WORD_COUNT}")
                # Truncate if necessary
                words = summary_text.split()
                summary_text = ' '.join(words[:MAX_WORD_COUNT])
                word_count = MAX_WORD_COUNT
            
            # Validate sentence count
            if sentence_count < MIN_SENTENCES:
                logger.warning(f"Summary has too few sentences: {sentence_count} < {MIN_SENTENCES}")
            elif sentence_count > MAX_SENTENCES:
                logger.warning(f"Summary has too many sentences: {sentence_count} > {MAX_SENTENCES}")
            
            return SummaryResult(
                summary=summary_text,
                word_count=word_count,
                sentence_count=sentence_count,
                key_points=key_points
            )
            
        except Exception as e:
            logger.error(f"Failed to parse summary result: {e}")
            raise ValueError(f"Failed to parse summary: {e}")
    
    def summarize_website(self, website_data: Dict[str, Any], classification_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a concise summary of website content.
        
        Args:
            website_data: Dictionary containing website content, metadata, etc.
            classification_context: Optional classification results from classifier agent
            
        Returns:
            Dictionary with summary results
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Summary attempt {attempt + 1}/{self.max_retries}")
                
                # Create and execute task
                task = self._create_summary_task(website_data, classification_context)
                result = task.execute()
                
                # Parse and validate result
                summary = self._parse_summary_result(result)
                
                logger.info(f"Summary successful: {summary.word_count} words, {summary.sentence_count} sentences")
                
                return {
                    "success": True,
                    "summary": summary.dict(),
                    "attempt": attempt + 1,
                    "timestamp": time.time()
                }
                
            except Exception as e:
                logger.error(f"Summary attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    # Last attempt failed
                    return {
                        "success": False,
                        "error": str(e),
                        "attempts": self.max_retries,
                        "timestamp": time.time()
                    }
                
                # Wait before retry
                time.sleep(1)
        
        return {
            "success": False,
            "error": "All summary attempts failed",
            "attempts": self.max_retries,
            "timestamp": time.time()
        }
    
    def summarize_website_from_url(self, url: str, classification_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Summarize website by scraping it first.
        
        Args:
            url: Website URL to summarize
            classification_context: Optional classification results from classifier agent
            
        Returns:
            Dictionary with summary results
        """
        try:
            # Import scraping tool
            from multi_agent_system.tools.scraping_tools import create_scraping_tool
            scraping_tool = create_scraping_tool()
            
            logger.info(f"Scraping website for summary: {url}")
            
            # Scrape website
            if hasattr(scraping_tool, 'func'):
                # CrewAI Tool
                scraped_data = scraping_tool.func(url)
                # Convert string result back to dict (simplified)
                website_data = {
                    "url": url,
                    "content": scraped_data,
                    "title": "",
                    "meta_description": ""
                }
            else:
                # Direct WebScrapingTool
                website_data = scraping_tool.scrape_website(url)
            
            if 'error' in website_data:
                return {
                    "success": False,
                    "error": f"Scraping failed: {website_data['error']}",
                    "timestamp": time.time()
                }
            
            # Summarize the scraped data
            return self.summarize_website(website_data, classification_context)
            
        except Exception as e:
            logger.error(f"Failed to summarize website from URL: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
