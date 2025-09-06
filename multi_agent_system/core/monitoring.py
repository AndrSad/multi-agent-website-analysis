"""
Monitoring and health check system for production deployment.

This module provides comprehensive monitoring, health checks, metrics collection,
and graceful shutdown capabilities.
"""

import time
import threading
import signal
import sys
import psutil
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
import json


class HealthStatus(Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    disk_usage_percent: float = 0.0
    network_io: Dict[str, int] = field(default_factory=dict)
    process_count: int = 0
    load_average: List[float] = field(default_factory=list)


@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    active_connections: int = 0
    queue_size: int = 0


class HealthChecker:
    """Health check manager."""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.results: Dict[str, HealthCheck] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_check(self, name: str, check_func: Callable[[], HealthCheck]):
        """Register a health check function."""
        self.checks[name] = check_func
        self.logger.info(f"Registered health check: {name}")
    
    def run_check(self, name: str) -> HealthCheck:
        """Run a specific health check."""
        if name not in self.checks:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{name}' not found",
                response_time_ms=0.0
            )
        
        start_time = time.time()
        try:
            result = self.checks[name]()
            result.response_time_ms = (time.time() - start_time) * 1000
            self.results[name] = result
            return result
        except Exception as e:
            self.logger.error(f"Health check '{name}' failed: {str(e)}")
            result = HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000
            )
            self.results[name] = result
            return result
    
    def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks."""
        results = {}
        for name in self.checks:
            results[name] = self.run_check(name)
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        if not self.results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in self.results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN


class MetricsCollector:
    """System and application metrics collector."""
    
    def __init__(self):
        self.system_metrics: List[SystemMetrics] = []
        self.application_metrics: List[ApplicationMetrics] = []
        self.max_metrics_history = 1000
        self.logger = logging.getLogger(__name__)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network_io = psutil.net_io_counters()._asdict()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Load average (Unix-like systems)
            try:
                load_average = list(psutil.getloadavg())
            except AttributeError:
                load_average = []
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                process_count=process_count,
                load_average=load_average
            )
            
            self.system_metrics.append(metrics)
            if len(self.system_metrics) > self.max_metrics_history:
                self.system_metrics.pop(0)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")
            return SystemMetrics()
    
    def collect_application_metrics(self, **kwargs) -> ApplicationMetrics:
        """Collect application-specific metrics."""
        metrics = ApplicationMetrics(**kwargs)
        self.application_metrics.append(metrics)
        
        if len(self.application_metrics) > self.max_metrics_history:
            self.application_metrics.pop(0)
        
        return metrics
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for the last hour."""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Filter recent metrics
        recent_system = [m for m in self.system_metrics if m.timestamp > one_hour_ago]
        recent_app = [m for m in self.application_metrics if m.timestamp > one_hour_ago]
        
        summary = {
            'timestamp': now.isoformat(),
            'system': {
                'avg_cpu_percent': sum(m.cpu_percent for m in recent_system) / len(recent_system) if recent_system else 0,
                'avg_memory_percent': sum(m.memory_percent for m in recent_system) / len(recent_system) if recent_system else 0,
                'max_memory_used_mb': max(m.memory_used_mb for m in recent_system) if recent_system else 0,
                'avg_disk_usage_percent': sum(m.disk_usage_percent for m in recent_system) / len(recent_system) if recent_system else 0,
            },
            'application': {
                'total_requests': sum(m.total_requests for m in recent_app),
                'successful_requests': sum(m.successful_requests for m in recent_app),
                'failed_requests': sum(m.failed_requests for m in recent_app),
                'avg_response_time_ms': sum(m.average_response_time_ms for m in recent_app) / len(recent_app) if recent_app else 0,
                'cache_hit_rate': self._calculate_cache_hit_rate(recent_app),
            }
        }
        
        return summary
    
    def _calculate_cache_hit_rate(self, metrics: List[ApplicationMetrics]) -> float:
        """Calculate cache hit rate."""
        total_hits = sum(m.cache_hits for m in metrics)
        total_misses = sum(m.cache_misses for m in metrics)
        total_requests = total_hits + total_misses
        
        return (total_hits / total_requests * 100) if total_requests > 0 else 0.0


