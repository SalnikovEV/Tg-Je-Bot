#TG Bot for Linux terminal and file download
#by Salnikov_EV

#желательно поместить в корневую папку
#запускает команды через subprocess()

import requests
import time
import subprocess
import os

# === Настройки ===
BOT_TOKEN = ""                                         # надо создать бота в @BotFather
CHAT_ID = ""                                           # можно узнать, написав боту @userinfobot
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
DOWNLOAD_DIR = "py_d"                                  # куда сохранять файлы
SUDO_PASSWORD = "твой_пароль_для_sudo"                 # будб аккуратен!!!


# === Создаём папку, если нет ===
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === Отправка текстового сообщения ===
def send_message(text):
    try:
        requests.post(API_URL + "sendMessage", data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Ошибка отправки:", e)

# === Получение апдейтов ===
def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    try:
        resp = requests.get(API_URL + "getUpdates", params=params, timeout=60)
        return resp.json()
    except Exception as e:
        print("Ошибка получения апдейтов:", e)
        return {}

# === Скачивание файла ===
def download_file(file_id, file_name):
    # 1. Получаем путь файла на серверах Telegram
    resp = requests.get(API_URL + "getFile", params={"file_id": file_id})
    data = resp.json()
    if not data.get("ok"):
        send_message("❌ Не удалось получить информацию о файле.")
        return

    file_path = data["result"]["file_path"]
    local_path = os.path.join(DOWNLOAD_DIR, file_name)

    # 2. Скачиваем сам файл
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    file_data = requests.get(file_url)

    with open(local_path, "wb") as f:
        f.write(file_data.content)

    send_message(f"📥 Файл сохранён:\n{local_path}")

# === Выполнение команды ===
def run_command(cmd):
    try:
        if cmd.startswith("sudo "):
            cmd = cmd.replace("sudo ", "", 1)
            full_cmd = f"echo {SUDO_PASSWORD} | sudo -S {cmd}"
        else:
            full_cmd = cmd

        output = subprocess.check_output(
            full_cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30
        )

        if not output.strip():
            output = "(Команда выполнена, но без вывода)"
        return output

    except subprocess.CalledProcessError as e:
        return f"Ошибка выполнения:\n{e.output}"
    except subprocess.TimeoutExpired:
        return "⏰ Время выполнения команды истекло."

# === Основной цикл ===
def main():
    send_message("🤖 Бот запущен и готов принимать команды ✅")

    # --- очищаем все старые апдейты, чтобы не выполнять старые команды ---
    updates = get_updates()
    if "result" in updates and updates["result"]:
        last_update_id = updates["result"][-1]["update_id"] + 1
    else:
        last_update_id = None
    # ----------------------------------------------------------------------

    while True:
        updates = get_updates(last_update_id)
        if "result" in updates:
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")

                if str(chat_id) != str(CHAT_ID):
                    send_message("⛔️ У вас нет доступа.")
                    continue

                # === Если пришёл файл ===
                if "document" in message:
                    file_id = message["document"]["file_id"]
                    file_name = message["document"]["file_name"]
                    send_message(f"📦 Получен файл: {file_name}\n⏳ Сохраняю...")
                    download_file(file_id, file_name)
                    continue

                # === Если пришло текстовое сообщение ===
                text = message.get("text", "")
                if not text:
                    continue
                    
                if text.startswith("/"):
                    cmd = text[1:].strip()
                    send_message(f"▶ Выполняю: `{cmd}`")
                    output = run_command(cmd)
                    if len(output) > 4000:
                        output = output[:4000] + "\n...(обрезано)"
                    send_message(f"🖥 Результат:\n{output}")

        time.sleep(2)
if __name__ == "__main__":
    main()
