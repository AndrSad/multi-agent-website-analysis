"""
Design Advisor Agent for Landing Page Design Recommendations

This agent provides specific design recommendations for landing pages including:
- Visual design assessment
- Brand consistency evaluation
- Color scheme analysis
- Typography recommendations
- Layout optimization suggestions
- Actionable design improvements
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

# Configure logging
logger = logging.getLogger(__name__)

# Constants
REQUIRED_RECOMMENDATIONS = 5
LANDING_PAGE_TYPE = "landing_page"


class DesignRecommendation(BaseModel):
    """Pydantic model for design recommendations."""
    title: str = Field(..., description="Title of the design recommendation")
    description: str = Field(..., description="Detailed description of the recommendation")
    category: str = Field(..., description="Design category: visual, layout, typography, color, interaction")
    priority: str = Field(..., description="Priority level: high, medium, low")
    implementation_difficulty: str = Field(..., description="Implementation difficulty: easy, medium, hard")
    
    @validator('category')
    def category_must_be_valid(cls, v):
        valid_categories = ['visual', 'layout', 'typography', 'color', 'interaction']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v.lower()
    
    @validator('priority')
    def priority_must_be_valid(cls, v):
        if v.lower() not in ['high', 'medium', 'low']:
            raise ValueError('Priority must be high, medium, or low')
        return v.lower()
    
    @validator('implementation_difficulty')
    def difficulty_must_be_valid(cls, v):
        if v.lower() not in ['easy', 'medium', 'hard']:
            raise ValueError('Implementation difficulty must be easy, medium, or hard')
        return v.lower()


class DesignAdviceResult(BaseModel):
    """Pydantic model for design advice results validation."""
    recommendations: List[DesignRecommendation] = Field(..., description="List of design recommendations")
    overall_design_score: float = Field(ge=1.0, le=10.0, description="Overall design score from 1.0 to 10.0")
    is_landing_page: bool = Field(..., description="Whether the website is identified as a landing page")
    
    @validator('recommendations')
    def recommendations_count_must_be_valid(cls, v):
        if len(v) != REQUIRED_RECOMMENDATIONS:
            raise ValueError(f'Must have exactly {REQUIRED_RECOMMENDATIONS} recommendations')
        return v


class DesignAdvisorAgent:
    """Agent responsible for providing landing page design recommendations."""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview", max_retries: int = 3):
        """
        Initialize the Design Advisor Agent.
        
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
            temperature=0.4 if 0.4 is not None else openai_cfg["temperature"],
            api_key=openai_cfg["api_key"],
            base_url=openai_cfg.get("base_url")
        )
        
        # Initialize CrewAI Agent
        self.agent = Agent(
            role="UI/Design Consultant",
            goal="Provide 5 practical design improvement suggestions for landing pages",
            backstory="""Ти консультант по UI/UX дизайну. На основе анализа контента предоставь 5 конкретных советов по улучшению визуального оформления и структуры лендинга. Сфокусируйся на практических, реализуемых рекомендациях. Верни ответ в виде списка.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3
        )
    
    def get_agent(self) -> Agent:
        """Return the configured CrewAI agent."""
        return self.agent
    
    def _is_landing_page(self, classification_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if the website is identified as a landing page.
        
        Args:
            classification_context: Optional classification results from classifier agent
            
        Returns:
            True if the website is a landing page, False otherwise
        """
        if not classification_context or not classification_context.get('success'):
            return False
        
        classification = classification_context.get('classification', {})
        website_type = classification.get('type', '').lower()
        
        return website_type == LANDING_PAGE_TYPE
    
    def _create_design_advice_task(self, website_data: Dict[str, Any], classification_context: Optional[Dict[str, Any]] = None) -> Task:
        """
        Create a CrewAI task for design advice.
        
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
        
        # Extract design-relevant data
        colors = website_data.get('colors', [])
        fonts = website_data.get('fonts', [])
        images = website_data.get('images', [])
        layout_elements = website_data.get('layout_elements', [])
        buttons = website_data.get('buttons', [])
        forms = website_data.get('forms', [])
        
        # Build context from classification if available
        classification_info = ""
        is_landing_page = False
        if classification_context and classification_context.get('success'):
            classification = classification_context.get('classification', {})
            classification_info = f"""
        Контекст классификации:
        - Тип сайта: {classification.get('type', 'неизвестно')}
        - Индустрия: {classification.get('industry', 'неизвестно')}
        - Целевая аудитория: {classification.get('target_audience', 'неизвестно')}
        - Бизнес-модель: {classification.get('business_model', 'неизвестно')}
        """
            is_landing_page = self._is_landing_page(classification_context)
        
        task_description = f"""
        Проанализируй дизайн лендинга и предоставь 5 конкретных рекомендаций:
        
        URL: {url}
        Заголовок: {title}
        Описание: {description}
        {classification_info}
        Контент: {content_preview}
        
        Дизайн данные:
        - Цвета: {len(colors)} цветов
        - Шрифты: {len(fonts)} шрифтов
        - Изображения: {len(images)} изображений
        - Элементы макета: {len(layout_elements)} элементов
        - Кнопки: {len(buttons)} кнопок
        - Формы: {len(forms)} форм
        
        Требования к рекомендациям:
        - Ровно {REQUIRED_RECOMMENDATIONS} конкретных рекомендаций
        - Фокус на практических, реализуемых советах
        - Категории: visual, layout, typography, color, interaction
        - Приоритеты: high, medium, low
        - Сложность реализации: easy, medium, hard
        
        Верни ответ ТОЛЬКО в формате JSON:
        {{
            "recommendations": [
                {{
                    "title": "Название рекомендации",
                    "description": "Подробное описание с конкретными шагами",
                    "category": "visual/layout/typography/color/interaction",
                    "priority": "high/medium/low",
                    "implementation_difficulty": "easy/medium/hard"
                }}
            ],
            "overall_design_score": 7.5,
            "is_landing_page": {str(is_landing_page).lower()}
        }}
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output=f"Структурированный JSON с {REQUIRED_RECOMMENDATIONS} конкретными рекомендациями по дизайну"
        )
    
    def _parse_design_advice_result(self, result: str) -> DesignAdviceResult:
        """
        Parse and validate design advice result.
        
        Args:
            result: Raw result from the agent
            
        Returns:
            Validated DesignAdviceResult object
            
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
            return DesignAdviceResult(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Failed to validate design advice result: {e}")
            raise ValueError(f"Validation error: {e}")
    
    def advise_design(self, website_data: Dict[str, Any], classification_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Provide design recommendations for landing page improvement.
        
        Args:
            website_data: Dictionary containing website content, metadata, etc.
            classification_context: Optional classification results from classifier agent
            
        Returns:
            Dictionary with design advice results
        """
        # Check if this is a landing page
        if not self._is_landing_page(classification_context):
            logger.info("Website is not identified as a landing page, skipping design advice")
            return {
                "success": False,
                "error": "Design advice is only available for landing pages",
                "is_landing_page": False,
                "timestamp": time.time()
            }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Design advice attempt {attempt + 1}/{self.max_retries}")
                
                # Create and execute task
                task = self._create_design_advice_task(website_data, classification_context)
                result = task.execute()
                
                # Parse and validate result
                design_advice = self._parse_design_advice_result(result)
                
                logger.info(f"Design advice successful: {len(design_advice.recommendations)} recommendations, score {design_advice.overall_design_score}")
                
                return {
                    "success": True,
                    "design_advice": design_advice.dict(),
                    "attempt": attempt + 1,
                    "timestamp": time.time()
                }
                
            except Exception as e:
                logger.error(f"Design advice attempt {attempt + 1} failed: {e}")
                
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
            "error": "All design advice attempts failed",
            "attempts": self.max_retries,
            "timestamp": time.time()
        }
    
    def advise_design_from_url(self, url: str, classification_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Provide design advice by scraping website first.
        
        Args:
            url: Website URL to analyze
            classification_context: Optional classification results from classifier agent
            
        Returns:
            Dictionary with design advice results
        """
        try:
            # Import scraping tool
            from multi_agent_system.tools.scraping_tools import create_scraping_tool
            scraping_tool = create_scraping_tool()
            
            logger.info(f"Scraping website for design advice: {url}")
            
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
                    "colors": [],
                    "fonts": [],
                    "images": [],
                    "layout_elements": [],
                    "buttons": [],
                    "forms": []
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
            
            # Provide design advice for the scraped data
            return self.advise_design(website_data, classification_context)
            
        except Exception as e:
            logger.error(f"Failed to provide design advice from URL: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
