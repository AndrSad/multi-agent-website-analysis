"""
Flask API Main Application

This module provides REST API endpoints for the multi-agent website analysis system.
"""

import asyncio
import time
import logging
import os
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from functools import wraps

# Flask imports
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Pydantic imports
from pydantic import BaseModel, Field, validator, HttpUrl
from pydantic.error_wrappers import ValidationError

# Local imports
from multi_agent_system.core.orchestrator import CrewOrchestrator
from multi_agent_system.core.config import config


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Initialize orchestrator
orchestrator = CrewOrchestrator()

# API Keys storage (in production, use a proper database)
VALID_API_KEYS = {
    os.getenv("API_KEY_1", "test-key-123"): {"user": "test_user", "rate_limit": "5 per minute"},
    os.getenv("API_KEY_2", "admin-key-456"): {"user": "admin_user", "rate_limit": "100 per minute"},
}

# Cache for API responses
api_cache = {}


# Pydantic Models for Request/Response Validation
class AgentsConfig(BaseModel):
    """Configuration for which agents to run."""
    classifier: bool = Field(default=True, description="Run classifier agent")
    summary: bool = Field(default=True, description="Run summary agent")
    ux_reviewer: bool = Field(default=True, description="Run UX reviewer agent")
    design_advisor: bool = Field(default=True, description="Run design advisor agent")


class AnalysisRequest(BaseModel):
    """Request model for website analysis."""
    url: HttpUrl = Field(..., description="Website URL to analyze")
    agents_config: Optional[AgentsConfig] = Field(default_factory=AgentsConfig, description="Agent configuration")
    analysis_depth: str = Field(default="full", description="Analysis depth: full, quick, or custom")
    output_format: str = Field(default="json", description="Output format: json, summary, detailed")
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    
    @validator('analysis_depth')
    def validate_analysis_depth(cls, v):
        allowed_depths = ['full', 'quick', 'custom']
        if v not in allowed_depths:
            raise ValueError(f'analysis_depth must be one of: {allowed_depths}')
        return v
    
    @validator('output_format')
    def validate_output_format(cls, v):
        allowed_formats = ['json', 'summary', 'detailed']
        if v not in allowed_formats:
            raise ValueError(f'output_format must be one of: {allowed_formats}')
        return v


