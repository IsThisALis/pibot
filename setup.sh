#!/bin/bash
echo "Запуск установки Пибота"
echo "Нажмите ctrl+C для отмены"
echo "------------------------------------------------"

sleep 3

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1

echo "Копирование файлов конфигурации..."

cp ./datafiles/public-phrases.json ./datafiles/phrases.json
cp ./datafiles/public-superusers.json ./datafiles/superusers.json
cp ./dev/public-botinfo.md ./dev/botinfo.md
cp ./dev/personality-public.md ./dev/personality.md

echo "Создание файлов с ключами..."

echo "TOKEN-WILL-BE-HERE-LATER" >./dev/telegram-token
echo "YOUR_GEMINI_API_KEY_HERE" >./dev/gemini-key
echo "gsk_YOUR_GROQ_API_KEY_HERE" >./dev/llm-key

echo "------------------------------------------------"
echo "[WARNING]: Впишите id суперюзеров в файл datafiles/superusers.json!"
echo "[WARNING]: Вставьте токен бота в dev/telegram-token (получить у BotFather)"
echo "[WARNING]: Вставьте API ключ в dev/gemini-key или dev/llm-key"
echo "Вы можете настроить свои фразы в datafiles/phrases.json"
echo "Отредактируйте dev/botinfo.md чтобы изменить сообщение о боте"
echo "------------------------------------------------"

sleep 3

chmod +x ./launchbot.sh

echo "Установка зависимостей..."

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
.venv/bin/pip install -r requirements.txt

echo "------------------------------------------------"
echo "Установка завершена! Запустите бота: ./launchbot.sh"
echo "------------------------------------------------"
