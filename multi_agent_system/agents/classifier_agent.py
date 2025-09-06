"""
Classifier Agent for Website Content Categorization

This agent analyzes website content and categorizes it based on:
- Website type (landing page, blog, e-commerce, etc.)
- Industry/domain
- Content type
- Target audience
- Business model
"""

from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from multi_agent_system.core.config import config
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
import os
import json
import logging
import time
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class WebsiteType(str, Enum):
    """Enumeration of possible website types."""
    LANDING_PAGE = "landing_page"
    BLOG = "blog"
    E_COMMERCE = "e_commerce"
    MARKETPLACE = "marketplace"
    CORPORATE = "corporate"
    PORTFOLIO = "portfolio"
    NEWS = "news"
    EDUCATIONAL = "educational"
    SOCIAL_MEDIA = "social_media"
    FORUM = "forum"
    WIKI = "wiki"
    OTHER = "other"


class ClassificationResult(BaseModel):
    """Pydantic model for classification results validation."""
    type: WebsiteType = Field(..., description="The type of website")
    reason: str = Field(..., description="Explanation for the classification")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    industry: Optional[str] = Field(None, description="Industry or domain")
    target_audience: Optional[str] = Field(None, description="Target audience")
    business_model: Optional[str] = Field(None, description="Business model")
    
    @validator('reason')
    def reason_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Reason must be at least 10 characters long')
        return v.strip()
    
    @validator('confidence')
    def confidence_must_be_valid(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Confidence must be a number')
        return float(v)


class ClassifierAgent:
    """Agent responsible for classifying and categorizing website content."""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview", max_retries: int = 3):
        """
        Initialize the Classifier Agent.
        
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
            temperature=0.1 if 0.1 is not None else openai_cfg["temperature"],
            api_key=openai_cfg["api_key"],
            base_url=openai_cfg.get("base_url")
        )
        
        # Initialize CrewAI Agent
        self.agent = Agent(
            role="Content Classification Expert",
            goal="Analyze website text and classify its type (landing page, blog, e-commerce, etc.)",
            backstory="""Ты эксперт по классификации веб-сайтов. Проанализируй предоставленный текст и определи тип сайта: лендинг, блог, маркетплейс, корпоративный сайт или другой тип. Верни ответ в формате JSON с полями 'type' и 'reason'.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3
        )
        
        # Import scraping tool
        try:
            from multi_agent_system.tools.scraping_tools import create_scraping_tool
            self.scraping_tool = create_scraping_tool()
            logger.info("Scraping tool loaded successfully")
        except ImportError as e:
            logger.error(f"Failed to import scraping tool: {e}")
            self.scraping_tool = None
    
    def get_agent(self) -> Agent:
        """Return the configured CrewAI agent."""
        return self.agent
    
    def _create_classification_task(self, website_data: Dict[str, Any]) -> Task:
        """
        Create a CrewAI task for website classification.
        
        Args:
            website_data: Dictionary containing website content and metadata
            
        Returns:
            CrewAI Task object
        """
        # Prepare content for analysis
        content_preview = website_data.get('content', '')[:2000]  # Limit content length
        title = website_data.get('title', 'N/A')
        description = website_data.get('meta_description', 'N/A')
        url = website_data.get('url', 'N/A')
        
        task_description = f"""
        Проанализируй следующий веб-сайт и определи его тип:
        
        URL: {url}
        Заголовок: {title}
        Описание: {description}
        Контент: {content_preview}
        
        Возможные типы сайтов:
        - landing_page: Лендинговая страница
        - blog: Блог или новостной сайт
        - e_commerce: Интернет-магазин
        - marketplace: Маркетплейс
        - corporate: Корпоративный сайт
        - portfolio: Портфолио
        - news: Новостной сайт
        - educational: Образовательный сайт
        - social_media: Социальная сеть
        - forum: Форум
        - wiki: Вики
        - other: Другой тип
        
        Верни ответ ТОЛЬКО в формате JSON:
        {{
            "type": "тип_сайта",
            "reason": "подробное объяснение классификации",
            "confidence": 0.95,
            "industry": "индустрия (опционально)",
            "target_audience": "целевая аудитория (опционально)",
            "business_model": "бизнес-модель (опционально)"
        }}
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON объект с классификацией сайта"
        )
    
    def _parse_classification_result(self, result: str) -> ClassificationResult:
        """
        Parse and validate classification result.
        
        Args:
            result: Raw result from the agent
            
        Returns:
            Validated ClassificationResult object
            
        Raises:
            ValueError: If result cannot be parsed or validated
        """
        try:
            # Try to extract JSON from the result
            if isinstance(result, str):
                # Look for JSON in the result
                start_idx = result.find('{')
                end_idx = result.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = result[start_idx:end_idx]
                else:
                    json_str = result
                
                # Parse JSON
                data = json.loads(json_str)
            else:
                data = result
            
            # Validate with Pydantic
            return ClassificationResult(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Failed to validate classification result: {e}")
            raise ValueError(f"Validation error: {e}")
    
    def classify_website(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify website content and return structured analysis.
        
        Args:
            website_data: Dictionary containing website content, metadata, etc.
            
        Returns:
            Dictionary with classification results
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Classification attempt {attempt + 1}/{self.max_retries}")
                
                # Create and execute task
                task = self._create_classification_task(website_data)
                result = task.execute()
                
                # Parse and validate result
                classification = self._parse_classification_result(result)
                
                logger.info(f"Classification successful: {classification.type}")
                
                return {
                    "success": True,
                    "classification": classification.dict(),
                    "attempt": attempt + 1,
                    "timestamp": time.time()
                }
                
            except Exception as e:
                logger.error(f"Classification attempt {attempt + 1} failed: {e}")
                
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
            "error": "All classification attempts failed",
            "attempts": self.max_retries,
            "timestamp": time.time()
        }
    
    def classify_website_from_url(self, url: str) -> Dict[str, Any]:
        """
        Classify website by scraping it first.
        
        Args:
            url: Website URL to classify
            
        Returns:
            Dictionary with classification results
        """
        if not self.scraping_tool:
            return {
                "success": False,
                "error": "Scraping tool not available",
                "timestamp": time.time()
            }
        
        try:
            logger.info(f"Scraping website: {url}")
            
            # Scrape website
            if hasattr(self.scraping_tool, 'func'):
                # CrewAI Tool
                scraped_data = self.scraping_tool.func(url)
                # Convert string result back to dict (simplified)
                website_data = {
                    "url": url,
                    "content": scraped_data,
                    "title": "",
                    "meta_description": ""
                }
            else:
                # Direct WebScrapingTool
                website_data = self.scraping_tool.scrape_website(url)
            
            if 'error' in website_data:
                return {
                    "success": False,
                    "error": f"Scraping failed: {website_data['error']}",
                    "timestamp": time.time()
                }
            
            # Classify the scraped data
            return self.classify_website(website_data)
            
        except Exception as e:
            logger.error(f"Failed to classify website from URL: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