class AnalysisResponse(BaseModel):
    """Response model for website analysis."""
    success: bool = Field(..., description="Whether the analysis was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Analysis results")
    error: Optional[str] = Field(None, description="Error message if analysis failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    timestamp: float = Field(default_factory=time.time, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: float = Field(default_factory=time.time, description="Error timestamp")


# Authentication decorator
def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify(ErrorResponse(
                error="API key required",
                error_code="MISSING_API_KEY"
            ).dict()), 401
        
        if api_key not in VALID_API_KEYS:
            return jsonify(ErrorResponse(
                error="Invalid API key",
                error_code="INVALID_API_KEY"
            ).dict()), 401
        
        # Store user info in g for use in the endpoint
        g.api_key = api_key
        g.user_info = VALID_API_KEYS[api_key]
        
        return f(*args, **kwargs)
    return decorated_function


# Cache decorator
def cache_response(ttl: int = 3600):
    """Decorator to cache API responses."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key = hashlib.md5(
                f"{request.endpoint}:{request.get_json()}:{g.get('api_key', 'anonymous')}".encode()
            ).hexdigest()
            
            # Check cache
            if cache_key in api_cache:
                cached_data, timestamp = api_cache[cache_key]
                if time.time() - timestamp < ttl:
                    logging.info(f"Cache hit for key: {cache_key}")
                    return jsonify(cached_data)
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Cache result
            if result[1] == 200:  # Only cache successful responses
                api_cache[cache_key] = (result[0].get_json(), time.time())
                logging.info(f"Cached response for key: {cache_key}")
            
            return result
        return decorated_function
    return decorator


@app.route('/', methods=['GET'])
def index():
    """Root endpoint: show available routes."""
    return jsonify({
        'status': 'ok',
        'message': 'Multi-Agent Website Analysis API',
        'version': '2.0.0',
        'endpoints': {
            'health': 'GET /health',
            'analyze': 'POST /analyze (requires API key)',
            'scrape': 'POST /scrape {"url": "https://example.com"}',
            'config': 'GET /config',
            'stats': 'GET /stats (requires API key)',
            'cache': 'GET /cache (requires API key)'
        },
        'authentication': {
            'method': 'API Key',
            'header': 'X-API-Key',
            'parameter': 'api_key'
        },
        'rate_limits': {
            'default': '5 requests per minute',
            'admin': '100 requests per minute'
        }
    })


@app.route('/ui', methods=['GET'])
def ui_page():
    """Simple HTML UI to interact with the API from a browser."""
    return (
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Multi-Agent Website Analysis UI</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji'; margin: 24px; }
    .card { max-width: 920px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    h1 { margin-top: 0; font-size: 20px; }
    input[type="text"] { width: 100%; padding: 10px 12px; font-size: 14px; border: 1px solid #cbd5e1; border-radius: 8px; }
    .row { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
    button { padding: 10px 14px; border: 0; border-radius: 8px; cursor: pointer; background: #2563eb; color: white; }
    button.secondary { background: #64748b; }
    pre { background: #0b1020; color: #e5e7eb; padding: 12px; border-radius: 8px; overflow: auto; max-height: 60vh; }
    .results { background: #fff; color: #111827; padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px; }
    .section { border-left: 4px solid #2563eb; background:#f8fafc; padding:12px; border-radius:8px; margin:12px 0; }
    .section h3 { margin: 0 0 8px 0; }
    .hint { color: #64748b; font-size: 12px; }
    .ok { color: #16a34a; }
    .err { color: #dc2626; }
  </style>
  <script>
    function htmlesc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
    function renderHtml(parsed){
      try{
        const container = document.getElementById('output');
        if(!parsed || parsed.success===false){ container.innerHTML = `<div class='section'><h3>Ошибка</h3><div>${htmlesc(parsed?.error||'Unknown')}</div></div>`; return; }
        const data = parsed.data || parsed;
        const mode = (parsed.metadata && parsed.metadata.output_format) || 'json';
        let html = '';
        // Общая информация
        html += `<div class='section'><h3>Общая информация</h3>
          <div><strong>URL:</strong> ${htmlesc(data.url||'')}</div>
          <div><strong>Статус:</strong> ${htmlesc(data.status||'')}</div>
          <div><strong>Тип анализа:</strong> ${htmlesc(parsed.metadata?.analysis_depth||'')}</div>
        </div>`;
        // Классификация
        const cls = data.classification;
        if(cls){
          if(typeof cls === 'string'){
            html += `<div class='section'><h3>Классификация</h3>
              <div><strong>Тип сайта:</strong> ${htmlesc(cls)}</div>
            </div>`;
          } else if(cls.success){
            const c = cls.classification||{};
            html += `<div class='section'><h3>Классификация</h3>
              <div><strong>Тип сайта:</strong> ${htmlesc(c.type||'')}</div>
              <div><strong>Индустрия:</strong> ${htmlesc(c.industry||'')}</div>
              <div><strong>Целевая аудитория:</strong> ${htmlesc(c.target_audience||'')}</div>
              <div><strong>Уверенность:</strong> ${typeof c.confidence==='number'? (c.confidence*100).toFixed(1)+'%':''}</div>
              <div><strong>Обоснование:</strong> ${htmlesc(c.reason||'')}</div>
            </div>`;
          }
        }
        // Резюме
        const sum = data.summary;
        if(sum){
          if(typeof sum === 'string' || mode==='summary'){
            const txt = typeof sum === 'string' ? sum : (sum.summary?.summary||'');
            html += `<div class='section'><h3>Краткое резюме</h3><div>${htmlesc(txt||'')}</div></div>`;
          } else if(sum.success){
            const s = sum.summary||{};
            html += `<div class='section'><h3>Краткое резюме</h3>
              <div>${htmlesc(s.summary||'')}</div>
              ${Array.isArray(s.key_points)?`<ul>${s.key_points.map(p=>`<li>${htmlesc(p)}</li>`).join('')}</ul>`:''}
            </div>`;
          }
        }
        // UX
        const ux = data.ux_review;
        if(ux && ux.success){
          const u = ux.ux_review||{};
          html += `<div class='section'><h3>UX Анализ</h3>
            <div><strong>Оценка:</strong> ${htmlesc(u.overall_score||'')}</div>
            ${Array.isArray(u.strengths)?`<div><strong>Достоинства:</strong><ul>${u.strengths.map(x=>`<li>${htmlesc(x)}</li>`).join('')}</ul></div>`:''}
            ${Array.isArray(u.weaknesses)?`<div><strong>Слабые места:</strong><ul>${u.weaknesses.map(x=>`<li>${htmlesc(x)}</li>`).join('')}</ul></div>`:''}
            ${Array.isArray(u.recommendations)?`<div><strong>Рекомендации:</strong><ol>${u.recommendations.map(r=>`<li><strong>${htmlesc(r.title||'')}</strong> — ${htmlesc(r.description||'')} (${htmlesc(r.priority||'')})</li>`).join('')}</ol></div>`:''}
          </div>`;
        }
        // Дизайн
        const da = data.design_advice;
        if(da && da.success){
          const d = da.design_advice||{};
          html += `<div class='section'><h3>Советы по дизайну</h3>
            <div><strong>Оценка дизайна:</strong> ${htmlesc(d.overall_design_score||'')}</div>
            ${Array.isArray(d.recommendations)?`<div><strong>Рекомендации:</strong><ol>${d.recommendations.map(r=>`<li><strong>${htmlesc(r.title||'')}</strong> — ${htmlesc(r.description||'')} (${htmlesc(r.category||'')}, ${htmlesc(r.priority||'')}, ${htmlesc(r.implementation_difficulty||'')})</li>`).join('')}</ol></div>`:''}
          </div>`;
        }
        container.innerHTML = html || '<div class="section">Нет данных</div>';
      }catch(e){
        document.getElementById('output').innerText = 'Ошибка отображения: '+e;
      }
    }
    async function callApi(path, payload, method = 'POST', headers = {}) {
      const defaultHeaders = { 'Content-Type': 'application/json' };
      const apiKey = document.getElementById('apiKey').value.trim();
      if (apiKey) defaultHeaders['X-API-Key'] = apiKey;
      
      const res = await fetch(path, { 
        method, 
        headers: { ...defaultHeaders, ...headers }, 
        body: payload ? JSON.stringify(payload) : undefined 
      });
      const text = await res.text();
      let parsedJson = null; try { parsedJson = JSON.parse(text); } catch {}
      if(parsedJson){ renderHtml(parsedJson); }
      else { document.getElementById('output').textContent = text; }
      document.getElementById('status').textContent = res.ok ? 'OK' : 'ERROR';
      document.getElementById('status').className = res.ok ? 'ok' : 'err';
    }
    function scrape() {
      const url = document.getElementById('url').value.trim();
      if (!url) return alert('Введите URL');
      callApi('/scrape', { url });
    }
    function analyze(type) {
      const url = document.getElementById('url').value.trim();
      if (!url) return alert('Введите URL');
      const apiKey = document.getElementById('apiKey').value.trim();
      if (!apiKey) return alert('Введите API ключ для анализа');
      
      const payload = {
        url,
        analysis_depth: type,
        agents_config: {
          classifier: document.getElementById('classifier').checked,
          summary: document.getElementById('summary').checked,
          ux_reviewer: document.getElementById('ux_reviewer').checked,
          design_advisor: document.getElementById('design_advisor').checked
        },
        output_format: document.getElementById('output_format').value,
        use_cache: document.getElementById('use_cache').checked
      };
      callApi('/analyze', payload);
    }
    async function health() {
      const res = await fetch('/health'); const data = await res.json();
      document.getElementById('output').textContent = JSON.stringify(data, null, 2);
      document.getElementById('status').textContent = res.ok ? 'OK' : 'ERROR';
      document.getElementById('status').className = res.ok ? 'ok' : 'err';
    }
    async function getStats() {
      const apiKey = document.getElementById('apiKey').value.trim();
      if (!apiKey) return alert('Введите API ключ');
      callApi('/stats', null, 'GET');
    }
    async function getCache() {
      const apiKey = document.getElementById('apiKey').value.trim();
      if (!apiKey) return alert('Введите API ключ');
      callApi('/cache', null, 'GET');
    }
    async function clearCache() {
      const apiKey = document.getElementById('apiKey').value.trim();
      if (!apiKey) return alert('Введите API ключ');
      if (!confirm('Очистить все кэши?')) return;
      callApi('/cache', null, 'DELETE');
    }
  </script>
  </head>
  <body>
    <div class="card">
      <h1>Multi-Agent Website Analysis UI v2.0</h1>
      
      <label for="apiKey">API Key (для анализа)</label>
      <input id="apiKey" type="text" placeholder="test-key-123 или admin-key-456" />
      
      <label for="url">URL сайта</label>
      <input id="url" type="text" placeholder="https://example.com" />
      
      <div style="margin: 16px 0;">
        <strong>Агенты:</strong>
        <div style="display: flex; gap: 16px; margin-top: 8px;">
          <label><input id="classifier" type="checkbox" checked /> Классификатор</label>
          <label><input id="summary" type="checkbox" checked /> Резюме</label>
          <label><input id="ux_reviewer" type="checkbox" checked /> UX</label>
          <label><input id="design_advisor" type="checkbox" checked /> Дизайн</label>
        </div>
      </div>
      
      <div style="margin: 16px 0;">
        <label for="output_format">Формат вывода:</label>
        <select id="output_format" style="padding: 8px; border-radius: 4px; margin-left: 8px;">
          <option value="json">JSON</option>
          <option value="summary">Краткий</option>
          <option value="detailed">Подробный</option>
        </select>
        
        <label style="margin-left: 16px;">
          <input id="use_cache" type="checkbox" checked /> Использовать кэш
        </label>
      </div>
      
      <div class="row">
        <button onclick="scrape()">Скрапинг</button>
        <button class="secondary" onclick="analyze('quick')">Быстрый</button>
        <button class="secondary" onclick="analyze('full')">Полный</button>
        <button class="secondary" onclick="analyze('custom')">Пользовательский</button>
        <button class="secondary" onclick="health()">Статус</button>
      </div>
      
      <div class="row">
        <button class="secondary" onclick="getStats()">Статистика</button>
        <button class="secondary" onclick="getCache()">Инфо кэша</button>
        <button class="secondary" onclick="clearCache()">Очистить кэш</button>
      </div>
      
      <p class="hint">
        API Keys: test-key-123 (5 req/min), admin-key-456 (100 req/min)<br>
        Для анализа требуется настроенный OPENAI_API_KEY в файле .env. Scrape работает без ключа.
      </p>
      
      <div class="row" style="align-items:center; gap:12px; margin-top:8px;">
        <strong>Статус: <span id="status">—</span></strong>
      </div>
      <div id="output" class="results">Результат появится здесь…</div>
    </div>
  </body>
</html>
        """,
        200,
        {"Content-Type": "text/html; charset=utf-8"}
    )



