# 📚 Примеры использования Multi-Agent Website Analysis System

## 🚀 Быстрый старт

### 1. Локальный запуск
```bash
# Клонирование репозитория
git clone https://github.com/AndrSad/multi-agent-website-analysis.git
cd multi-agent-website-analysis

# Установка зависимостей
pip install -r multi_agent_system/requirements.txt

# Настройка переменных окружения
cp env.example .env
# Отредактируйте .env и добавьте OPENAI_API_KEY

# Запуск сервера
python -m multi_agent_system.api.main
```

### 2. Docker запуск
```bash
# Быстрый запуск
docker-compose up --build

# Или через скрипт (Windows)
deploy.bat
```

## 🌐 API Примеры

### Базовые запросы

#### 1. Проверка состояния системы
```bash
curl http://localhost:5000/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "version": "1.0.0",
  "agents": {
    "classifier": "ready",
    "summary": "ready", 
    "ux_reviewer": "ready",
    "design_advisor": "ready"
  }
}
```

#### 2. Полный анализ веб-сайта
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "analysis_type": "full",
    "output_format": "json"
  }'
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "website_data": {
      "title": "Example Website",
      "meta_description": "Example description",
      "content": "Website content...",
      "headers": [...],
      "links": [...],
      "images": [...],
      "forms": [...],
      "buttons": [...],
      "navigation": [...],
      "colors": [...],
      "fonts": [...],
      "layout_elements": [...],
      "performance_metrics": {...}
    },
    "analysis_results": {
      "classification": {
        "type": "landing_page",
        "confidence": 0.95,
        "industry": "SaaS",
        "target_audience": "Small business owners",
        "business_model": "Subscription-based"
      },
      "summary": {
        "summary": "Сайт представляет собой SaaS-платформу...",
        "word_count": 142,
        "key_points": ["Управление проектами", "Интеграции", "Бесплатный план"]
      },
      "ux_review": {
        "strengths": ["Интуитивная навигация", "Быстрая загрузка"],
        "weaknesses": ["Отсутствие поиска", "Слишком много текста"],
        "recommendations": [...]
      },
      "design_advice": {
        "recommendations": [
          {
            "title": "Улучшить контрастность",
            "category": "visual",
            "priority": "high",
            "implementation_difficulty": "easy"
          }
        ]
      }
    }
  },
  "metadata": {
    "processing_time": 45.2,
    "agents_used": ["classifier", "summary", "ux_reviewer", "design_advisor"],
    "cache_hit": false
  }
}
```

#### 3. Быстрый анализ
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "analysis_type": "quick"
  }'
```

#### 4. Только скрапинг
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
  }'
```

## 🎯 Примеры для разных типов сайтов

### 1. Анализ лендинговой страницы SaaS продукта

**Запрос:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://notion.so",
    "analysis_type": "full",
    "output_format": "detailed"
  }'
```

**Ожидаемые результаты:**
- **Классификация:** Landing Page, Productivity Tools, B2B
- **Резюме:** Описание функций, ценообразование, CTA кнопки
- **UX:** Оценка навигации, форм регистрации, мобильной версии
- **Дизайн:** Рекомендации по цветам, типографике, макету

### 2. Анализ интернет-магазина

**Запрос:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://shopify.com",
    "analysis_type": "full"
  }'
```

**Ожидаемые результаты:**
- **Классификация:** E-commerce Platform, B2B, SaaS
- **Резюме:** Каталог функций, тарифные планы, партнеры
- **UX:** Оценка каталога, поиска, корзины, checkout
- **Дизайн:** Рекомендации по витрине, товарным карточкам

### 3. Анализ корпоративного сайта

**Запрос:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://microsoft.com",
    "analysis_type": "quick"
  }'
```

**Ожидаемые результаты:**
- **Классификация:** Corporate, Technology, B2B/B2C
- **Резюме:** Основные продукты, новости, карьера
- **UX:** Оценка навигации, поиска, доступности
- **Дизайн:** Рекомендации по брендингу, консистентности

## 🐍 Python примеры

### 1. Базовое использование
```python
import requests
import json

# Настройка
API_BASE = "http://localhost:5000"
API_KEY = "your-api-key"  # если настроена аутентификация

# Функция для анализа сайта
def analyze_website(url, analysis_type="full"):
    response = requests.post(
        f"{API_BASE}/analyze",
        headers={"Content-Type": "application/json"},
        json={
            "url": url,
            "analysis_type": analysis_type,
            "output_format": "json"
        }
    )
    return response.json()

# Пример использования
result = analyze_website("https://example.com")
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 2. Массовый анализ сайтов
```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def analyze_multiple_sites(urls, max_workers=3):
    """Анализ нескольких сайтов параллельно"""
    results = {}
    
    def analyze_single(url):
        try:
            result = analyze_website(url, "quick")
            return url, result
        except Exception as e:
            return url, {"error": str(e)}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(analyze_single, url) for url in urls]
        
        for future in futures:
            url, result = future.result()
            results[url] = result
            time.sleep(1)  # Rate limiting
    
    return results

# Пример использования
urls = [
    "https://example1.com",
    "https://example2.com", 
    "https://example3.com"
]

