# Pibot — Telegram Chat Bot

Многофункциональный Telegram-бот с фразовыми ответами, RP-командами, AI-интеграцией и модерацией.

## Возможности

- **Фразовые ответы** — автоматически отвечает на триггер-фразы из `phrases.json`
- **RP-команды** — интерактивный ролеплей (обнять, поцеловать и т.д.) через ответ на сообщение
- **AI-интеграция** — отвечает с контекстом при @упоминании бота в ответе (Gemini или Groq)
- **Админ-команды** — `$nuke`, `$mute`, `$unmute`
- **Суперюзер-команды** — `$kick`, `$ban`, `$changeai`
- **Антиспам** — rate limiter, age filter, защита от спама триггер-фразами, Telegram-мут

## Структура

```
pibot/
├── bot-data/         # JSON-файлы данных (phrases, synonyms, rp-commands)
├── env/              # Файлы конфигов (gitignored: .env, botinfo.txt, changelog.txt)
├── info/             # Документация
├── source/pibot.py    # Основной код бота (~900 строк)
└── setup.sh          # Скрипт развёртывания
```

## Установка

1. Скопировать репозиторий на сервер
2. Создать `env/.env` с `BOT_TOKEN`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `GROQ_BASE_URL`, `SUPERUSER_IDS`
3. Опционально настроить `env/botinfo.txt` и `env/changelog.txt`
4. Запустить `bash setup.sh` для установки systemd-сервиса или запустить вручную

## Команды

Полный список в `info/command-list.md` или по фразе `пибот команды` в чате.

## Зависимости

- python-telegram-bot (v20+)
- google-genai
- openai (AsyncOpenAI)
