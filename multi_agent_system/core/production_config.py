"""
Production-ready configuration management for the multi-agent system.

This module provides comprehensive configuration for production deployment
with security, monitoring, caching, and performance optimizations.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from pathlib import Path


class OpenAIConfig(BaseModel):
    """OpenAI API configuration."""
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model to use")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(default=4000, ge=1, le=8000, description="Maximum tokens per request")
    timeout: int = Field(default=60, ge=1, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")


class CrewAIConfig(BaseModel):
    """CrewAI configuration."""
    verbose: bool = Field(default=True, description="Enable verbose logging")
    memory: bool = Field(default=True, description="Enable memory for agents")
    max_iterations: int = Field(default=3, ge=1, le=10, description="Maximum iterations per task")
    max_execution_time: int = Field(default=300, ge=30, description="Maximum execution time in seconds")


class FlaskConfig(BaseModel):
    """Flask application configuration."""
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=5000, ge=1, le=65535, description="Port to bind to")
    debug: bool = Field(default=False, description="Enable debug mode")
    secret_key: str = Field(default="dev-secret-key", description="Flask secret key")
    max_content_length: int = Field(default=16777216, description="Maximum content length (16MB)")
    threaded: bool = Field(default=True, description="Enable threading")
    processes: int = Field(default=1, ge=1, le=4, description="Number of processes")


class ScrapingConfig(BaseModel):
    """Web scraping configuration."""
    timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="User agent string"
    )
    max_content_length: int = Field(default=8000, ge=100, description="Maximum content length")
    connection_pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    connection_pool_maxsize: int = Field(default=20, ge=1, le=200, description="Connection pool max size")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    file: Optional[str] = Field(default=None, description="Log file path")
    max_file_size: int = Field(default=10485760, description="Maximum log file size (10MB)")
    backup_count: int = Field(default=5, ge=1, description="Number of backup files")
    enable_console: bool = Field(default=True, description="Enable console logging")
    enable_file: bool = Field(default=True, description="Enable file logging")


class SecurityConfig(BaseModel):
    """Security configuration."""
    enable_security: bool = Field(default=True, description="Enable security features")
    max_url_length: int = Field(default=2048, description="Maximum URL length")
    max_request_size: int = Field(default=10485760, description="Maximum request size (10MB)")
    allowed_schemes: List[str] = Field(default=["http", "https"], description="Allowed URL schemes")
    blocked_domains: List[str] = Field(default_factory=list, description="Blocked domains")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    max_requests_per_window: int = Field(default=100, description="Max requests per window")
    enable_content_filtering: bool = Field(default=True, description="Enable content filtering")
    enable_xss_protection: bool = Field(default=True, description="Enable XSS protection")
    api_key_rotation_days: int = Field(default=90, ge=1, description="API key rotation period in days")


class CacheConfig(BaseModel):
    """Caching configuration."""
    enable_cache: bool = Field(default=True, description="Enable caching")
    cache_type: str = Field(default="memory", description="Cache type: memory, redis, file")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    max_cache_size: int = Field(default=1000, ge=1, description="Maximum cache entries")
    redis_url: Optional[str] = Field(default=None, description="Redis URL for cache")
    cache_directory: str = Field(default="./cache", description="Cache directory for file cache")


class MonitoringConfig(BaseModel):
    """Monitoring and health check configuration."""
    enable_health_checks: bool = Field(default=True, description="Enable health checks")
    health_check_interval: int = Field(default=30, ge=5, description="Health check interval in seconds")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=9090, ge=1, le=65535, description="Metrics port")
    enable_profiling: bool = Field(default=False, description="Enable performance profiling")
    max_response_time: int = Field(default=30, ge=1, description="Maximum response time in seconds")


class DatabaseConfig(BaseModel):
    """Database configuration."""
    enable_database: bool = Field(default=False, description="Enable database storage")
    database_url: Optional[str] = Field(default=None, description="Database URL")
    database_type: str = Field(default="sqlite", description="Database type")
    connection_pool_size: int = Field(default=5, ge=1, le=20, description="Connection pool size")
    max_overflow: int = Field(default=10, ge=0, le=50, description="Maximum overflow connections")


class ProductionConfig(BaseSettings):
    """Main configuration class for production deployment."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT", description="Environment: development, staging, production")
    app_name: str = Field(default="Multi-Agent Website Analysis", env="APP_NAME", description="Application name")
    version: str = Field(default="2.0.0", env="VERSION", description="Application version")
    
    # OpenAI configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL", description="OpenAI model")
    temperature: float = Field(default=0.1, env="TEMPERATURE", description="Model temperature")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS", description="Maximum tokens")
    openai_timeout: int = Field(default=60, env="OPENAI_TIMEOUT", description="OpenAI timeout")
    openai_max_retries: int = Field(default=3, env="OPENAI_MAX_RETRIES", description="OpenAI max retries")
    
    # CrewAI configuration
    crewai_verbose: bool = Field(default=True, env="CREWAI_VERBOSE", description="CrewAI verbose mode")
    crewai_memory: bool = Field(default=True, env="CREWAI_MEMORY", description="CrewAI memory")
    max_iterations: int = Field(default=3, env="MAX_ITERATIONS", description="Max iterations")
    max_execution_time: int = Field(default=300, env="MAX_EXECUTION_TIME", description="Max execution time")
    
    # Flask configuration
    flask_host: str = Field(default="0.0.0.0", env="FLASK_HOST", description="Flask host")
    flask_port: int = Field(default=5000, env="FLASK_PORT", description="Flask port")
    flask_debug: bool = Field(default=False, env="FLASK_DEBUG", description="Flask debug mode")
    flask_secret_key: str = Field(default="dev-secret-key", env="FLASK_SECRET_KEY", description="Flask secret key")
    flask_max_content_length: int = Field(default=16777216, env="FLASK_MAX_CONTENT_LENGTH", description="Flask max content length")
    flask_threaded: bool = Field(default=True, env="FLASK_THREADED", description="Flask threading")
    flask_processes: int = Field(default=1, env="FLASK_PROCESSES", description="Flask processes")
    
    # Scraping configuration
    scraping_timeout: int = Field(default=30, env="SCRAPING_TIMEOUT", description="Scraping timeout")
    scraping_max_retries: int = Field(default=3, env="SCRAPING_MAX_RETRIES", description="Scraping max retries")
    scraping_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        env="SCRAPING_USER_AGENT",
        description="Scraping user agent"
    )
    max_content_length: int = Field(default=8000, env="MAX_CONTENT_LENGTH", description="Max content length")
    connection_pool_size: int = Field(default=10, env="CONNECTION_POOL_SIZE", description="Connection pool size")
    connection_pool_maxsize: int = Field(default=20, env="CONNECTION_POOL_MAXSIZE", description="Connection pool max size")
    
    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Log format"
    )
    log_file: Optional[str] = Field(default=None, env="LOG_FILE", description="Log file path")
    log_max_file_size: int = Field(default=10485760, env="LOG_MAX_FILE_SIZE", description="Log max file size")
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT", description="Log backup count")
    log_enable_console: bool = Field(default=True, env="LOG_ENABLE_CONSOLE", description="Enable console logging")
    log_enable_file: bool = Field(default=True, env="LOG_ENABLE_FILE", description="Enable file logging")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE", description="Rate limit per minute")
    
    # Security configuration
    security_enable: bool = Field(default=True, env="SECURITY_ENABLE", description="Enable security features")
    security_max_url_length: int = Field(default=2048, env="SECURITY_MAX_URL_LENGTH", description="Max URL length")
    security_max_request_size: int = Field(default=10485760, env="SECURITY_MAX_REQUEST_SIZE", description="Max request size")
    security_allowed_schemes: str = Field(default="http,https", env="SECURITY_ALLOWED_SCHEMES", description="Allowed schemes")
    security_blocked_domains: str = Field(default="", env="SECURITY_BLOCKED_DOMAINS", description="Blocked domains")
    security_rate_limit_window: int = Field(default=60, env="SECURITY_RATE_LIMIT_WINDOW", description="Rate limit window")
    security_max_requests_per_window: int = Field(default=100, env="SECURITY_MAX_REQUESTS_PER_WINDOW", description="Max requests per window")
    security_enable_content_filtering: bool = Field(default=True, env="SECURITY_ENABLE_CONTENT_FILTERING", description="Enable content filtering")
    security_enable_xss_protection: bool = Field(default=True, env="SECURITY_ENABLE_XSS_PROTECTION", description="Enable XSS protection")
    security_api_key_rotation_days: int = Field(default=90, env="SECURITY_API_KEY_ROTATION_DAYS", description="API key rotation days")
    
    # Cache configuration
    cache_enable: bool = Field(default=True, env="CACHE_ENABLE", description="Enable caching")
    cache_type: str = Field(default="memory", env="CACHE_TYPE", description="Cache type")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL", description="Cache TTL")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE", description="Max cache size")
    cache_redis_url: Optional[str] = Field(default=None, env="CACHE_REDIS_URL", description="Redis URL")
    cache_directory: str = Field(default="./cache", env="CACHE_DIRECTORY", description="Cache directory")
    
    # Monitoring configuration
    monitoring_enable_health_checks: bool = Field(default=True, env="MONITORING_ENABLE_HEALTH_CHECKS", description="Enable health checks")
    monitoring_health_check_interval: int = Field(default=30, env="MONITORING_HEALTH_CHECK_INTERVAL", description="Health check interval")
    monitoring_enable_metrics: bool = Field(default=True, env="MONITORING_ENABLE_METRICS", description="Enable metrics")
    monitoring_metrics_port: int = Field(default=9090, env="MONITORING_METRICS_PORT", description="Metrics port")
    monitoring_enable_profiling: bool = Field(default=False, env="MONITORING_ENABLE_PROFILING", description="Enable profiling")
    monitoring_max_response_time: int = Field(default=30, env="MONITORING_MAX_RESPONSE_TIME", description="Max response time")
    
    # Database configuration
    database_enable: bool = Field(default=False, env="DATABASE_ENABLE", description="Enable database")
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL", description="Database URL")
    database_type: str = Field(default="sqlite", env="DATABASE_TYPE", description="Database type")
    database_connection_pool_size: int = Field(default=5, env="DATABASE_CONNECTION_POOL_SIZE", description="Database connection pool size")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW", description="Database max overflow")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'Environment must be one of: {allowed}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of: {allowed}')
        return v.upper()
    
    @validator('cache_type')
    def validate_cache_type(cls, v):
        allowed = ['memory', 'redis', 'file']
        if v not in allowed:
            raise ValueError(f'Cache type must be one of: {allowed}')
        return v
    
    @validator('database_type')
    def validate_database_type(cls, v):
        allowed = ['sqlite', 'postgresql', 'mysql']
        if v not in allowed:
            raise ValueError(f'Database type must be one of: {allowed}')
        return v
    
    def validate_config(self) -> None:
        """Validate configuration values."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        
        if self.max_tokens < 1 or self.max_tokens > 8000:
            raise ValueError("Max tokens must be between 1 and 8000")
        
        if self.max_iterations < 1 or self.max_iterations > 10:
            raise ValueError("Max iterations must be between 1 and 10")
        
        if self.environment == "production":
            if self.flask_debug:
                raise ValueError("Debug mode must be disabled in production")
            
            if self.flask_secret_key == "dev-secret-key":
                raise ValueError("Default secret key must be changed in production")
        
        # Validate cache configuration
        if self.cache_enable and self.cache_type == "redis" and not self.cache_redis_url:
            raise ValueError("Redis URL is required when using Redis cache")
        
        # Validate database configuration
        if self.database_enable and not self.database_url:
            raise ValueError("Database URL is required when database is enabled")
    
    def get_openai_config(self) -> OpenAIConfig:
        """Get OpenAI configuration."""
        return OpenAIConfig(
            api_key=self.openai_api_key,
            model=self.openai_model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.openai_timeout,
            max_retries=self.openai_max_retries
        )
    
    def get_crewai_config(self) -> CrewAIConfig:
        """Get CrewAI configuration."""
        return CrewAIConfig(
            verbose=self.crewai_verbose,
            memory=self.crewai_memory,
            max_iterations=self.max_iterations,
            max_execution_time=self.max_execution_time
        )
    
    def get_flask_config(self) -> FlaskConfig:
        """Get Flask configuration."""
        return FlaskConfig(
            host=self.flask_host,
            port=self.flask_port,
            debug=self.flask_debug,
            secret_key=self.flask_secret_key,
            max_content_length=self.flask_max_content_length,
            threaded=self.flask_threaded,
            processes=self.flask_processes
        )
    
    def get_scraping_config(self) -> ScrapingConfig:
        """Get scraping configuration."""
        return ScrapingConfig(
            timeout=self.scraping_timeout,
            max_retries=self.scraping_max_retries,
            user_agent=self.scraping_user_agent,
            max_content_length=self.max_content_length,
            connection_pool_size=self.connection_pool_size,
            connection_pool_maxsize=self.connection_pool_maxsize
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return LoggingConfig(
            level=self.log_level,
            format=self.log_format,
            file=self.log_file,
            max_file_size=self.log_max_file_size,
            backup_count=self.log_backup_count,
            enable_console=self.log_enable_console,
            enable_file=self.log_enable_file
        )
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return SecurityConfig(
            enable_security=self.security_enable,
            max_url_length=self.security_max_url_length,
            max_request_size=self.security_max_request_size,
            allowed_schemes=self.security_allowed_schemes.split(','),
            blocked_domains=self.security_blocked_domains.split(',') if self.security_blocked_domains else [],
            rate_limit_window=self.security_rate_limit_window,
            max_requests_per_window=self.security_max_requests_per_window,
            enable_content_filtering=self.security_enable_content_filtering,
            enable_xss_protection=self.security_enable_xss_protection,
            api_key_rotation_days=self.security_api_key_rotation_days
        )
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        return CacheConfig(
            enable_cache=self.cache_enable,
            cache_type=self.cache_type,
            cache_ttl=self.cache_ttl,
            max_cache_size=self.cache_max_size,
            redis_url=self.cache_redis_url,
            cache_directory=self.cache_directory
        )
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        return MonitoringConfig(
            enable_health_checks=self.monitoring_enable_health_checks,
            health_check_interval=self.monitoring_health_check_interval,
            enable_metrics=self.monitoring_enable_metrics,
            metrics_port=self.monitoring_metrics_port,
            enable_profiling=self.monitoring_enable_profiling,
            max_response_time=self.monitoring_max_response_time
        )
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return DatabaseConfig(
            enable_database=self.database_enable,
            database_url=self.database_url,
            database_type=self.database_type,
            connection_pool_size=self.database_connection_pool_size,
            max_overflow=self.database_max_overflow
        )
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def get_app_info(self) -> Dict[str, Any]:
        """Get application information."""
        return {
            'name': self.app_name,
            'version': self.version,
            'environment': self.environment,
            'debug': self.flask_debug,
            'host': self.flask_host,
            'port': self.flask_port
        }


# Global configuration instance
production_config = ProductionConfig()
