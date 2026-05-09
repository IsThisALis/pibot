#!/bin/bash
echo "Запуск установки Пибота"
echo "Нажмите ctrl+C для отмены"
echo "------------------------------------------------"

sleep 5

echo "Установка"

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1

cp ./datafiles/public-phrases.json ./datafiles/phrases.json
cp ./datafiles/public-superusers.json ./datafiles/superusers.json
cp ./dev/public-botinfo.md ./dev/botinfo.md
echo "------------------------------------------------"
sleep 3

echo "------------------------------------------------"
echo "[WARNING]: Впишите id суперюзеров в файл superusers.json! Иначе некоторые команды не будут работать."
echo "Вы можете настроить свои фразы в phrases.json"
echo "Отредактируйте dev/botinfo.md чтобы изменить сообщение о боте"
echo "------------------------------------------------"

sleep 5

chmod +x ./launchbot.sh

echo "------------------------------------------------"
echo "Впишите id суперюзеров в файл superusers.json и запустите бота файлом ./launchbot.sh"
echo "------------------------------------------------"
