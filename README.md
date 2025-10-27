# Tg-Je-Bot
# This repository will contain my telegram bots. I call them Je_Bot.


# 1. Linux Terminal File Telegram Je Bot
Простой Telegram-бот для управления MacOS/Linux/OrangePi... через чат.  
Позволяет:
- Выполнять команды терминала (`/ls`, `/python3 script.py` и т.д.)
- Загружать файлы с устройства (`/get filename`)
- Принимать файлы от пользователя и сохранять в указанную папку
- Удобно положить файл в корневую папку и пользоваться потчти как терминалом
- Удобно отправить файл который можно сразу открыть
- Удобно добавить файл в автоматический запуск вместе с системой

## Установка
1️⃣ Клонируем файл с GitHub
```
cd /      # переходим в корневую папку, если именно туда нужно  
wget https://raw.githubusercontent.com/SalnikovEV/Tg-Je-Bot/main/Linux_Terminal_File_Telegram_Je_Bot.py
```

2️⃣ Настройка токена и chat_id
Открой файл в редакторе:
```
nano Linux_Terminal_File_Telegram_Je_Bot.py
```

Найди строки с настройками бота:
```
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
```

`YOUR_BOT_TOKEN` — вставь сюда токен твоего бота, который дал @BotFather  
`YOUR_CHAT_ID` — вставь сюда свой личный chat_id (можно узнать через @userinfobot)  
Сохрани изменения: Ctrl+O → Enter, затем Ctrl+X чтобы выйти из nano.

3️⃣ Запуск бота
В терминале, находясь в той же папке:  
```
python3 Linux_Terminal_File_Telegram_Je_Bot.py
```
Бот запустится и отправит приветственное сообщение в Telegram, если соединение с интернетом есть.


## Автозапуск 
Инструкция, как настроить автозапуск твоего бота на Linux, чтобы он автоматически запускался при старте системы.  

1️⃣ Создаём unit-файл systemd  
Создаем файл сервиса:
```
sudo nano /etc/systemd/system/tg_bot.service
```

Вставь туда:
```
[Unit]
Description=Telegram Terminal & File Bot
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/!!!user!!!/Linux_Terminal_File_Telegram_Je_Bot.py
Restart=on-failure
User=!!!!
WorkingDirectory=/home/ev-ora
StandardOutput=inherit
StandardError=inherit

[Install]
WantedBy=multi-user.target
```

⚠️ Обрати внимание:  
`User=____` — это пользователь Linux, от которого будет запускаться бот (Это то что пред @ d терминале )  
`ExecStart`— полный путь до скрипта. В примере у меня так, работает на Ubuntu (если затык -> то GPT)  

Сохрани: Ctrl+O, Enter → Ctrl+X.  

2️⃣ Активируем сервис  
```
sudo systemctl daemon-reload
sudo systemctl enable tg_bot.service
sudo systemctl start tg_bot.service
```

3️⃣ Проверяем статус
```
sudo systemctl status tg_bot.service
```

Если всё ок, статус будет active (running)  
Если есть ошибки — система покажет их в логах, можно исправить путь или права на файл.  

4️⃣ Поведение  
Бот автоматически запускается после старта Linux
Если интернет ещё не подключён, бот будет ожидать подключения.  
В случае падения бота, systemd перезапустит его автоматически.  

