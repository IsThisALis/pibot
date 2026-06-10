# Pibot — Telegram Chat Bot

Многофункциональный Telegram-бот с фразовыми ответами, RP-командами, AI-интеграцией (Groq Llama) и модерацией.

## Возможности

- **Фразовые ответы** — автоматически отвечает на триггер-фразы из `phrases.json`
- **RP-команды** — интерактивный ролеплей (обнять, поцеловать и т.д.) через ответ на сообщение
- **AI-интеграция** — отвечает с контекстом при @упоминании бота (Groq Llama 3.3 70B через OpenAI SDK)
- **Админ-команды** — `сотри`, `мут`, `размут`
- **Суперюзер-команды** — `кикни`, `кинь`, `заблокируй`
- **Антиспам** — rate limiter, age filter, защита от спама триггер-фразами, Telegram-мут
- **Ранговая система** — 4 уровня доступа (Owner, Admin+, Admin, Member)

## Структура

```
pibot/
├── bot-data/         # JSON/MD файлы данных (phrases, rp-commands, personality)
├── env/              # Файлы конфигов (gitignored: токены, ключи, ID разработчиков)
├── info/             # Документация и справка
├── important/        # Настройка логирования и утилиты (gitignored)
├── source/
│   ├── pibot.py      # Основной код бота (класс, ~1120 строк)
│   └── persistence.py # SQLite persistence
├── setup.sh          # Скрипт развёртывания
└── launchbot.sh      # Скрипт запуска
```

## Установка

1. Скопировать репозиторий на сервер
2. Запустить `bash setup.sh` — создаст файлы конфигов, venz и установит зависимости
3. Вставить токен бота в `env/telegram-token` (получить у BotFather)
4. Вставить Groq API ключ в `env/groq-key`
5. Опционально настроить `bot-data/personality.md` и `bot-data/botinfo.md`
6. Запустить `./launchbot.sh`

## Команды

Полный список в `info/command-list.md` или по фразе `пибот команды` в чате.

## Зависимости

- python-telegram-bot (v22+, с job-queue)
- openai (AsyncOpenAI для Groq API)
