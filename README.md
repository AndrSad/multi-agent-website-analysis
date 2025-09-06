# 🤖 Multi-Agent Website Analysis System

> Интеллектуальная система анализа веб-сайтов с командой специализированных ИИ-агентов

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://github.com/AndrSad/multi-agent-website-analysis/workflows/Minimal%20CI/badge.svg)](https://github.com/AndrSad/multi-agent-website-analysis/actions)

## 🎯 Что это такое?

**Multi-Agent Website Analysis System** - это мощная система анализа веб-сайтов, использующая команду специализированных ИИ-агентов для комплексной оценки и предоставления профессиональных рекомендаций по улучшению веб-ресурсов.

### 🚀 Основные возможности

- **🎯 Классификация контента** - Автоматическое определение типа сайта, отрасли, целевой аудитории
- **📝 Создание резюме** - Интеллектуальное извлечение ключевой информации и создание структурированных резюме
- **🎨 UX-анализ** - Профессиональная оценка пользовательского опыта, навигации и доступности
- **💡 Дизайн-консультации** - Экспертные рекомендации по улучшению визуального дизайна и брендинга
- **🌐 Веб-скрапинг** - Извлечение и анализ данных с веб-сайтов
- **🔌 REST API** - Простой API для интеграции с другими системами
- **🐳 Docker** - Готовая контейнеризация для быстрого развертывания

### 🤖 Специализированные агенты

| Агент | Функция | Описание |
|-------|---------|----------|
| **Classifier** | Классификация | Определяет тип сайта, отрасль, целевую аудиторию |
| **Summary** | Резюме | Создает структурированные резюме контента |
| **UX Reviewer** | UX-анализ | Оценивает удобство использования и навигацию |
| **Design Advisor** | Дизайн | Дает рекомендации по визуальному дизайну |

## 📚 Документация

- **[Подробное описание возможностей](FEATURES.md)** - Детальное описание всех функций системы
- **[Примеры использования](EXAMPLES.md)** - Практические примеры и код
- **[Docker документация](DOCKER_README.md)** - Настройка и развертывание через Docker

## 🛠️ Установка и запуск

1. Python 3.10+, Windows PowerShell:
```
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r multi_agent_system/requirements.txt
```
2. Настройте `.env` в корне:
```
OPENAI_API_KEY=your_key
OPENAI_API_BASE=https://your-proxy/v1  # опционально
SCRAPING_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36
```
3. Запуск:
```
python -m multi_agent_system.api.main
```
UI: `http://127.0.0.1:5000/ui`

## 🚀 Быстрые примеры

### Анализ веб-сайта через API
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

### Python интеграция
```python
import requests

# Анализ сайта
response = requests.post('http://localhost:5000/analyze', json={
    'url': 'https://example.com',
    'analysis_type': 'full'
})

result = response.json()
print(f"Тип сайта: {result['data']['analysis_results']['classification']['type']}")
print(f"Резюме: {result['data']['analysis_results']['summary']['summary']}")
```

### Веб-интерфейс
Откройте `http://localhost:5000/ui` в браузере для интерактивного анализа.

## 🧪 Тесты
```
pytest -q
```
Нагрузочное тестирование (k6):
```
k6 run k6/load_test.js
```

## 🐳 Docker

### Быстрый запуск
```bash
# Сборка и запуск
docker build -t multi-agent-analysis .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key multi-agent-analysis

# Или через Docker Compose
docker-compose up --build
```

### Docker Hub
```bash
# Скачать готовый образ
docker pull yourusername/multi-agent-analysis:latest
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key yourusername/multi-agent-analysis:latest
```

Подробная документация: [DOCKER_README.md](DOCKER_README.md)

## 🎯 Применение

### Для веб-разработчиков
- Аудит существующих сайтов
- Получение рекомендаций по улучшению
- Анализ конкурентов
- Проверка UX/UI решений

### Для маркетологов
- Анализ эффективности лендингов
- Оценка контентной стратегии
- Исследование целевой аудитории
- Оптимизация конверсии

### Для дизайнеров
- Получение профессиональных рекомендаций
- Анализ трендов в дизайне
- Оценка доступности
- Улучшение пользовательского опыта

### Для владельцев бизнеса
- Комплексная оценка веб-присутствия
- Выявление проблем и возможностей
- Планирование улучшений
- ROI анализ веб-инвестиций

## 🔧 CI/CD
GitHub Actions запускает тесты и проверку покрытия (>=80%).


