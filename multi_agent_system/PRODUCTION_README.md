# 🚀 Multi-Agent Website Analysis System - Production Deployment Guide

A production-ready multi-agent system for comprehensive website analysis using AI agents for classification, summarization, UX analysis, and design recommendations.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Security](#security)
- [Monitoring](#monitoring)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

## ✨ Features

### 🔒 Security
- **URL Validation & Sanitization**: Comprehensive URL validation with malicious pattern detection
- **XSS Protection**: Content filtering and sanitization to prevent cross-site scripting
- **Input Validation**: Pydantic-based request/response validation
- **Rate Limiting**: Configurable rate limiting with sliding window
- **API Key Authentication**: Secure API key-based authentication
- **Content Filtering**: Automatic filtering of malicious content

### 📊 Monitoring & Observability
- **Health Checks**: Comprehensive system health monitoring
- **Metrics Collection**: System and application metrics with Prometheus integration
- **Structured Logging**: JSON-structured logging with log rotation
- **Performance Monitoring**: Request timing and resource usage tracking
- **Graceful Shutdown**: Proper cleanup and resource management

### ⚡ Performance
- **Multiple Cache Backends**: Memory, Redis, and file-based caching
- **Connection Pooling**: HTTP connection pooling for better performance
- **Async Processing**: Asynchronous agent execution
- **Optimized Prompts**: Token-optimized prompts for cost efficiency
- **Load Balancing**: Nginx-based load balancing and reverse proxy

### 🔧 Production Features
- **Docker Support**: Complete Docker and Docker Compose setup
- **Environment Configuration**: Comprehensive environment-based configuration
- **Database Support**: PostgreSQL integration with connection pooling
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Error Handling**: Robust error handling and retry mechanisms

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Load Balancer │    │   API Gateway   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Flask API App  │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Security Layer  │    │  Orchestrator   │    │  Cache Manager  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Classifier      │    │ Summary Agent   │    │ UX Reviewer     │
│ Agent           │    │                 │    │ Agent           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Design Advisor  │
                    │ Agent           │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for production)
- OpenAI API Key
- Redis (for caching)
- PostgreSQL (for data persistence)

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd multi_agent_system
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements_production.txt
   ```

2. **Configuration**
   ```bash
   cp config.example.env .env
   # Edit .env with your configuration
   ```

3. **Run the Application**
   ```bash
   python api/main.py
   ```

4. **Access the API**
   - API: http://localhost:5000
   - Documentation: http://localhost:5000/api/docs/
   - Health Check: http://localhost:5000/health

## 🏭 Production Deployment

### Docker Deployment

1. **Environment Setup**
   ```bash
   cp config.example.env .env
   # Update .env with production values
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Verify Deployment**
   ```bash
   curl http://localhost/health
   curl http://localhost/api/docs/
   ```

### Kubernetes Deployment

1. **Create Namespace**
   ```bash
   kubectl create namespace multi-agent-system
   ```

2. **Deploy ConfigMap**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   ```

3. **Deploy Application**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

## ⚙️ Configuration

### Environment Variables

| Category | Variable | Description | Default |
|----------|----------|-------------|---------|
| **Application** | `ENVIRONMENT` | Environment (development/staging/production) | `development` |
| | `FLASK_SECRET_KEY` | Flask secret key | `dev-secret-key` |
| **OpenAI** | `OPENAI_API_KEY` | OpenAI API key | Required |
| | `OPENAI_MODEL` | OpenAI model | `gpt-4-turbo-preview` |
| **Security** | `SECURITY_ENABLE` | Enable security features | `True` |
| | `SECURITY_MAX_URL_LENGTH` | Maximum URL length | `2048` |
| **Cache** | `CACHE_TYPE` | Cache backend (memory/redis/file) | `memory` |
| | `CACHE_REDIS_URL` | Redis URL | `redis://localhost:6379/0` |
| **Monitoring** | `MONITORING_ENABLE_HEALTH_CHECKS` | Enable health checks | `True` |
| | `LOG_LEVEL` | Logging level | `INFO` |

### Configuration Files

- **`.env`**: Main configuration file
- **`nginx.conf`**: Nginx reverse proxy configuration
- **`docker-compose.yml`**: Docker Compose services
- **`Dockerfile`**: Application container definition

## 🔒 Security

### Security Features

1. **Input Validation**
   - URL validation and sanitization
   - Request size limits
   - Content type validation

2. **Authentication**
   - API key-based authentication
   - Rate limiting per API key
   - Request origin validation

3. **Content Security**
   - XSS protection
   - Content filtering
   - Malicious pattern detection

4. **Network Security**
   - HTTPS enforcement (production)
   - Security headers
   - CORS configuration

### Security Best Practices

1. **Environment Variables**
   ```bash
   # Use strong, unique secrets
   FLASK_SECRET_KEY=your-very-secure-secret-key-here
   POSTGRES_PASSWORD=your-secure-database-password
   ```

2. **API Keys**
   ```bash
   # Rotate API keys regularly
   API_KEY_1=your-production-api-key-1
   API_KEY_2=your-production-api-key-2
   ```

3. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Enable DDoS protection

## 📊 Monitoring

### Health Checks

The system provides comprehensive health checks:

```bash
# Check overall health
curl http://localhost/health

# Response example
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "system": {
      "status": "healthy",
      "message": "System resources are normal",
      "response_time_ms": 5.2
    },
    "application": {
      "status": "healthy",
      "message": "Application is responsive",
      "response_time_ms": 2.1
    }
  }
}
```

### Metrics

Access metrics at `/metrics` endpoint:

- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Request counts, response times
- **Cache Metrics**: Hit rates, cache size
- **Agent Metrics**: Success rates, execution times

### Logging

Structured JSON logging with rotation:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "api.analyze",
  "message": "Analysis completed successfully",
  "request_id": "req-123",
  "url": "https://example.com",
  "duration_ms": 1500,
  "agents_used": ["classifier", "summary"]
}
```

## 📚 API Documentation

### Interactive Documentation

Access the interactive API documentation at:
- **Swagger UI**: http://localhost:5000/api/docs/
- **OpenAPI Spec**: http://localhost:5000/api/docs/swagger.json

### Example Requests

#### Full Website Analysis
```bash
curl -X POST "http://localhost:5000/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "url": "https://example.com",
    "analysis_depth": "full",
    "output_format": "json"
  }'
