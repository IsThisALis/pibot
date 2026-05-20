#!/bin/bash
echo "Запуск установки Пибота"
echo "Нажмите ctrl+C для отмены"
echo "------------------------------------------------"

sleep 3

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1

echo "\n Копирование файлов конфигурации..."

cp ./bot-data/public-phrases.json ./bot-data/phrases.json
cp ./bot-data/public-superusers.json ./bot-data/superusers.json
cp ./info/public-botinfo.md ./info/botinfo.md

echo "\n Создание файлов с ключами... \n"

echo "YOUR-TELEGRAM-TOKEN" > ./info/telegram-token
echo "YOUR-GEMINI-API-KEY-HERE" > ./info/gemini-key
echo "YOUR-GROQ-API-KEY-HERE" > ./info/groq-key

echo "------------------------------------------------"
echo "\n [WARNING]: Впишите id суперюзеров в файл bot-data/superusers.json!"
echo "\n [WARNING]: Вставьте токен бота в info/telegram-token (получить у BotFather)"
echo "\n [WARNING]: Вставьте API ключ в info/gemini-key или info/groq-key"
echo "\n Вы можете настроить свои фразы в bot-data/phrases.json"
echo "\n Отредактируйте info/botinfo.md чтобы изменить сообщение о боте \n"
echo "------------------------------------------------"

sleep 3

chmod +x ./launchbot.sh

echo "\n Установка зависимостей... \n"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
.venv/bin/pip install -r requirements.txt

echo "------------------------------------------------"
echo "\n Установка завершена! Запустите бота: ./launchbot.sh \n"
echo "------------------------------------------------"
