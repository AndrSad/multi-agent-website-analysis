"""
UX Reviewer Agent for User Experience Analysis

This agent evaluates website user experience with focus on:
- Usability assessment
- Navigation analysis
- Accessibility evaluation
- User journey optimization
- Professional UX recommendations
"""

from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from multi_agent_system.core.config import config
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
import os
import json
import logging
import time
import re

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAX_WORD_COUNT = 500
MIN_RECOMMENDATIONS = 5
MAX_RECOMMENDATIONS = 5


class UXRecommendation(BaseModel):
    """Pydantic model for UX recommendations."""
    title: str = Field(..., description="Title of the recommendation")
    description: str = Field(..., description="Detailed description of the recommendation")
    priority: str = Field(..., description="Priority level: high, medium, low")
    impact: str = Field(..., description="Expected impact on UX")
    
    @validator('priority')
    def priority_must_be_valid(cls, v):
        if v.lower() not in ['high', 'medium', 'low']:
            raise ValueError('Priority must be high, medium, or low')
        return v.lower()


class UXReviewResult(BaseModel):
    """Pydantic model for UX review results validation."""
    strengths: List[str] = Field(..., description="List of UX strengths")
    weaknesses: List[str] = Field(..., description="List of UX weaknesses")
    recommendations: List[UXRecommendation] = Field(..., description="List of improvement recommendations")
    overall_score: float = Field(ge=1.0, le=10.0, description="Overall UX score from 1.0 to 10.0")
    word_count: int = Field(..., description="Total word count of the review")
    
    @validator('recommendations')
    def recommendations_count_must_be_valid(cls, v):
        if len(v) < MIN_RECOMMENDATIONS:
            raise ValueError(f'Must have at least {MIN_RECOMMENDATIONS} recommendations')
        if len(v) > MAX_RECOMMENDATIONS:
            raise ValueError(f'Must have at most {MAX_RECOMMENDATIONS} recommendations')
        return v
    
    @validator('word_count')
    def word_count_must_be_valid(cls, v):
        if v > MAX_WORD_COUNT:
            raise ValueError(f'Word count must not exceed {MAX_WORD_COUNT}')
        return v


