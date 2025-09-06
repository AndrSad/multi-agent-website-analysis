"""
Swagger/OpenAPI documentation for the Multi-Agent Website Analysis API.

This module provides comprehensive API documentation with examples,
request/response schemas, and interactive testing capabilities.
"""

from flask import Blueprint, jsonify, render_template_string
from typing import Dict, Any, List, Optional
import json

# Swagger UI HTML template
SWAGGER_UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Website Analysis API</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
        .swagger-ui .topbar {
            background-color: #667eea;
        }
        .swagger-ui .topbar .download-url-wrapper .select-label {
            color: white;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/docs/swagger.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                tryItOutEnabled: true,
                requestInterceptor: function(request) {
                    // Add API key to requests
                    const apiKey = localStorage.getItem('api_key');
                    if (apiKey) {
                        request.headers['X-API-Key'] = apiKey;
                    }
                    return request;
                }
            });
            
            // Add API key input
            const apiKeyInput = document.createElement('div');
            apiKeyInput.innerHTML = `
                <div style="position: fixed; top: 10px; right: 10px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <label for="api-key-input">API Key:</label>
                    <input type="text" id="api-key-input" placeholder="Enter API key" style="margin-left: 5px; padding: 5px; border: 1px solid #ccc; border-radius: 3px;">
                    <button onclick="setApiKey()" style="margin-left: 5px; padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 3px; cursor: pointer;">Set</button>
                </div>
            `;
            document.body.appendChild(apiKeyInput);
            
            window.setApiKey = function() {
                const apiKey = document.getElementById('api-key-input').value;
                localStorage.setItem('api_key', apiKey);
                alert('API key set successfully!');
            };
            
            // Load saved API key
            const savedApiKey = localStorage.getItem('api_key');
            if (savedApiKey) {
                document.getElementById('api-key-input').value = savedApiKey;
            }
        };
    </script>
