# Multi-Agent Website Analysis System

## Установка и запуск

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

## Тесты
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

## CI/CD
GitHub Actions запускает тесты и проверку покрытия (>=80%).


