"""
Production-ready logging configuration for the multi-agent system.

This module provides comprehensive logging setup with file rotation,
structured logging, and performance monitoring.
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json
import traceback


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records."""
    
    def filter(self, record):
        """Add performance metrics to log record."""
        # Add request timing if available
        if hasattr(record, 'request_time'):
            record.response_time_ms = record.request_time * 1000
        
        # Add memory usage if available
        try:
            import psutil
            process = psutil.Process()
            record.memory_mb = process.memory_info().rss / 1024 / 1024
            record.cpu_percent = process.cpu_percent()
        except ImportError:
            pass
        
        return True


class SecurityFilter(logging.Filter):
    """Filter to sanitize sensitive information from logs."""
    
    SENSITIVE_FIELDS = [
        'password', 'token', 'key', 'secret', 'api_key', 'auth',
        'authorization', 'cookie', 'session', 'credential'
    ]
    
    def filter(self, record):
        """Sanitize sensitive information from log record."""
        # Sanitize message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._sanitize_string(record.msg)
        
        # Sanitize args
        if hasattr(record, 'args') and record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    sanitized_args.append(self._sanitize_string(arg))
                elif isinstance(arg, dict):
                    sanitized_args.append(self._sanitize_dict(arg))
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)
        
        return True
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize sensitive information in string."""
        for field in self.SENSITIVE_FIELDS:
            # Replace patterns like "password=secret" with "password=***"
            import re
            pattern = rf'({field}[=:]\s*)([^\s&]+)'
            text = re.sub(pattern, r'\1***', text, flags=re.IGNORECASE)
        return text
    
    def _sanitize_dict(self, data: dict) -> dict:
        """Sanitize sensitive information in dictionary."""
        sanitized = {}
        for key, value in data.items():
            if any(field in key.lower() for field in self.SENSITIVE_FIELDS):
                sanitized[key] = '***'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            else:
                sanitized[key] = value
        return sanitized


class LoggingManager:
    """Production-ready logging manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.loggers = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create logs directory if it doesn't exist
        if self.config.get('file'):
            log_dir = Path(self.config['file']).parent
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config['level']))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if self.config.get('enable_console', True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.config['level']))
            
            if self.config.get('structured', False):
                console_formatter = StructuredFormatter()
            else:
                console_formatter = logging.Formatter(self.config['format'])
            
            console_handler.setFormatter(console_formatter)
            console_handler.addFilter(PerformanceFilter())
            console_handler.addFilter(SecurityFilter())
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.config.get('enable_file', True) and self.config.get('file'):
            file_handler = logging.handlers.RotatingFileHandler(
                self.config['file'],
                maxBytes=self.config.get('max_file_size', 10 * 1024 * 1024),  # 10MB
                backupCount=self.config.get('backup_count', 5)
            )
            file_handler.setLevel(getattr(logging, self.config['level']))
            
            if self.config.get('structured', False):
                file_formatter = StructuredFormatter()
            else:
                file_formatter = logging.Formatter(self.config['format'])
            
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(PerformanceFilter())
            file_handler.addFilter(SecurityFilter())
            root_logger.addHandler(file_handler)
        
        # Error file handler
        if self.config.get('enable_file', True) and self.config.get('file'):
            error_file = str(Path(self.config['file']).with_suffix('.error.log'))
            error_handler = logging.handlers.RotatingFileHandler(
                error_file,
                maxBytes=self.config.get('max_file_size', 10 * 1024 * 1024),
                backupCount=self.config.get('backup_count', 5)
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            error_handler.addFilter(PerformanceFilter())
            error_handler.addFilter(SecurityFilter())
            root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger instance with performance tracking."""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            
            # Add performance tracking
            logger = self._add_performance_tracking(logger)
            
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def _add_performance_tracking(self, logger: logging.Logger):
        """Add performance tracking to logger."""
        original_log = logger._log
        
        def log_with_performance(level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
            # Add performance metrics
            if extra is None:
                extra = {}
            
            # Add request ID if available
            import threading
            thread_local = threading.local()
            if hasattr(thread_local, 'request_id'):
                extra['request_id'] = thread_local.request_id
            
            # Add timing information
            if hasattr(thread_local, 'request_start_time'):
                extra['request_time'] = time.time() - thread_local.request_start_time
            
            return original_log(level, msg, args, exc_info, extra, stack_info, stacklevel)
        
        logger._log = log_with_performance
        return logger
    
    def set_request_context(self, request_id: str, start_time: float):
        """Set request context for logging."""
        import threading
        thread_local = threading.local()
        thread_local.request_id = request_id
        thread_local.request_start_time = start_time
    
    def clear_request_context(self):
        """Clear request context."""
        import threading
        thread_local = threading.local()
        if hasattr(thread_local, 'request_id'):
            delattr(thread_local, 'request_id')
        if hasattr(thread_local, 'request_start_time'):
            delattr(thread_local, 'request_start_time')


class MetricsLogger:
    """Logger for application metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, url: str, status_code: int, 
                   response_time: float, user_agent: str = None):
        """Log HTTP request metrics."""
        self.logger.info(
            "HTTP Request",
            extra={
                'event_type': 'http_request',
                'method': method,
                'url': url,
                'status_code': status_code,
                'response_time_ms': response_time * 1000,
                'user_agent': user_agent
            }
        )
    
    def log_analysis(self, url: str, analysis_type: str, duration: float, 
                    success: bool, agents_used: list, cache_hit: bool = False):
        """Log analysis metrics."""
        self.logger.info(
            "Analysis Completed",
            extra={
                'event_type': 'analysis',
                'url': url,
                'analysis_type': analysis_type,
                'duration_ms': duration * 1000,
                'success': success,
                'agents_used': agents_used,
                'cache_hit': cache_hit
            }
        )
    
    def log_error(self, error_type: str, error_message: str, 
                 context: Dict[str, Any] = None):
        """Log error metrics."""
        extra = {
            'event_type': 'error',
            'error_type': error_type,
            'error_message': error_message
        }
        if context:
            extra.update(context)
        
        self.logger.error("Application Error", extra=extra)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events."""
        self.logger.warning(
            "Security Event",
            extra={
                'event_type': 'security',
                'security_event_type': event_type,
                **details
            }
        )
    
    def log_performance(self, operation: str, duration: float, 
                       details: Dict[str, Any] = None):
        """Log performance metrics."""
        extra = {
            'event_type': 'performance',
            'operation': operation,
            'duration_ms': duration * 1000
        }
        if details:
            extra.update(details)
        
        self.logger.info("Performance Metric", extra=extra)


# Global logging manager instance
_logging_manager = None
_metrics_logger = None

def setup_logging(config: Dict[str, Any]) -> LoggingManager:
    """Setup global logging configuration."""
    global _logging_manager
    _logging_manager = LoggingManager(config)
    return _logging_manager

def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    global _logging_manager
    if _logging_manager is None:
        # Default configuration
        default_config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'enable_console': True,
            'enable_file': False
        }
        _logging_manager = LoggingManager(default_config)
    
    return _logging_manager.get_logger(name)

def get_metrics_logger() -> MetricsLogger:
    """Get metrics logger instance."""
    global _metrics_logger
    if _metrics_logger is None:
        logger = get_logger('metrics')
        _metrics_logger = MetricsLogger(logger)
    return _metrics_logger

def set_request_context(request_id: str, start_time: float):
    """Set request context for logging."""
    global _logging_manager
    if _logging_manager:
        _logging_manager.set_request_context(request_id, start_time)

def clear_request_context():
    """Clear request context."""
    global _logging_manager
    if _logging_manager:
        _logging_manager.clear_request_context()