```

#### Quick Analysis
```bash
curl -X POST "http://localhost:5000/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "url": "https://example.com",
    "analysis_depth": "quick",
    "output_format": "summary"
  }'
```

### Response Format

```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "status": "completed",
    "classification": {
      "success": true,
      "classification": {
        "type": "landing_page",
        "industry": "technology",
        "confidence": 0.95,
        "reason": "Clear call-to-action and product focus"
      }
    },
    "summary": {
      "success": true,
      "summary": {
        "summary": "Technology company offering business solutions",
        "word_count": 8,
        "key_points": ["Technology", "Business solutions"]
      }
    }
  },
  "metadata": {
    "analysis_time": 15.2,
    "cache_used": false,
    "analysis_depth": "full"
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Errors (401)
```bash
# Check API key
curl -H "X-API-Key: your-api-key" http://localhost:5000/health

# Verify API key format
# Valid keys: test-key-123, admin-key-456
```

#### 2. Rate Limit Errors (429)
```bash
# Check current rate limits
curl -H "X-API-Key: test-key-123" http://localhost:5000/stats

# Wait for rate limit reset or use admin key
```

#### 3. Validation Errors (400)
```bash
# Check URL format
curl -X POST "http://localhost:5000/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{"url": "https://valid-url.com"}'
```

#### 4. Server Errors (500)
```bash
# Check logs
docker-compose logs app

# Check health
curl http://localhost:5000/health

# Verify environment variables
docker-compose exec app env | grep OPENAI
```

### Debug Mode

Enable debug logging:

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Or via environment variable
export LOG_LEVEL=DEBUG
```

### Performance Issues

1. **Check System Resources**
   ```bash
   curl http://localhost:5000/stats
   ```

2. **Monitor Cache Performance**
   ```bash
   curl -H "X-API-Key: test-key-123" http://localhost:5000/cache
   ```

3. **Optimize Configuration**
   - Increase cache TTL
   - Use Redis for caching
   - Enable connection pooling

## ⚡ Performance Optimization

### Caching Strategy

1. **Enable Redis Caching**
   ```bash
   CACHE_TYPE=redis
   CACHE_REDIS_URL=redis://localhost:6379/0
   ```

2. **Optimize Cache TTL**
   ```bash
   CACHE_TTL=3600  # 1 hour for analysis results
   ```

### Database Optimization

1. **Connection Pooling**
   ```bash
   DATABASE_CONNECTION_POOL_SIZE=10
   DATABASE_MAX_OVERFLOW=20
   ```

2. **Query Optimization**
   - Use database indexes
   - Implement query caching
   - Monitor slow queries

### Application Optimization

1. **Async Processing**
   - Use async/await for I/O operations
   - Implement request queuing
   - Enable connection pooling

2. **Resource Management**
   - Monitor memory usage
   - Implement garbage collection
   - Use resource limits

### Load Balancing

1. **Nginx Configuration**
   ```nginx
   upstream app_backend {
       server app1:5000;
       server app2:5000;
       server app3:5000;
   }
   ```

2. **Health Checks**
   ```bash
   # Configure health check endpoints
   location /health {
       proxy_pass http://app_backend;
   }
   ```

## 📞 Support

### Documentation
- **API Docs**: http://localhost:5000/api/docs/
- **Examples**: http://localhost:5000/api/docs/examples
- **Troubleshooting**: http://localhost:5000/api/docs/troubleshooting

### Monitoring
- **Health Check**: http://localhost:5000/health
- **Metrics**: http://localhost:5000/metrics
- **Stats**: http://localhost:5000/stats

### Contact
- **Issues**: GitHub Issues
- **Email**: support@example.com
- **Documentation**: Full documentation available in `/docs`

---

**🚀 Ready for Production!** This system is designed for high availability, security, and performance in production environments.