@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Multi-Agent Website Analysis System',
        'version': '1.0.0'
    })


@app.route('/analyze', methods=['POST'])
@require_api_key
@limiter.limit(lambda: g.user_info.get('rate_limit', '5 per minute'))
@cache_response(ttl=3600)
def analyze_website():
    """
    Analyze a website using configured agents.
    
    Expected JSON payload:
    {
        "url": "https://example.com",
        "agents_config": {
            "classifier": true,
            "summary": true,
            "ux_reviewer": true,
            "design_advisor": true
        },
        "analysis_depth": "full|quick|custom",
        "output_format": "json|summary|detailed",
        "use_cache": true
    }
    """
    try:
        # Parse and validate request
        try:
            request_data = request.get_json()
            if not request_data:
                return jsonify(ErrorResponse(
                    error="Request body is required",
                    error_code="MISSING_BODY"
                ).dict()), 400
            
            analysis_request = AnalysisRequest(**request_data)
        except ValidationError as e:
            return jsonify(ErrorResponse(
                error=f"Validation error: {str(e)}",
                error_code="VALIDATION_ERROR"
            ).dict()), 400
        
        # Perform analysis based on depth
        start_time = time.time()
        
        if analysis_request.analysis_depth == "quick":
            result = asyncio.run(orchestrator.get_quick_analysis(
                str(analysis_request.url), 
                use_cache=analysis_request.use_cache
            ))
        elif analysis_request.analysis_depth == "custom":
            # Custom analysis based on agents_config
            result = asyncio.run(_run_custom_analysis(analysis_request))
        else:  # full
            result = asyncio.run(orchestrator.analyze_website(
                str(analysis_request.url), 
                use_cache=analysis_request.use_cache
            ))
        
        analysis_time = time.time() - start_time
        
        # Check for errors
        if 'error' in result:
            return jsonify(ErrorResponse(
                error=result['error'],
                error_code="ANALYSIS_ERROR"
            ).dict()), 500
        
        # Format response based on output_format
        formatted_result = _format_analysis_result(result, analysis_request.output_format)
        
        # Create response
        response = AnalysisResponse(
            success=True,
            data=formatted_result,
            metadata={
                'analysis_time': analysis_time,
                'analysis_depth': analysis_request.analysis_depth,
                'output_format': analysis_request.output_format,
                'agents_used': analysis_request.agents_config.dict(),
                'user': g.user_info.get('user'),
                'cache_used': analysis_request.use_cache,
                'timestamp': time.time()
            }
        )
        
        return jsonify(response.dict()), 200
        
    except Exception as e:
        logging.error(f"Error in analyze_website endpoint: {str(e)}")
        return jsonify(ErrorResponse(
            error=f"Internal server error: {str(e)}",
            error_code="INTERNAL_ERROR"
        ).dict()), 500


