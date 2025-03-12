#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
РОЗСИЛКА ПОВІДОМЛЕНЬ TELEGRAM ДЛЯ УКРАЇНСЬКИХ КОРИСТУВАЧІВ
=========================================================

Спеціальний інструмент для відправки повідомлень українським користувачам Telegram.
Підтримує відправку за номерами телефону та нікнеймами.

ВИКОРИСТАННЯ:
   python main.py

Програма має графічний інтерфейс для легкої взаємодії.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
from datetime import datetime

# Імпортуємо клас відправника
from ua_telegram_sender.sender import UkrainianTelegramSender

# Константи
CONFIG_FILE = "config.json"
DEFAULT_RECIPIENTS_FILE = "recipients.txt"
LOG_FILE = "sending_log.txt"

# Значення за замовчуванням
DEFAULT_CONFIG = {
    "api_id": 1079592,
    "api_hash": "4b3c8eeb47a62ecc941e61907f1a7bf0",
    "session_name": "ua_session",
    "delay": 2.0,
    "last_phone": ""
}

class TelegramSenderApp:
    """Головний клас програми з графічним інтерфейсом"""
    
    def __init__(self, root):
        """Ініціалізація програми"""
        self.root = root
        self.root.title("Telegram Розсилка для України")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Змінні
        self.phone_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.code_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.delay_var = tk.DoubleVar(value=2.0)
        self.status_var = tk.StringVar(value="Готовий до роботи")
        
        # Завантажуємо конфігурацію
        self.config = self.load_config()
        
        # Ініціалізуємо відправника
        self.sender = UkrainianTelegramSender(
            api_id=self.config["api_id"],
            api_hash=self.config["api_hash"],
            session_name=self.config["session_name"]
        )
        
        # Заповнюємо значення за замовчуванням
        self.delay_var.set(self.config["delay"])
        if self.config["last_phone"]:
            self.phone_var.set(self.config["last_phone"])
        
        # Створюємо інтерфейс
        self.create_widgets()
        
        # Перевіряємо наявність файлу одержувачів
        if not os.path.exists(DEFAULT_RECIPIENTS_FILE):
            with open(DEFAULT_RECIPIENTS_FILE, "w", encoding="utf-8") as f:
                f.write("# Список одержувачів (по одному на рядок)\n")
                f.write("# Можна використовувати @username або телефон у форматі +380xxxxxxxxx\n\n")
                f.write("@username1\n")
                f.write("@username2\n")
                f.write("+380xxxxxxxxx\n")
        
        # Перевіряємо авторизацію
        self.check_authorization()
        
    def load_config(self):
        """Завантаження конфігурації з файлу"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Перевіряємо наявність всіх необхідних полів
                    for key, value in DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка завантаження конфігурації: {e}")
                return DEFAULT_CONFIG
        else:
            return DEFAULT_CONFIG
            
    def save_config(self):
        """Збереження конфігурації у файл"""
        # Оновлюємо значення
        self.config["delay"] = self.delay_var.get()
        self.config["last_phone"] = self.phone_var.get()
        
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти конфігурацію: {e}")
    
    def create_widgets(self):
        """Створення елементів інтерфейсу"""
        # Основний контейнер
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Область авторизації
        auth_frame = ttk.LabelFrame(main_frame, text="Авторизація", padding=10)
        auth_frame.pack(fill=tk.X, pady=5)
        
        # Телефон
        ttk.Label(auth_frame, text="Номер телефону:").grid(row=0, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(auth_frame, textvariable=self.phone_var, width=30)
        phone_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Label(auth_frame, text="(з '+', наприклад +380xxxxxxxxx)").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        
        # Код підтвердження
        ttk.Label(auth_frame, text="Код підтвердження:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(auth_frame, textvariable=self.code_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Пароль 2FA
        ttk.Label(auth_frame, text="Пароль 2FA (якщо є):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(auth_frame, textvariable=self.password_var, show="*", width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Кнопки авторизації
        auth_btn_frame = ttk.Frame(auth_frame)
        auth_btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(auth_btn_frame, text="Запит коду", command=self.request_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(auth_btn_frame, text="Увійти", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(auth_btn_frame, text="Перевірити статус", command=self.check_authorization).pack(side=tk.LEFT, padx=5)
        
        # Область повідомлення
        message_frame = ttk.LabelFrame(main_frame, text="Повідомлення", padding=10)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Затримка між повідомленнями
        delay_frame = ttk.Frame(message_frame)
        delay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(delay_frame, text="Затримка між повідомленнями (сек):").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(delay_frame, from_=1.0, to=10.0, increment=0.5, textvariable=self.delay_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Текст повідомлення
        ttk.Label(message_frame, text="Текст повідомлення:").pack(anchor=tk.W, pady=5)
        self.message_text = scrolledtext.ScrolledText(message_frame, height=10, wrap=tk.WORD)
        self.message_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Область одержувачів
        recipients_frame = ttk.LabelFrame(main_frame, text="Одержувачі", padding=10)
        recipients_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(recipients_frame, text=f"Зі списку файлу {DEFAULT_RECIPIENTS_FILE}:").pack(anchor=tk.W, pady=5)
        
        # Список одержувачів
        recipients_btn_frame = ttk.Frame(recipients_frame)
        recipients_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(recipients_btn_frame, text="Відкрити файл", command=self.open_recipients_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(recipients_btn_frame, text="Оновити список", command=self.reload_recipients).pack(side=tk.LEFT, padx=5)
        
        # Список одержувачів
        self.recipients_text = scrolledtext.ScrolledText(recipients_frame, height=5, wrap=tk.WORD)
        self.recipients_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.reload_recipients()
        
        # Область відправки
        send_frame = ttk.Frame(main_frame)
        send_frame.pack(fill=tk.X, pady=10)
        
        # Кнопка відправки
        ttk.Button(send_frame, text="ВІДПРАВИТИ ПОВІДОМЛЕННЯ", command=self.send_messages, style="Accent.TButton").pack(pady=10)
        
        # Лог і статус
        log_frame = ttk.LabelFrame(main_frame, text="Лог відправки", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Статус
        status_frame = ttk.Frame(log_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="Статус:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status_var, font=("", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Лог
        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Створюємо стилі
        style = ttk.Style()
        if "Accent.TButton" not in style.theme_names():
            style.configure("Accent.TButton", font=("", 12, "bold"))
        
        # Обробник закриття вікна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """Обробник закриття вікна"""
        # Зберігаємо конфігурацію
        self.save_config()
        
        # Відключаємося від Telegram
        if hasattr(self, "sender"):
            self.sender.disconnect()
            
        # Закриваємо вікно
        self.root.destroy()
        
    def check_authorization(self):
        """Перевірка авторизації у Telegram"""
        if not self.sender:
            self.log("Помилка: відправник не ініціалізований")
            return
            
        self.log("Перевірка авторизації...")
        self.status_var.set("Перевірка авторизації...")
        
        # Запускаємо в окремому потоці
        threading.Thread(target=self._check_auth_thread, daemon=True).start()
        
    def _check_auth_thread(self):
        """Перевірка авторизації у окремому потоці"""
        try:
            is_authorized = self.sender.connect_and_check()
            
            if is_authorized:
                self.log("✓ Авторизація успішна!")
                self.status_var.set("Авторизовано")
                
                # Отримуємо інформацію про користувача
                user_info = self.sender.get_me()
                if user_info:
                    self.log(f"Ви увійшли як: {user_info.first_name} {user_info.last_name or ''} (@{user_info.username or 'немає'})")
            else:
                self.log("✗ Не авторизовано. Потрібно ввести номер телефону і код підтвердження.")
                self.status_var.set("Не авторизовано")
        except Exception as e:
            self.log(f"Помилка перевірки авторизації: {e}")
            self.status_var.set("Помилка")
            
    def request_code(self):
        """Запит коду підтвердження"""
        phone = self.phone_var.get().strip()
        
        if not phone:
            messagebox.showerror("Помилка", "Введіть номер телефону")
            return
            
        if not phone.startswith("+"):
            messagebox.showerror("Помилка", "Номер телефону повинен починатися з '+'")
            return
            
        # Оновлюємо статус
        self.log(f"Запит коду підтвердження на номер {phone}...")
        self.status_var.set("Запит коду...")
        
        # Запускаємо в окремому потоці
        threading.Thread(target=self._request_code_thread, args=(phone,), daemon=True).start()
        
    def _request_code_thread(self, phone):
        """Запит коду у окремому потоці"""
        try:
            result = self.sender.request_code(phone)
            
            if result:
                self.log(f"✓ Код відправлено на номер {phone}")
                self.status_var.set("Код відправлено")
                
                # Зберігаємо телефон у конфігурації
                self.config["last_phone"] = phone
                self.save_config()
            else:
                self.log("✗ Помилка відправки коду")
                self.status_var.set("Помилка")
        except Exception as e:
            self.log(f"Помилка запиту коду: {e}")
            self.status_var.set("Помилка")
            
    def login(self):
        """Вхід з кодом підтвердження"""
        phone = self.phone_var.get().strip()
        code = self.code_var.get().strip()
        password = self.password_var.get()
        
        if not phone or not code:
            messagebox.showerror("Помилка", "Введіть номер телефону і код підтвердження")
            return
            
        # Оновлюємо статус
        self.log(f"Вхід з номером {phone} і кодом...")
        self.status_var.set("Вхід...")
        
        # Запускаємо в окремому потоці
        threading.Thread(target=self._login_thread, args=(phone, code, password), daemon=True).start()
        
    def _login_thread(self, phone, code, password):
        """Вхід у окремому потоці"""
        try:
            result = self.sender.login(phone, code, password)
            
            if result:
                self.log("✓ Успішний вхід!")
                self.status_var.set("Авторизовано")
                
                # Очищаємо поля
                self.code_var.set("")
                self.password_var.set("")
                
                # Отримуємо інформацію про користувача
                user_info = self.sender.get_me()
                if user_info:
                    self.log(f"Ви увійшли як: {user_info.first_name} {user_info.last_name or ''} (@{user_info.username or 'немає'})")
                
                # Зберігаємо телефон у конфігурації
                self.config["last_phone"] = phone
                self.save_config()
            else:
                self.log("✗ Помилка входу")
                self.status_var.set("Помилка")
        except Exception as e:
            self.log(f"Помилка входу: {e}")
            self.status_var.set("Помилка")
            
    def open_recipients_file(self):
        """Відкриття файлу зі списком одержувачів"""
        if os.path.exists(DEFAULT_RECIPIENTS_FILE):
            if sys.platform == "win32":
                os.system(f"notepad.exe {DEFAULT_RECIPIENTS_FILE}")
            else:
                os.system(f"xdg-open {DEFAULT_RECIPIENTS_FILE}")
        else:
            messagebox.showerror("Помилка", f"Файл {DEFAULT_RECIPIENTS_FILE} не знайдено")
            
    def reload_recipients(self):
        """Оновлення списку одержувачів з файлу"""
        if os.path.exists(DEFAULT_RECIPIENTS_FILE):
            try:
                with open(DEFAULT_RECIPIENTS_FILE, "r", encoding="utf-8") as f:
                    recipients = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            recipients.append(line)
                
                # Оновлюємо текст
                self.recipients_text.delete(1.0, tk.END)
                self.recipients_text.insert(tk.END, "\n".join(recipients))
                
                # Виводимо статистику
                self.log(f"Завантажено {len(recipients)} одержувачів з файлу {DEFAULT_RECIPIENTS_FILE}")
            except Exception as e:
                self.log(f"Помилка завантаження одержувачів: {e}")
        else:
            self.log(f"Файл {DEFAULT_RECIPIENTS_FILE} не знайдено")
            
    def send_messages(self):
        """Відправка повідомлень"""
        # Перевіряємо авторизацію
        if not self.sender.is_authorized():
            messagebox.showerror("Помилка", "Ви не авторизовані у Telegram")
            return
            
        # Отримуємо повідомлення
        message = self.message_text.get(1.0, tk.END).strip()
        if not message:
            messagebox.showerror("Помилка", "Введіть текст повідомлення")
            return
            
        # Отримуємо список одержувачів
        recipients_text = self.recipients_text.get(1.0, tk.END)
        recipients = [r.strip() for r in recipients_text.split("\n") if r.strip()]
        
        if not recipients:
            messagebox.showerror("Помилка", "Список одержувачів порожній")
            return
            
        # Затримка між повідомленнями
        delay = self.delay_var.get()
        
        # Підтвердження
        if not messagebox.askyesno("Підтвердження", 
                                   f"Відправити повідомлення {len(recipients)} одержувачам?\n\n"
                                   f"Текст: {message[:50]}{'...' if len(message) > 50 else ''}"):
            return
            
        # Оновлюємо статус
        self.log(f"Початок відправки повідомлень {len(recipients)} одержувачам...")
        self.status_var.set("Відправка...")
        
        # Запускаємо в окремому потоці
        threading.Thread(target=self._send_messages_thread, args=(message, recipients, delay), daemon=True).start()
        
    def _send_messages_thread(self, message, recipients, delay):
        """Відправка повідомлень у окремому потоці"""
        start_time = time.time()
        
        try:
            # Перевіряємо підключення
            if not self.sender.is_connected():
                if not self.sender.connect():
                    self.log("✗ Помилка підключення до Telegram")
                    self.status_var.set("Помилка")
                    return
                    
            # Починаємо відправку
            self.log(f"Відправка повідомлень {len(recipients)} одержувачам...")
            
            # Лічильники
            successful = 0
            failed = 0
            error_details = {}
            
            # Відправляємо повідомлення
            for i, recipient in enumerate(recipients, 1):
                recipient = recipient.strip()
                if not recipient:
                    continue
                    
                try:
                    # Виводимо прогрес
                    self.log(f"[{i}/{len(recipients)}] Відправка для {recipient}...")
                    self.status_var.set(f"Відправка {i}/{len(recipients)}")
                    
                    # Відправляємо повідомлення
                    result = self.sender.send_message(recipient, message)
                    
                    if result:
                        # Успішно
                        successful += 1
                        self.log(f"✓ Успішно відправлено: {recipient}")
                    else:
                        # Помилка
                        failed += 1
                        self.log(f"✗ Помилка відправки: {recipient}")
                        error_details[recipient] = "Невідома помилка"
                        
                    # Пауза між повідомленнями
                    if i < len(recipients):
                        time.sleep(delay)
                        
                except Exception as e:
                    # Помилка відправки
                    failed += 1
                    error_message = str(e)
                    self.log(f"✗ Помилка відправки для {recipient}: {error_message}")
                    error_details[recipient] = error_message
                    
                    # Додаткова пауза після помилки
                    time.sleep(2)
            
            # Загальний час
            total_time = time.time() - start_time
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            
            # Підсумки
            self.log("\n===== РЕЗУЛЬТАТИ ВІДПРАВКИ =====")
            self.log(f"Всього одержувачів: {len(recipients)}")
            self.log(f"Успішно відправлено: {successful}")
            self.log(f"Помилок: {failed}")
            self.log(f"Час відправки: {minutes} хв {seconds} сек")
            
            # Процент успіху
            if recipients:
                success_rate = (successful / len(recipients)) * 100
                self.log(f"Процент успіху: {success_rate:.1f}%")
                
            # Деталі помилок
            if error_details:
                self.log("\nОдержувачі з помилками:")
                for i, (recipient, error) in enumerate(list(error_details.items())[:5], 1):
                    self.log(f"  {i}. {recipient}: {error}")
                
                if len(error_details) > 5:
                    self.log(f"  ... і ще {len(error_details) - 5} помилок")
                    
            # Зберігаємо лог у файл
            self.save_log(message, recipients, successful, failed, error_details)
            
            # Оновлюємо статус
            self.status_var.set(f"Готово: {successful}/{len(recipients)}")
            
            # Повідомлення про завершення
            messagebox.showinfo("Завершено", 
                               f"Відправка завершена!\n\n"
                               f"Успішно: {successful}\n"
                               f"Помилок: {failed}\n"
                               f"Час: {minutes} хв {seconds} сек")
                
        except Exception as e:
            self.log(f"Критична помилка відправки: {e}")
            self.status_var.set("Помилка")
            messagebox.showerror("Помилка", f"Критична помилка відправки: {e}")
            
    def save_log(self, message, recipients, successful, failed, error_details):
        """Збереження логу у файл"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n===== ВІДПРАВКА {timestamp} =====\n")
                f.write(f"Повідомлення: {message[:100]}{'...' if len(message) > 100 else ''}\n")
                f.write(f"Всього одержувачів: {len(recipients)}\n")
                f.write(f"Успішно відправлено: {successful}\n")
                f.write(f"Помилок: {failed}\n")
                
                if error_details:
                    f.write("\nОдержувачі з помилками:\n")
                    for recipient, error in error_details.items():
                        f.write(f"  {recipient}: {error}\n")
                        
                f.write("\n")
        except Exception as e:
            self.log(f"Помилка збереження логу: {e}")
            
    def log(self, message):
        """Виведення повідомлення у лог"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            # Додаємо у віджет
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
            
            # Оновлюємо GUI
            self.root.update_idletasks()
        except:
            pass

def main():
    """Основна функція програми"""
    root = tk.Tk()
    app = TelegramSenderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()