class GracefulShutdown:
    """Graceful shutdown manager."""
    
    def __init__(self):
        self.shutdown_handlers: List[Callable] = []
        self.is_shutting_down = False
        self.shutdown_timeout = 30  # seconds
        self.logger = logging.getLogger(__name__)
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown()
    
    def register_handler(self, handler: Callable):
        """Register a shutdown handler."""
        self.shutdown_handlers.append(handler)
        self.logger.info(f"Registered shutdown handler: {handler.__name__}")
    
    def shutdown(self):
        """Execute graceful shutdown."""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        self.logger.info("Starting graceful shutdown...")
        
        # Execute shutdown handlers
        for handler in self.shutdown_handlers:
            try:
                self.logger.info(f"Executing shutdown handler: {handler.__name__}")
                handler()
            except Exception as e:
                self.logger.error(f"Shutdown handler {handler.__name__} failed: {str(e)}")
        
        self.logger.info("Graceful shutdown completed")
        sys.exit(0)


class MonitoringManager:
    """Main monitoring manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        self.graceful_shutdown = GracefulShutdown()
        self.logger = logging.getLogger(__name__)
        self.monitoring_thread = None
        self.is_running = False
        
        # Register default health checks
        self._register_default_health_checks()
        
        # Register shutdown handlers
        self.graceful_shutdown.register_handler(self.stop_monitoring)
    
    def _register_default_health_checks(self):
        """Register default health checks."""
        # System health check
        def system_health():
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                    return HealthCheck(
                        name="system",
                        status=HealthStatus.DEGRADED,
                        message=f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%, Disk {disk_percent}%",
                        response_time_ms=0.0,
                        details={
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory_percent,
                            'disk_percent': disk_percent
                        }
                    )
                else:
                    return HealthCheck(
                        name="system",
                        status=HealthStatus.HEALTHY,
                        message="System resources are normal",
                        response_time_ms=0.0,
                        details={
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory_percent,
                            'disk_percent': disk_percent
                        }
                    )
            except Exception as e:
                return HealthCheck(
                    name="system",
                    status=HealthStatus.UNHEALTHY,
                    message=f"System health check failed: {str(e)}",
                    response_time_ms=0.0
                )
        
        self.health_checker.register_check("system", system_health)
        
        # Application health check
        def application_health():
            try:
                # Check if application is responsive
                # This is a simple check - in real implementation, you might
                # check database connections, external services, etc.
                return HealthCheck(
                    name="application",
                    status=HealthStatus.HEALTHY,
                    message="Application is responsive",
                    response_time_ms=0.0
                )
            except Exception as e:
                return HealthCheck(
                    name="application",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Application health check failed: {str(e)}",
                    response_time_ms=0.0
                )
        
        self.health_checker.register_check("application", application_health)
    
    def start_monitoring(self):
        """Start monitoring in background thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        interval = self.config.get('health_check_interval', 30)
        
        while self.is_running:
            try:
                # Collect system metrics
                self.metrics_collector.collect_system_metrics()
                
                # Run health checks
                if self.config.get('enable_health_checks', True):
                    self.health_checker.run_all_checks()
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(interval)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        overall_status = self.health_checker.get_overall_status()
        checks = self.health_checker.results
        
        return {
            'status': overall_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                name: {
                    'status': check.status.value,
                    'message': check.message,
                    'response_time_ms': check.response_time_ms,
                    'timestamp': check.timestamp.isoformat(),
                    'details': check.details
                }
                for name, check in checks.items()
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics_collector.get_metrics_summary()
    
    def record_request(self, method: str, url: str, status_code: int, 
                      response_time: float, user_agent: str = None):
        """Record HTTP request metrics."""
        # This would be called from the API layer
        pass
    
    def record_analysis(self, url: str, analysis_type: str, duration: float, 
                       success: bool, agents_used: list, cache_hit: bool = False):
        """Record analysis metrics."""
        # This would be called from the analysis layer
        pass


# Global monitoring manager instance
_monitoring_manager = None

def get_monitoring_manager(config: Dict[str, Any] = None) -> MonitoringManager:
    """Get global monitoring manager instance."""
    global _monitoring_manager
    if _monitoring_manager is None:
        if config is None:
            config = {
                'enable_health_checks': True,
                'health_check_interval': 30,
                'enable_metrics': True
            }
        _monitoring_manager = MonitoringManager(config)
    return _monitoring_manager

def start_monitoring(config: Dict[str, Any] = None):
    """Start global monitoring."""
    manager = get_monitoring_manager(config)
    manager.start_monitoring()

def stop_monitoring():
    """Stop global monitoring."""
    global _monitoring_manager
    if _monitoring_manager:
        _monitoring_manager.stop_monitoring()