async def _run_custom_analysis(request: AnalysisRequest) -> Dict[str, Any]:
    """Run custom analysis based on agents configuration."""
    try:
        # Scrape website first
        website_data = await orchestrator._scrape_website_with_retry(str(request.url))
        
        if 'error' in website_data:
            return {'error': f"Failed to scrape website: {website_data['error']}"}
        
        results = {}
        
        # Run classifier if requested
        if request.agents_config.classifier:
            results['classification'] = await orchestrator._run_classifier_with_retry(website_data)
        
        # Run other agents based on configuration
        tasks = []
        if request.agents_config.summary:
            tasks.append(('summary', orchestrator._run_summary_with_retry(
                website_data, results.get('classification')
            )))
        
        if request.agents_config.ux_reviewer:
            tasks.append(('ux_review', orchestrator._run_ux_reviewer_with_retry(
                website_data, results.get('classification')
            )))
        
        if request.agents_config.design_advisor:
            # Only run if it's a landing page
            classification = results.get('classification', {})
            if (classification.get('success') and 
                classification.get('classification', {}).get('type') == 'landing_page'):
                tasks.append(('design_advice', orchestrator._run_design_advisor_with_retry(
                    website_data, classification
                )))
        
        # Run tasks in parallel
        if tasks:
            task_results = await asyncio.gather(
                *[task for _, task in tasks], 
                return_exceptions=True
            )
            
            for i, (name, _) in enumerate(tasks):
                if isinstance(task_results[i], Exception):
                    results[name] = {'success': False, 'error': str(task_results[i])}
                else:
                    results[name] = task_results[i]
        
        # Aggregate results
        return orchestrator._aggregate_results(
            str(request.url), website_data,
            results.get('classification'),
            results.get('summary'),
            results.get('ux_review'),
            results.get('design_advice')
        )
        
    except Exception as e:
        return {'error': f"Custom analysis failed: {str(e)}"}


