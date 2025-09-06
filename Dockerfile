# Используем официальный Python образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY multi_agent_system/ ./multi_agent_system/
COPY requirements.txt .
COPY env.example .env

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем папку для логов
RUN mkdir -p logs

# Открываем порт
EXPOSE 5000

# Команда запуска
CMD ["python", "-m", "multi_agent_system.api.main"]
