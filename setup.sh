#!/bin/bash
echo "Запуск установки Пибота"
echo "Нажмите ctrl+C для отмены"
echo "------------------------------------------------ \n"

sleep 3

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1

echo "Копирование файлов конфигурации... \n"

cp ./bot-data/public-phrases.json ./bot-data/phrases.json
cp ./bot-data/public-botinfo.md ./bot-data/botinfo.md
touch ./bot-data/banned-users.json
touch ./bot-data/personality.md

# Надо наполнить персоналити мд каким-нибудь шаблоном хз
# Да и в целом файлы пофиксить

echo "Создание файлов с ключами... \n"

mkdir ./env/
touch ./env/telegram-token ./env/groq-key ./env/dev-ids.json

echo "YOUR-TELEGRAM-TOKEN" > ./env/telegram-token
echo "YOUR-GROQ-API-KEY-HERE" > ./env/groq-key

echo "------------------------------------------------ \n"
echo "[WARNING]: Вставьте токен бота в env/telegram-token (получить у BotFather) \n"
echo "[WARNING]: Вставьте API ключ в env/groq-key \n"
echo "Вы можете настроить свои фразы в bot-data/phrases.json \n"
echo "Отредактируйте info/botinfo.md чтобы изменить сообщение о боте \n"
echo "------------------------------------------------ \n \n"

sleep 3

chmod +x ./launchbot.sh

echo "Установка зависимостей... \n"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
.venv/bin/pip install -r requirements.txt

echo "------------------------------------------------ \n"
echo "Установка завершена! Запустите бота: ./launchbot.sh \n"
echo "------------------------------------------------"