def _format_analysis_result(result: Dict[str, Any], output_format: str) -> Dict[str, Any]:
    """Format analysis result based on output format."""
    if output_format == "summary":
        return {
            'url': result.get('url'),
            'status': result.get('status'),
            'summary': result.get('summary', {}).get('summary', 'No summary available'),
            'classification': result.get('classification', {}).get('classification', {}).get('type', 'Unknown'),
            'success_rate': result.get('success_rate', 0)
        }
    elif output_format == "detailed":
        return {
            'url': result.get('url'),
            'status': result.get('status'),
            'website_data': {
                'title': result.get('website_data', {}).get('title', ''),
                'meta_description': result.get('website_data', {}).get('meta_description', ''),
                'content_length': len(result.get('website_data', {}).get('content', '')),
                'scraped_at': result.get('website_data', {}).get('scraped_at')
            },
            'classification': result.get('classification'),
            'summary': result.get('summary'),
            'ux_review': result.get('ux_review'),
            'design_advice': result.get('design_advice'),
            'metadata': result.get('metadata', {}),
            'success_rate': result.get('success_rate', 0)
        }
    else:  # json (default)
        return result


@app.route('/scrape', methods=['POST'])
def scrape_website():
    """
    Scrape a website and return raw data.
    
    Expected JSON payload:
    {
        "url": "https://example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'URL is required',
                'status': 'error'
            }), 400
        
        url = data['url']
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'error': 'Invalid URL format. URL must start with http:// or https://',
                'status': 'error'
            }), 400
        
        # Scrape website
        website_data = orchestrator.scraping_tool.scrape_website(url)
        
        if 'error' in website_data:
            return jsonify({
                'error': website_data['error'],
                'status': 'error'
            }), 500
        
        return jsonify({
            'data': website_data,
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error in scrape_website endpoint: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500


@app.route('/config', methods=['GET'])
def get_config():
    """Get current system configuration (without sensitive data)."""
    try:
        safe_config = {
            'openai_model': config.openai_model,
            'crewai_verbose': config.crewai_verbose,
            'crewai_memory': config.crewai_memory,
            'scraping_timeout': config.scraping_timeout,
            'max_iterations': config.max_iterations,
            'temperature': config.temperature,
            'log_level': config.log_level,
            'rate_limit_per_minute': config.rate_limit_per_minute
        }
        
        return jsonify({
            'data': safe_config,
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error in get_config endpoint: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500


@app.route('/stats', methods=['GET'])
@require_api_key
def get_statistics():
    """Get orchestrator statistics (requires API key)."""
    try:
        stats = orchestrator.get_statistics()
        
        return jsonify({
            'data': stats,
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error in get_statistics endpoint: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500


@app.route('/cache', methods=['GET'])
@require_api_key
def get_cache_info():
    """Get cache information (requires API key)."""
    try:
        cache_info = orchestrator.get_cache_info()
        api_cache_info = {
            'api_cache_size': len(api_cache),
            'api_cache_keys': list(api_cache.keys())[:10]  # Show first 10 keys
        }
        
        return jsonify({
            'data': {
                'orchestrator_cache': cache_info,
                'api_cache': api_cache_info
            },
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error in get_cache_info endpoint: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500


@app.route('/cache', methods=['DELETE'])
@require_api_key
def clear_cache():
    """Clear all caches (requires API key)."""
    try:
        # Clear orchestrator cache
        orchestrator.clear_cache()
        
        # Clear API cache
        global api_cache
        api_cache.clear()
        
        return jsonify({
            'message': 'All caches cleared successfully',
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error in clear_cache endpoint: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'error': 'Method not allowed',
        'status': 'error'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500


if __name__ == '__main__':
    # Validate configuration
    try:
        config.validate_config()
        logging.info("Configuration validated successfully")
    except Exception as e:
        logging.error(f"Configuration validation failed: {str(e)}")
        exit(1)
    
    # Run the Flask app
    flask_config = config.get_flask_config()
    app.run(
        host=flask_config['host'],
        port=flask_config['port'],
        debug=flask_config['debug']
    )