</body>
</html>
"""

# OpenAPI specification
OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Multi-Agent Website Analysis API",
        "description": "A comprehensive API for analyzing websites using multiple AI agents including classification, summarization, UX analysis, and design recommendations.",
        "version": "2.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@example.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5000",
            "description": "Development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ],
    "security": [
        {
            "ApiKeyAuth": []
        }
    ],
    "paths": {
        "/": {
            "get": {
                "summary": "Get API information",
                "description": "Returns basic information about the API and available endpoints.",
                "tags": ["General"],
                "responses": {
                    "200": {
                        "description": "API information",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ApiInfo"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/analyze": {
            "post": {
                "summary": "Analyze website",
                "description": "Analyze a website using AI agents for classification, summarization, UX analysis, and design recommendations.",
                "tags": ["Analysis"],
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AnalysisRequest"
                            },
                            "examples": {
                                "full_analysis": {
                                    "summary": "Full website analysis",
                                    "value": {
                                        "url": "https://example.com",
                                        "agents_config": {
                                            "classifier": True,
                                            "summary": True,
                                            "ux_reviewer": True,
                                            "design_advisor": True
                                        },
                                        "analysis_depth": "full",
                                        "output_format": "json",
                                        "use_cache": True
                                    }
                                },
                                "quick_analysis": {
                                    "summary": "Quick analysis (classification + summary)",
                                    "value": {
                                        "url": "https://example.com",
                                        "analysis_depth": "quick",
                                        "output_format": "summary"
                                    }
                                },
                                "custom_analysis": {
                                    "summary": "Custom analysis with specific agents",
                                    "value": {
                                        "url": "https://example.com",
                                        "agents_config": {
                                            "classifier": True,
                                            "summary": False,
                                            "ux_reviewer": True,
                                            "design_advisor": False
                                        },
                                        "analysis_depth": "custom",
                                        "output_format": "detailed"
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Analysis completed successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AnalysisResponse"
                                },
                                "examples": {
                                    "successful_analysis": {
                                        "summary": "Successful analysis result",
                                        "value": {
                                            "success": True,
                                            "data": {
                                                "url": "https://example.com",
                                                "status": "completed",
                                                "classification": {
                                                    "success": True,
                                                    "classification": {
                                                        "type": "landing_page",
                                                        "industry": "technology",
                                                        "target_audience": "businesses",
                                                        "confidence": 0.95,
                                                        "reason": "Clear call-to-action buttons and product-focused content"
                                                    }
                                                },
                                                "summary": {
                                                    "success": True,
                                                    "summary": {
                                                        "summary": "Example.com is a technology company offering innovative solutions for businesses.",
                                                        "word_count": 12,
                                                        "sentence_count": 1,
                                                        "key_points": [
                                                            "Technology company",
                                                            "Business solutions",
                                                            "Innovative approach"
                                                        ]
                                                    }
                                                }
                                            },
                                            "metadata": {
                                                "analysis_time": 15.2,
                                                "cache_used": False,
                                                "analysis_depth": "full",
                                                "output_format": "json"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request - invalid input",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized - invalid API key",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "429": {
                        "description": "Too many requests - rate limit exceeded",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "500": {
                        "description": "Internal server error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/scrape": {
            "post": {
                "summary": "Scrape website content",
                "description": "Extract and clean content from a website URL.",
                "tags": ["Scraping"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "url": {
                                        "type": "string",
                                        "format": "uri",
                                        "description": "URL to scrape"
                                    }
                                },
                                "required": ["url"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Content scraped successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "url": {"type": "string"},
                                                "title": {"type": "string"},
                                                "content": {"type": "string"},
                                                "links": {"type": "array", "items": {"type": "string"}},
                                                "images": {"type": "array", "items": {"type": "string"}}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/stats": {
            "get": {
                "summary": "Get system statistics",
                "description": "Get system performance and usage statistics.",
                "tags": ["Monitoring"],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "Statistics retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "total_requests": {"type": "integer"},
                                        "successful_requests": {"type": "integer"},
                                        "failed_requests": {"type": "integer"},
                                        "average_response_time": {"type": "number"},
                                        "cache_hit_rate": {"type": "number"},
                                        "system_metrics": {
                                            "type": "object",
                                            "properties": {
                                                "cpu_percent": {"type": "number"},
                                                "memory_percent": {"type": "number"},
                                                "disk_usage_percent": {"type": "number"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/health": {
            "get": {
                "summary": "Health check",
                "description": "Check the health status of the API and its components.",
                "tags": ["Monitoring"],
                "responses": {
                    "200": {
                        "description": "System is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
                                        "timestamp": {"type": "string", "format": "date-time"},
                                        "checks": {
                                            "type": "object",
                                            "additionalProperties": {
                                                "type": "object",
                                                "properties": {
                                                    "status": {"type": "string"},
                                                    "message": {"type": "string"},
                                                    "response_time_ms": {"type": "number"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/cache": {
            "get": {
                "summary": "Get cache information",
                "description": "Get information about the cache system including statistics and configuration.",
                "tags": ["Cache"],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "Cache information retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "backend_type": {"type": "string"},
                                        "size": {"type": "integer"},
                                        "hit_rate": {"type": "number"},
                                        "stats": {
                                            "type": "object",
                                            "properties": {
                                                "hits": {"type": "integer"},
                                                "misses": {"type": "integer"},
                                                "sets": {"type": "integer"},
                                                "deletes": {"type": "integer"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "delete": {
                "summary": "Clear cache",
                "description": "Clear all cached data.",
                "tags": ["Cache"],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "Cache cleared successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for authentication. Use 'test-key-123' for testing (5 requests/minute) or 'admin-key-456' for admin access (100 requests/minute)."
            }
        },
        "schemas": {
            "ApiInfo": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "description": {"type": "string"},
                    "endpoints": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "authentication": {"type": "string"},
                    "rate_limits": {"type": "object"}
                }
            },
            "AnalysisRequest": {
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL of the website to analyze",
                        "example": "https://example.com"
                    },
                    "agents_config": {
                        "type": "object",
                        "description": "Configuration for which agents to use",
                        "properties": {
                            "classifier": {
                                "type": "boolean",
                                "description": "Enable website classification agent",
                                "default": True
                            },
                            "summary": {
                                "type": "boolean",
                                "description": "Enable content summarization agent",
                                "default": True
                            },
                            "ux_reviewer": {
                                "type": "boolean",
                                "description": "Enable UX analysis agent",
                                "default": True
                            },
                            "design_advisor": {
                                "type": "boolean",
                                "description": "Enable design recommendation agent",
                                "default": True
                            }
                        }
                    },
                    "analysis_depth": {
                        "type": "string",
                        "enum": ["quick", "full", "custom"],
                        "description": "Depth of analysis to perform",
                        "default": "full"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "summary", "detailed"],
                        "description": "Format of the output",
                        "default": "json"
                    },
                    "use_cache": {
                        "type": "boolean",
                        "description": "Whether to use cached results if available",
                        "default": True
                    }
                }
            },
            "AnalysisResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether the analysis was successful"
                    },
                    "data": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "status": {"type": "string"},
                            "classification": {"$ref": "#/components/schemas/AgentResult"},
                            "summary": {"$ref": "#/components/schemas/AgentResult"},
                            "ux_review": {"$ref": "#/components/schemas/AgentResult"},
                            "design_advice": {"$ref": "#/components/schemas/AgentResult"}
                        }
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "analysis_time": {"type": "number"},
                            "cache_used": {"type": "boolean"},
                            "analysis_depth": {"type": "string"},
                            "output_format": {"type": "string"}
                        }
                    }
                }
            },
            "AgentResult": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "error": {"type": "string"},
                    "classification": {"$ref": "#/components/schemas/ClassificationResult"},
                    "summary": {"$ref": "#/components/schemas/SummaryResult"},
                    "ux_review": {"$ref": "#/components/schemas/UXReviewResult"},
                    "design_advice": {"$ref": "#/components/schemas/DesignAdviceResult"}
                }
            },
            "ClassificationResult": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["landing_page", "blog", "ecommerce", "corporate", "portfolio", "other"]
                    },
                    "industry": {"type": "string"},
                    "target_audience": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "reason": {"type": "string"}
                }
            },
            "SummaryResult": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "word_count": {"type": "integer"},
                    "sentence_count": {"type": "integer"},
                    "key_points": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "UXReviewResult": {
                "type": "object",
                "properties": {
                    "overall_score": {"type": "number", "minimum": 0, "maximum": 10},
                    "word_count": {"type": "integer"},
                    "strengths": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "weaknesses": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                            }
                        }
                    }
                }
            },
            "DesignAdviceResult": {
                "type": "object",
                "properties": {
                    "overall_design_score": {"type": "number", "minimum": 0, "maximum": 10},
                    "is_landing_page": {"type": "boolean"},
                    "recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "category": {"type": "string"},
                                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                "implementation_difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]}
                            }
                        }
                    }
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "default": False},
                    "error": {"type": "string"},
                    "error_code": {"type": "string"},
                    "details": {"type": "object"}
                }
            }
        }
    },
    "tags": [
        {
            "name": "General",
            "description": "General API information and status"
        },
        {
            "name": "Analysis",
            "description": "Website analysis operations"
        },
        {
            "name": "Scraping",
            "description": "Web scraping operations"
        },
        {
            "name": "Monitoring",
            "description": "System monitoring and health checks"
        },
        {
            "name": "Cache",
            "description": "Cache management operations"
        }
    ]
}

# Create Blueprint for Swagger documentation
swagger_bp = Blueprint('swagger', __name__, url_prefix='/api/docs')

@swagger_bp.route('/')
def swagger_ui():
    """Serve Swagger UI."""
    return render_template_string(SWAGGER_UI_TEMPLATE)

@swagger_bp.route('/swagger.json')
def swagger_json():
    """Serve OpenAPI specification as JSON."""
    return jsonify(OPENAPI_SPEC)

@swagger_bp.route('/examples')
def examples():
    """Provide example requests and responses."""
    examples_data = {
        "curl_examples": {
            "full_analysis": {
                "description": "Perform full website analysis",
                "command": """curl -X POST "http://localhost:5000/analyze" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: test-key-123" \\
  -d '{
    "url": "https://example.com",
    "analysis_depth": "full",
    "output_format": "json"
  }'"""
            },
            "quick_analysis": {
                "description": "Perform quick analysis (classification + summary)",
                "command": """curl -X POST "http://localhost:5000/analyze" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: test-key-123" \\
  -d '{
    "url": "https://example.com",
    "analysis_depth": "quick",
    "output_format": "summary"
  }'"""
            },
            "custom_analysis": {
                "description": "Perform custom analysis with specific agents",
                "command": """curl -X POST "http://localhost:5000/analyze" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: test-key-123" \\
  -d '{
    "url": "https://example.com",
    "agents_config": {
      "classifier": true,
      "summary": false,
      "ux_reviewer": true,
      "design_advisor": false
    },
    "analysis_depth": "custom",
    "output_format": "detailed"
  }'"""
            },
            "health_check": {
                "description": "Check system health",
                "command": """curl -X GET "http://localhost:5000/health" """
            },
            "get_stats": {
                "description": "Get system statistics",
                "command": """curl -X GET "http://localhost:5000/stats" \\
  -H "X-API-Key: test-key-123" """
            }
        },
        "python_examples": {
            "full_analysis": {
                "description": "Perform full website analysis using Python requests",
                "code": """import requests

url = "http://localhost:5000/analyze"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "test-key-123"
}
data = {
    "url": "https://example.com",
    "analysis_depth": "full",
    "output_format": "json"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

if result["success"]:
    print("Analysis completed successfully!")
    print(f"Website type: {result['data']['classification']['classification']['type']}")
    print(f"Summary: {result['data']['summary']['summary']['summary']}")
else:
    print(f"Analysis failed: {result['error']}")"""
            }
        },
        "javascript_examples": {
            "full_analysis": {
                "description": "Perform full website analysis using JavaScript fetch",
                "code": """const analyzeWebsite = async (url) => {
  const response = await fetch('http://localhost:5000/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'test-key-123'
    },
    body: JSON.stringify({
      url: url,
      analysis_depth: 'full',
      output_format: 'json'
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('Analysis completed successfully!');
    console.log('Website type:', result.data.classification.classification.type);
    console.log('Summary:', result.data.summary.summary.summary);
  } else {
    console.error('Analysis failed:', result.error);
  }
};

// Usage
analyzeWebsite('https://example.com');"""
            }
        }
    }
    
    return jsonify(examples_data)