class UXReviewerAgent:
    """Agent responsible for evaluating website user experience."""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview", max_retries: int = 3):
        """
        Initialize the UX Reviewer Agent.
        
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
            temperature=0.3 if 0.3 is not None else openai_cfg["temperature"],
            api_key=openai_cfg["api_key"],
            base_url=openai_cfg.get("base_url")
        )
        
        # Initialize CrewAI Agent
        self.agent = Agent(
            role="Senior UX Analyst",
            goal="Generate detailed UX report with strengths, weaknesses and 5 improvement recommendations",
            backstory="""Ти Senior UX аналитик с 10-летним опытом. Проанализируй пользовательский опыт сайта и предоставь детальный отчет. Включи: 1) Достоинства UX, 2) Слабые места, 3) 5 конкретных рекомендаций по улучшению. Форматируй ответ как структурированный JSON.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3
        )
    
    def get_agent(self) -> Agent:
        """Return the configured CrewAI agent."""
        return self.agent
    
    def _create_ux_review_task(self, website_data: Dict[str, Any], classification_context: Optional[Dict[str, Any]] = None) -> Task:
        """
        Create a CrewAI task for UX review.
        
        Args:
            website_data: Dictionary containing website content and metadata
            classification_context: Optional classification results from classifier agent
            
        Returns:
            CrewAI Task object
        """
        # Prepare content for analysis
        content_preview = website_data.get('content', '')[:2000]  # Limit content length
        title = website_data.get('title', 'N/A')
        description = website_data.get('meta_description', 'N/A')
        url = website_data.get('url', 'N/A')
        
        # Extract UX-relevant data
        navigation = website_data.get('navigation', [])
        forms = website_data.get('forms', [])
        buttons = website_data.get('buttons', [])
        links = website_data.get('links', [])
        images = website_data.get('images', [])
        
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
        Проведи детальный UX анализ веб-сайта:
        
        URL: {url}
        Заголовок: {title}
        Описание: {description}
        {classification_info}
        Контент: {content_preview}
        
        UX данные:
        - Навигация: {len(navigation)} элементов
        - Формы: {len(forms)} форм
        - Кнопки: {len(buttons)} кнопок
        - Ссылки: {len(links)} ссылок
        - Изображения: {len(images)} изображений
        
        Требования к анализу:
        - Максимум {MAX_WORD_COUNT} слов
        - Используй профессиональную UX терминологию
        - Оцени по шкале 1-10
        - Предоставь ровно {MIN_RECOMMENDATIONS} рекомендаций
        
        Верни ответ ТОЛЬКО в формате JSON:
        {{
            "strengths": ["достоинство 1", "достоинство 2", "достоинство 3"],
            "weaknesses": ["слабое место 1", "слабое место 2", "слабое место 3"],
            "recommendations": [
                {{
                    "title": "Название рекомендации",
                    "description": "Подробное описание",
                    "priority": "high/medium/low",
                    "impact": "Ожидаемый эффект"
                }}
            ],
            "overall_score": 7.5,
            "word_count": 450
        }}
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output=f"Структурированный JSON отчет UX анализа (максимум {MAX_WORD_COUNT} слов)"
        )
    
    def _parse_ux_review_result(self, result: str) -> UXReviewResult:
        """
        Parse and validate UX review result.
        
        Args:
            result: Raw result from the agent
            
        Returns:
            Validated UXReviewResult object
            
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
            return UXReviewResult(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Failed to validate UX review result: {e}")
            raise ValueError(f"Validation error: {e}")
    
    def review_ux(self, website_data: Dict[str, Any], classification_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Review website user experience and provide recommendations.
        
        Args:
            website_data: Dictionary containing website content, metadata, etc.
            classification_context: Optional classification results from classifier agent
            
        Returns:
            Dictionary with UX review results
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"UX review attempt {attempt + 1}/{self.max_retries}")
                
                # Create and execute task
                task = self._create_ux_review_task(website_data, classification_context)
                result = task.execute()
                
                # Parse and validate result
                ux_review = self._parse_ux_review_result(result)
                
                logger.info(f"UX review successful: score {ux_review.overall_score}, {len(ux_review.recommendations)} recommendations")
                
                return {
                    "success": True,
                    "ux_review": ux_review.dict(),
                    "attempt": attempt + 1,
                    "timestamp": time.time()
                }
                
            except Exception as e:
                logger.error(f"UX review attempt {attempt + 1} failed: {e}")
                
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
            "error": "All UX review attempts failed",
            "attempts": self.max_retries,
            "timestamp": time.time()
        }
    
    def review_ux_from_url(self, url: str, classification_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Review UX by scraping website first.
        
        Args:
            url: Website URL to review
            classification_context: Optional classification results from classifier agent
            
        Returns:
            Dictionary with UX review results
        """
        try:
            # Import scraping tool
            from multi_agent_system.tools.scraping_tools import create_scraping_tool
            scraping_tool = create_scraping_tool()
            
            logger.info(f"Scraping website for UX review: {url}")
            
            # Scrape website
            if hasattr(scraping_tool, 'func'):
                # CrewAI Tool
                scraped_data = scraping_tool.func(url)
                # Convert string result back to dict (simplified)
                website_data = {
                    "url": url,
                    "content": scraped_data,
                    "title": "",
                    "meta_description": "",
                    "navigation": [],
                    "forms": [],
                    "buttons": [],
                    "links": [],
                    "images": []
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
            
            # Review UX of the scraped data
            return self.review_ux(website_data, classification_context)
            
        except Exception as e:
            logger.error(f"Failed to review UX from URL: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
