# Multi-Agent Website Analysis System

Система мультиагентного анализа веб-сайтов, использующая CrewAI для координации работы специализированных агентов.

## 🚀 Возможности

- **Классификация контента**: Анализ и категоризация контента веб-сайта
- **Создание резюме**: Комплексные резюме контента веб-сайта
- **UX-анализ**: Оценка пользовательского опыта и удобства использования
- **Дизайн-консультации**: Рекомендации по улучшению дизайна
- **Веб-скрапинг**: Извлечение данных с веб-сайтов
- **REST API**: Простой API для интеграции с другими системами

## 🏗️ Архитектура

```
multi_agent_system/
├── agents/                 # Специализированные агенты
│   ├── classifier_agent.py      # Классификация контента
│   ├── summary_agent.py         # Создание резюме
│   ├── ux_reviewer_agent.py     # UX-анализ
│   └── design_advisor_agent.py  # Дизайн-консультации
├── tools/                  # Инструменты
│   └── scraping_tools.py        # Веб-скрапинг
├── core/                   # Основные компоненты
│   ├── config.py               # Конфигурация
│   └── orchestrator.py         # Оркестратор агентов
├── api/                    # REST API
│   └── main.py                 # Flask приложение
├── requirements.txt        # Зависимости Python
├── env.example            # Пример переменных окружения
└── README.md              # Документация
```

## 📋 Требования

- Python 3.10+
- OpenAI API ключ
- Виртуальное окружение (рекомендуется)

## 🛠️ Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone <repository-url>
   cd multi_agent_system
   ```

2. **Создайте виртуальное окружение**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения**:
   ```bash
   cp env.example .env
   # Отредактируйте .env файл и добавьте ваш OPENAI_API_KEY
   ```

## ⚙️ Конфигурация

Создайте файл `.env` на основе `env.example`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# CrewAI Configuration
CREWAI_VERBOSE=true
CREWAI_MEMORY=true

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Web Scraping Configuration
SCRAPING_TIMEOUT=30
SCRAPING_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

## 🚀 Использование

### Запуск API сервера

```bash
python -m api.main
```

Сервер будет доступен по адресу: `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

#### 2. Полный анализ веб-сайта
```bash
POST /analyze
Content-Type: application/json

{
    "url": "https://example.com",
    "analysis_type": "full"
}
```

#### 3. Быстрый анализ
```bash
POST /analyze
Content-Type: application/json

{
    "url": "https://example.com",
    "analysis_type": "quick"
}
```

#### 4. Только скрапинг
```bash
POST /scrape
Content-Type: application/json

{
    "url": "https://example.com"
}
```

#### 5. Получение конфигурации
```bash
GET /config
```

### Пример использования с curl

```bash
# Полный анализ
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "analysis_type": "full"}'

# Быстрый анализ
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "analysis_type": "quick"}'
```

### Использование в Python коде

```python
from core.orchestrator import MultiAgentOrchestrator

# Инициализация оркестратора
orchestrator = MultiAgentOrchestrator()

# Полный анализ
result = orchestrator.analyze_website("https://example.com")

# Быстрый анализ
quick_result = orchestrator.get_quick_analysis("https://example.com")

# Только скрапинг
website_data = orchestrator.scraping_tool.scrape_website("https://example.com")
```

## 🤖 Агенты

### 1. ClassifierAgent
- **Роль**: Классификатор контента веб-сайта
- **Функции**: Анализ индустрии, типа контента, целевой аудитории, бизнес-модели
- **Выходные данные**: Структурированная классификация с оценками

### 2. SummaryAgent
- **Роль**: Создатель резюме контента
- **Функции**: Извлечение ключевой информации, анализ структуры контента
- **Выходные данные**: Комплексное резюме с основными разделами

### 3. UXReviewerAgent
- **Роль**: UX/UI рецензент
- **Функции**: Оценка удобства использования, навигации, доступности
- **Выходные данные**: UX-анализ с рекомендациями по улучшению

### 4. DesignAdvisorAgent
- **Роль**: Дизайн-консультант
- **Функции**: Оценка визуального дизайна, брендинга, типографики
- **Выходные данные**: Рекомендации по дизайну с конкретными предложениями

## 🛠️ Инструменты

### WebScrapingTool
- Извлечение HTML контента
- Анализ метаданных
- Сбор ссылок и изображений
- Анализ форм и кнопок
- Извлечение цветов и шрифтов
- Расчет метрик производительности

## 📊 Структура данных

### Результат анализа веб-сайта
```json
{
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
        "classification": "...",
        "summary": "...",
        "ux_review": "...",
        "design_advice": "..."
    },
    "status": "completed",
    "timestamp": 1234567890
}
```

## 🔧 Разработка

### Установка зависимостей для разработки
```bash
pip install -r requirements.txt
```

### Запуск тестов
```bash
pytest
```

### Форматирование кода
```bash
black .
flake8 .
```

## 📝 Логирование

Система использует стандартный модуль logging Python. Уровень логирования настраивается через переменную окружения `LOG_LEVEL`.

## 🚨 Ограничения

- Требуется OpenAI API ключ
- Скрапинг может быть ограничен robots.txt и rate limiting
- Некоторые сайты могут блокировать автоматические запросы
- Анализ больших сайтов может занять значительное время

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 🆘 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте документацию
2. Поищите в Issues
3. Создайте новый Issue с подробным описанием проблемы

## 🔄 Обновления

### v1.0.0
- Первоначальный релиз
- Базовые агенты для анализа веб-сайтов
- REST API
- Веб-скрапинг инструменты
