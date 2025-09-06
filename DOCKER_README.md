# 🐳 Docker Setup для Multi-Agent Website Analysis System

## 🚀 Быстрый старт

### 1. Сборка и запуск
```bash
# Сборка образа
docker build -t multi-agent-analysis .

# Запуск контейнера
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key_here multi-agent-analysis
```

### 2. Использование Docker Compose
```bash
# Продакшн версия
docker-compose up --build

# Разработка (с hot reload)
docker-compose -f docker-compose.dev.yml up --build
```

## 🔧 Настройка

### Переменные окружения
Создайте файл `.env` в корне проекта:
```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=production
FLASK_DEBUG=false
```

### Порты
- **5000** - основной API сервер
- **8080** - веб-интерфейс (если настроен)

## 📊 Тестирование

### Health Check
```bash
curl http://localhost:5000/health
```

### Анализ сайта
```bash
# Быстрый анализ
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "analysis_type": "quick"}'

# Полный анализ
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "analysis_type": "full"}'
```

## 🐳 Docker Hub

### Загрузка на Docker Hub
```bash
# Логин
docker login

# Тегирование
docker tag multi-agent-analysis yourusername/multi-agent-analysis:latest

# Загрузка
docker push yourusername/multi-agent-analysis:latest
```

### Использование с Docker Hub
```bash
# Скачивание и запуск
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key yourusername/multi-agent-analysis:latest
```

## 🔍 Мониторинг

### Логи
```bash
# Просмотр логов
docker logs multi-agent-analysis

# Следить за логами в реальном времени
docker logs -f multi-agent-analysis
```

### Статистика
```bash
# Использование ресурсов
docker stats multi-agent-analysis
```

## 🛠️ Разработка

### Hot Reload (разработка)
```bash
# Запуск с монтированием кода
docker-compose -f docker-compose.dev.yml up --build
```

### Отладка
```bash
# Запуск с отладчиком
docker run -it --rm -p 5000:5000 -e OPENAI_API_KEY=your_key multi-agent-analysis bash
```

## 📁 Структура файлов

```
.
├── Dockerfile              # Основной Docker образ
├── docker-compose.yml      # Продакшн конфигурация
├── docker-compose.dev.yml  # Разработка конфигурация
├── .dockerignore           # Исключения для Docker
└── DOCKER_README.md        # Эта документация
```

## ⚠️ Важные замечания

1. **API ключ** - обязательно установите `OPENAI_API_KEY`
2. **Порты** - убедитесь, что порт 5000 свободен
3. **Логи** - сохраняются в папке `./logs`
4. **Память** - рекомендуется минимум 2GB RAM

## 🆘 Решение проблем

### Контейнер не запускается
```bash
# Проверьте логи
docker logs multi-agent-analysis

# Проверьте переменные окружения
docker exec multi-agent-analysis env
```

### Порт занят
```bash
# Используйте другой порт
docker run -p 8080:5000 -e OPENAI_API_KEY=your_key multi-agent-analysis
```

### Проблемы с зависимостями
```bash
# Пересоберите образ
docker build --no-cache -t multi-agent-analysis .
```
