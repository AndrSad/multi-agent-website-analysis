@echo off
REM Multi-Agent Website Analysis System - Deployment Script for Windows

echo 🚀 Multi-Agent Website Analysis System - Deployment Script
echo ==========================================================

REM Проверка наличия Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не установлен. Установите Docker и попробуйте снова.
    pause
    exit /b 1
)

REM Проверка наличия Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова.
    pause
    exit /b 1
)

REM Проверка наличия .env файла
if not exist .env (
    echo ⚠️  Файл .env не найден. Создаю из env.example...
    copy env.example .env
    echo 📝 Отредактируйте .env файл и добавьте ваш OPENAI_API_KEY
    echo    Затем запустите скрипт снова.
    pause
    exit /b 1
)

echo 🔨 Сборка Docker образа...
docker build -t multi-agent-analysis .

if %errorlevel% neq 0 (
    echo ❌ Ошибка при сборке образа
    pause
    exit /b 1
)

echo ✅ Образ успешно собран

echo 🚀 Запуск контейнера...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Ошибка при запуске контейнера
    pause
    exit /b 1
)

echo ✅ Контейнер запущен
echo.
echo 🌐 Сервис доступен по адресу: http://localhost:5000
echo 📊 Health check: http://localhost:5000/health
echo 📖 API документация: http://localhost:5000/docs
echo.
echo 📋 Полезные команды:
echo    docker-compose logs -f    # Просмотр логов
echo    docker-compose down       # Остановка сервиса
echo    docker-compose restart    # Перезапуск сервиса
echo.
pause
