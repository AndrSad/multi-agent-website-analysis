#!/bin/bash

# Multi-Agent Website Analysis System - Deployment Script

echo "🚀 Multi-Agent Website Analysis System - Deployment Script"
echo "=========================================================="

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Создаю из env.example..."
    cp env.example .env
    echo "📝 Отредактируйте .env файл и добавьте ваш OPENAI_API_KEY"
    echo "   Затем запустите скрипт снова."
    exit 1
fi

# Проверка наличия OPENAI_API_KEY
if ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
    echo "✅ .env файл настроен"
else
    echo "⚠️  Пожалуйста, установите ваш OPENAI_API_KEY в .env файле"
    exit 1
fi

echo "🔨 Сборка Docker образа..."
docker build -t multi-agent-analysis .

if [ $? -eq 0 ]; then
    echo "✅ Образ успешно собран"
else
    echo "❌ Ошибка при сборке образа"
    exit 1
fi

echo "🚀 Запуск контейнера..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Контейнер запущен"
    echo ""
    echo "🌐 Сервис доступен по адресу: http://localhost:5000"
    echo "📊 Health check: http://localhost:5000/health"
    echo "📖 API документация: http://localhost:5000/docs"
    echo ""
    echo "📋 Полезные команды:"
    echo "   docker-compose logs -f    # Просмотр логов"
    echo "   docker-compose down       # Остановка сервиса"
    echo "   docker-compose restart    # Перезапуск сервиса"
else
    echo "❌ Ошибка при запуске контейнера"
    exit 1
fi
