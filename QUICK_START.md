# 🚀 Быстрый старт - Загрузка на GitHub

## Что уже готово ✅
- Git репозиторий инициализирован
- Первый коммит создан (bd68ce1)
- .gitignore настроен (исключает .env, venv, logs)
- GitHub Actions workflow готов
- Документация создана

## Следующие шаги:

### 1. Создайте репозиторий на GitHub
- Перейдите на https://github.com/new
- Название: `multi-agent-website-analysis`
- Описание: `Multi-Agent Website Analysis System using CrewAI`
- НЕ добавляйте README, .gitignore, лицензию (уже есть)

### 2. Подключите локальный репозиторий
```bash
# Удалите текущий remote
git remote remove origin

# Добавьте ваш репозиторий (замените YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/multi-agent-website-analysis.git

# Переименуйте ветку
git branch -M main

# Отправьте код
git push -u origin main
```

### 3. Настройте секреты
- Settings → Secrets and variables → Actions
- Добавьте `OPENAI_API_KEY`

## Альтернатива: ZIP загрузка
Если Git не работает, используйте файл `multi-agent-website-analysis.zip` для загрузки через веб-интерфейс GitHub.

## Проверка
После загрузки проверьте:
- [ ] Все файлы загружены
- [ ] GitHub Actions запускаются
- [ ] README отображается корректно
- [ ] .env файл НЕ виден (защищен .gitignore)
