# Telegram Media Downloader Bot

Простой Telegram-бот на Python, aiogram и yt-dlp. Бот принимает публичную ссылку, скачивает фото или видео во временную папку, отправляет файл пользователю и удаляет его с сервера.

Бот не обходит авторизацию, не скачивает приватные аккаунты и не предназначен для закрытого контента.

## Что поддерживается

yt-dlp поддерживает тысячи сайтов, включая TikTok, Instagram, YouTube Shorts, X/Twitter, VK и многие другие. Если конкретный сайт изменил защиту или не поддерживается yt-dlp, бот покажет ошибку.

По умолчанию бот не отправляет файлы больше `49` МБ. Значение можно изменить через `MAX_FILE_SIZE_MB`, но Telegram и хостинг всё равно могут иметь собственные ограничения.

## Файлы проекта

- `bot.py` - весь код бота
- `requirements.txt` - зависимости Python
- `.env.example` - пример переменных окружения
- `Procfile` - команда запуска для платформ, которые читают Procfile
- `runtime.txt` - версия Python
- `.gitignore` - исключает `.env`, виртуальное окружение и временные файлы

## Запуск на Windows

1. Установите Python 3.12.
2. Создайте бота через [@BotFather](https://t.me/BotFather) и получите токен.
3. Откройте PowerShell в папке проекта.
4. Создайте виртуальное окружение:

```powershell
python -m venv .venv
```

5. Активируйте его:

```powershell
.\.venv\Scripts\Activate.ps1
```

6. Установите зависимости:

```powershell
pip install -r requirements.txt
```

7. Создайте `.env` из примера:

```powershell
copy .env.example .env
```

8. Откройте `.env` и вставьте токен:

```env
BOT_TOKEN=ваш_токен_от_BotFather
MAX_FILE_SIZE_MB=49
```

9. Запустите бота:

```powershell
python bot.py
```

## Как загрузить код на GitHub

1. Создайте новый пустой репозиторий на [GitHub](https://github.com/new).
2. В PowerShell внутри папки проекта выполните:

```powershell
git init
git add .
git commit -m "Initial bot"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

3. Замените `USERNAME` и `REPOSITORY` на свои значения.

Не загружайте настоящий `.env` в GitHub. На сервере токен добавляется через переменные окружения.

## Деплой на Render 24/7

Для polling-бота лучше использовать Render Background Worker, потому что обычный Web Service ожидает HTTP-сервер.

1. Зарегистрируйтесь или войдите в [Render](https://render.com/).
2. Нажмите `New` и выберите `Background Worker`.
3. Подключите GitHub и выберите репозиторий с ботом.
4. Укажите настройки:

- Runtime: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python bot.py`

5. В разделе `Environment Variables` добавьте:

```env
BOT_TOKEN=ваш_токен_от_BotFather
MAX_FILE_SIZE_MB=49
```

6. Нажмите `Deploy`.
7. После успешного запуска откройте Telegram и отправьте боту публичную ссылку.

Для работы 24/7 выберите тариф Render, который не останавливает worker. Если сервис остановлен или спит, polling-бот не получает новые сообщения.

## Railway или Fly.io

Через Railway процесс похожий: создайте проект из GitHub-репозитория, добавьте `BOT_TOKEN` в Variables и укажите команду запуска `python bot.py`.

Для Fly.io обычно нужен Dockerfile или отдельная настройка приложения. Этот проект без Docker готов в первую очередь для Render и Railway.

## Полезно знать

- Если сайт перестал скачиваться, обновите yt-dlp:

```powershell
pip install -U yt-dlp
```

- Если ссылка ведёт на приватный пост, закрытый аккаунт или требует входа, бот не будет её скачивать.
- Если файл слишком большой, уменьшите качество на стороне источника или используйте ссылку на меньший файл.

## Ссылки

- [aiogram long polling](https://docs.aiogram.dev/en/latest/dispatcher/long_polling.html)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Render deploys](https://render.com/docs/deploys)
- [Render environment variables](https://render.com/docs/configure-environment-variables)
