"""
Configuration Management for Multi-Agent System

This module handles all configuration settings for the multi-agent system.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Config(BaseSettings):
    """Configuration class for the multi-agent system."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_api_base: Optional[str] = Field(None, env="OPENAI_API_BASE")
    
    # CrewAI Configuration
    crewai_verbose: bool = Field(True, env="CREWAI_VERBOSE")
    crewai_memory: bool = Field(True, env="CREWAI_MEMORY")
    
    # Flask Configuration
    flask_env: str = Field("development", env="FLASK_ENV")
    flask_debug: bool = Field(True, env="FLASK_DEBUG")
    flask_host: str = Field("0.0.0.0", env="FLASK_HOST")
    flask_port: int = Field(5000, env="FLASK_PORT")
    
    # Web Scraping Configuration
    scraping_timeout: int = Field(30, env="SCRAPING_TIMEOUT")
    scraping_user_agent: str = Field(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        env="SCRAPING_USER_AGENT"
    )
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/multi_agent_system.log", env="LOG_FILE")
    
    # Database Configuration
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    
    # Agent Configuration
    max_iterations: int = Field(3, env="MAX_ITERATIONS")
    temperature: float = Field(0.3, env="TEMPERATURE")
    
    # pydantic-settings v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    def __init__(self, **kwargs):
        """Initialize configuration with environment variables."""
        # Load environment variables from nearest .env (searching upwards)
        load_dotenv(find_dotenv())
        super().__init__(**kwargs)
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration dictionary."""
        cfg = {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "temperature": self.temperature
        }
        if self.openai_api_base:
            # Many SDKs expect base_url / base_path name; expose with conventional key
            cfg["base_url"] = self.openai_api_base
        return cfg
    
    def get_crewai_config(self) -> Dict[str, Any]:
        """Get CrewAI configuration dictionary."""
        return {
            "verbose": self.crewai_verbose,
            "memory": self.crewai_memory,
            "max_iter": self.max_iterations
        }
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask configuration dictionary."""
        return {
            "env": self.flask_env,
            "debug": self.flask_debug,
            "host": self.flask_host,
            "port": self.flask_port
        }
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Get web scraping configuration dictionary."""
        return {
            "timeout": self.scraping_timeout,
            "user_agent": self.scraping_user_agent
        }
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present."""
        required_fields = ["openai_api_key"]
        
        for field in required_fields:
            if not getattr(self, field, None):
                raise ValueError(f"Required configuration field '{field}' is missing")
        
        return True


# Global configuration instance
config = Config()