@swagger_bp.route('/troubleshooting')
def troubleshooting():
    """Provide troubleshooting guide."""
    troubleshooting_guide = {
        "common_issues": {
            "authentication_errors": {
                "problem": "401 Unauthorized errors",
                "solutions": [
                    "Ensure you're using a valid API key",
                    "Check that the X-API-Key header is included in your request",
                    "Verify the API key format (test-key-123 or admin-key-456)",
                    "Make sure you're not exceeding rate limits"
                ]
            },
            "rate_limit_errors": {
                "problem": "429 Too Many Requests errors",
                "solutions": [
                    "Wait for the rate limit window to reset",
                    "Use the admin API key for higher limits",
                    "Implement exponential backoff in your client",
                    "Consider caching results to reduce API calls"
                ]
            },
            "validation_errors": {
                "problem": "400 Bad Request errors",
                "solutions": [
                    "Check that the URL is valid and accessible",
                    "Ensure all required fields are provided",
                    "Verify the request body format is correct JSON",
                    "Check that enum values match the allowed options"
                ]
            },
            "server_errors": {
                "problem": "500 Internal Server Error",
                "solutions": [
                    "Check the server logs for detailed error information",
                    "Verify that all required environment variables are set",
                    "Ensure the OpenAI API key is valid and has sufficient credits",
                    "Check system resources (CPU, memory, disk space)"
                ]
            },
            "timeout_errors": {
                "problem": "Request timeouts",
                "solutions": [
                    "Increase the client timeout value",
                    "Use quick analysis for faster results",
                    "Check network connectivity",
                    "Consider using cached results if available"
                ]
            }
        },
        "debugging_tips": {
            "enable_debug_logging": "Set LOG_LEVEL=DEBUG in environment variables",
            "check_health_endpoint": "Use /health endpoint to verify system status",
            "monitor_metrics": "Use /stats endpoint to check system performance",
            "test_with_simple_urls": "Start with simple, well-known websites for testing",
            "verify_api_key_permissions": "Ensure your API key has the required permissions"
        },
        "performance_optimization": {
            "use_caching": "Enable caching to reduce response times for repeated requests",
            "choose_appropriate_analysis_depth": "Use 'quick' for faster results, 'full' for comprehensive analysis",
            "optimize_output_format": "Use 'summary' format for faster processing",
            "batch_requests": "When possible, batch multiple analysis requests",
            "monitor_rate_limits": "Keep track of your API usage to avoid hitting limits"
        },
        "support": {
            "documentation": "Check the full API documentation at /api/docs/",
            "examples": "See example requests at /api/docs/examples",
            "health_check": "Use /health endpoint to verify system status",
            "contact": "For additional support, contact support@example.com"
        }
    }
    
    return jsonify(troubleshooting_guide)
