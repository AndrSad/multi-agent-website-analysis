# 🚀 Инструкция по загрузке проекта на GitHub

## Вариант 1: Создание репозитория через веб-интерфейс GitHub

### Шаг 1: Создание репозитория на GitHub
1. Перейдите на https://github.com
2. Войдите в свой аккаунт
3. Нажмите зеленую кнопку "New" или "New repository"
4. Заполните форму:
   - **Repository name**: `multi-agent-website-analysis`
   - **Description**: `Multi-Agent Website Analysis System using CrewAI for automated website content analysis, UX review, and design recommendations`
   - **Visibility**: Public или Private (на ваш выбор)
   - **НЕ** ставьте галочки на "Add a README file", "Add .gitignore", "Choose a license" (у нас уже есть эти файлы)
5. Нажмите "Create repository"

### Шаг 2: Подключение локального репозитория
После создания репозитория GitHub покажет инструкции. Выполните следующие команды:

```bash
# Удалите текущий remote (если есть)
git remote remove origin

# Добавьте правильный remote (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/multi-agent-website-analysis.git

# Переименуйте ветку в main (если нужно)
git branch -M main

# Отправьте код
git push -u origin main
```

## Вариант 2: Загрузка через ZIP архив

Если у вас проблемы с Git, можете загрузить проект как ZIP архив:

### Шаг 1: Создание архива
```bash
# Создайте ZIP архив (уже создан)
# Файл: multi-agent-website-analysis.zip
```

### Шаг 2: Загрузка через GitHub
1. Создайте новый репозиторий на GitHub (как в Варианте 1)
2. Нажмите "uploading an existing file"
3. Перетащите ZIP архив или выберите файл
4. GitHub автоматически распакует архив

## Вариант 3: Использование GitHub Desktop

1. Скачайте GitHub Desktop: https://desktop.github.com/
2. Установите и войдите в свой аккаунт
3. Выберите "Add an Existing Repository from your hard drive"
4. Выберите папку проекта
5. Нажмите "Publish repository"

## Вариант 4: Использование VS Code

1. Откройте проект в VS Code
2. Установите расширение "GitHub Pull Requests and Issues"
3. Нажмите Ctrl+Shift+P
4. Выберите "Git: Publish to GitHub"
5. Следуйте инструкциям

## 🔧 Настройка после загрузки

### 1. Настройка переменных окружения
После создания репозитория:
1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте секрет `OPENAI_API_KEY` с вашим API ключом

### 2. Проверка GitHub Actions
1. Перейдите на вкладку "Actions" в репозитории
2. Убедитесь, что CI/CD pipeline запускается успешно

### 3. Настройка веток
1. Создайте ветку `develop` для разработки
2. Настройте защиту ветки `main`

## 📋 Что уже готово

✅ Git репозиторий инициализирован
✅ Первый коммит создан
✅ .gitignore настроен (исключает .env, venv, logs)
✅ GitHub Actions workflow создан
✅ Пример переменных окружения (env.example)
✅ Полная документация в README.md

## 🚨 Важные замечания

- Файл `.env` НЕ будет загружен (защищен .gitignore)
- Все секретные ключи должны быть в GitHub Secrets
- Проверьте, что все зависимости указаны в requirements.txt
- Убедитесь, что тесты проходят локально перед загрузкой

## 🆘 Если что-то не работает

1. Проверьте подключение к интернету
2. Убедитесь, что у вас есть права на создание репозиториев
3. Попробуйте другой браузер или очистите кэш
4. Используйте мобильный интернет как альтернативу