results = analyze_multiple_sites(urls)
for url, result in results.items():
    print(f"\n{url}:")
    if "error" in result:
        print(f"  Ошибка: {result['error']}")
    else:
        classification = result.get("data", {}).get("analysis_results", {}).get("classification", {})
        print(f"  Тип: {classification.get('type', 'N/A')}")
        print(f"  Уверенность: {classification.get('confidence', 'N/A')}")
```

### 3. Интеграция с базой данных
```python
import sqlite3
import requests
from datetime import datetime

def save_analysis_to_db(url, analysis_result):
    """Сохранение результатов анализа в базу данных"""
    conn = sqlite3.connect('website_analyses.db')
    cursor = conn.cursor()
    
    # Создание таблицы если не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            analysis_type TEXT,
            classification_type TEXT,
            confidence REAL,
            summary TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # Извлечение данных
    data = analysis_result.get("data", {})
    analysis_results = data.get("analysis_results", {})
    classification = analysis_results.get("classification", {})
    summary = analysis_results.get("summary", {})
    
    # Сохранение
    cursor.execute('''
        INSERT INTO analyses (url, analysis_type, classification_type, confidence, summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        url,
        analysis_result.get("metadata", {}).get("analysis_type", "unknown"),
        classification.get("type", "unknown"),
        classification.get("confidence", 0.0),
        summary.get("summary", ""),
        datetime.now()
    ))
    
    conn.commit()
    conn.close()

# Пример использования
result = analyze_website("https://example.com")
save_analysis_to_db("https://example.com", result)
```

## 🌐 Веб-интерфейс примеры

### 1. Простой HTML интерфейс
```html
<!DOCTYPE html>
<html>
<head>
    <title>Website Analysis Tool</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .form-group { margin: 20px 0; }
        input[type="url"] { width: 400px; padding: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Website Analysis Tool</h1>
    
    <form id="analysisForm">
        <div class="form-group">
            <label for="url">Website URL:</label><br>
            <input type="url" id="url" placeholder="https://example.com" required>
        </div>
        
        <div class="form-group">
            <label for="analysisType">Analysis Type:</label><br>
            <select id="analysisType">
                <option value="quick">Quick Analysis</option>
                <option value="full">Full Analysis</option>
            </select>
        </div>
        
        <button type="submit">Analyze Website</button>
    </form>
    
    <div id="result" class="result" style="display: none;"></div>
    
    <script>
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('url').value;
            const analysisType = document.getElementById('analysisType').value;
            const resultDiv = document.getElementById('result');
            
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = 'Analyzing...';
            
            try {
                const response = await fetch('http://localhost:5000/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: url,
                        analysis_type: analysisType
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const results = data.data.analysis_results;
                    resultDiv.innerHTML = `
                        <h3>Analysis Results</h3>
                        <p><strong>Type:</strong> ${results.classification?.type || 'N/A'}</p>
                        <p><strong>Confidence:</strong> ${results.classification?.confidence || 'N/A'}</p>
                        <p><strong>Summary:</strong> ${results.summary?.summary || 'N/A'}</p>
                        <p><strong>Industry:</strong> ${results.classification?.industry || 'N/A'}</p>
                    `;
                } else {
                    resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
```

## 🔧 Конфигурация и настройка

### 1. Настройка агентов
```python
# В файле .env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
CREWAI_VERBOSE=true
CREWAI_MEMORY=true

# Настройка конкретных агентов
CLASSIFIER_AGENT_ENABLED=true
SUMMARY_AGENT_ENABLED=true
UX_REVIEWER_AGENT_ENABLED=true
DESIGN_ADVISOR_AGENT_ENABLED=true
```

### 2. Настройка скрапинга
```python
# В файле .env
SCRAPING_TIMEOUT=30
SCRAPING_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
SCRAPING_MAX_RETRIES=3
SCRAPING_DELAY_BETWEEN_REQUESTS=1
```

### 3. Настройка API
```python
# В файле .env
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
RATE_LIMIT_PER_MINUTE=60
API_KEY_REQUIRED=false
```

## 📊 Мониторинг и логирование

### 1. Просмотр логов
```bash
# Docker
docker-compose logs -f

# Локально
tail -f logs/multi_agent_system.log
```

### 2. Метрики производительности
```bash
# Health check
curl http://localhost:5000/health

# Статистика API
curl http://localhost:5000/stats
```

### 3. Мониторинг ресурсов
```bash
# Docker stats
docker stats

# Системные ресурсы
htop
```

## 🚨 Решение проблем

### 1. Ошибки API
```bash
# Проверка статуса
curl -v http://localhost:5000/health

# Проверка логов
docker-compose logs multi-agent
```

### 2. Проблемы с OpenAI API
```bash
# Проверка ключа
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### 3. Проблемы со скрапингом
```bash
# Тест скрапинга
python -c "
from multi_agent_system.tools.scraping_tools import scrape_website
result = scrape_website('https://example.com')
print(result)
"
```

---

*Эти примеры помогут вам быстро начать работу с Multi-Agent Website Analysis System и интегрировать её в ваши проекты.*
