#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
МУЛЬТИ-АККАУНТ ОТПРАВИТЕЛЬ TELEGRAM
===================================

Оптимизированная версия с поддержкой:
- Нескольких аккаунтов Telegram
- Мобильных устройств
- Простого и понятного интерфейса
- Безопасного хранения сессий

Поддерживает Windows, macOS и Android (через Termux или Pydroid 3)
"""

import os
import sys
import time
import json
import random
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# API данные для Telegram
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

# Директория для хранения файлов сессий
SESSIONS_DIR = "telegram_sessions"

# Файл с информацией об аккаунтах
ACCOUNTS_FILE = "telegram_accounts.json"

# Файл для получателей
RECIPIENTS_FILE = "recipients.txt"

# Проверяем наличие библиотеки Telethon
try:
    from telethon.sync import TelegramClient
    from telethon.errors import FloodWaitError, SessionPasswordNeededError
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logger.error("Telethon не установлен! Устанавливаем...")

# Проверяем мобильную платформу
IS_ANDROID = False
try:
    if "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ:
        IS_ANDROID = True
        logger.info("Обнаружена Android система")
except:
    pass

# Проверяем, есть ли возможность использования графического интерфейса
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    HAVE_GUI = True
except ImportError:
    HAVE_GUI = False

class TelegramAccount:
    """Класс для работы с аккаунтом Telegram"""
    def __init__(self, phone=None, name=None, session_name=None):
        self.phone = phone
        self.name = name or f"Аккаунт ({phone})"
        self.session_name = session_name or self._generate_session_name(phone)
        self.client = None
        self.is_connected = False
        self.is_authorized = False
        self.client_info = {}
    
    def _generate_session_name(self, phone=None):
        """Генерирует имя сессии на основе телефона или случайно"""
        if phone:
            # Очищаем телефон от нечисловых символов для имени файла
            return f"session_{phone.replace('+', '').replace('-', '').replace(' ', '')}"
        else:
            # Случайное имя сессии
            import uuid
            return f"session_{uuid.uuid4().hex[:8]}"
    
    def get_session_path(self):
        """Получает полный путь к файлу сессии"""
        # Создаем директорию для сессий если её нет
        if not os.path.exists(SESSIONS_DIR):
            os.makedirs(SESSIONS_DIR)
        
        return os.path.join(SESSIONS_DIR, self.session_name)
    
    def connect(self):
        """Подключается к Telegram"""
        if self.client:
            self.disconnect()  # Отключаемся от предыдущей сессии
        
        self.client = TelegramClient(self.get_session_path(), API_ID, API_HASH)
        
        try:
            self.client.connect()
            self.is_connected = True
            self.is_authorized = self.client.is_user_authorized()
            
            # Получаем информацию о клиенте если авторизован
            if self.is_authorized:
                me = self.client.get_me()
                self.client_info = {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name or "",
                    "username": me.username or "",
                    "phone": me.phone or self.phone or ""
                }
                if not self.name or self.name.startswith("Аккаунт ("):
                    self.name = f"{me.first_name} {me.last_name or ''}".strip()
                    if me.username:
                        self.name += f" (@{me.username})"
                
                logger.info(f"Подключен к аккаунту: {self.name}")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при подключении: {e}")
            self.is_connected = False
            self.is_authorized = False
            return False
    
    def disconnect(self):
        """Отключается от Telegram"""
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
            self.client = None
        self.is_connected = False
    
    def login(self, phone, code_callback, password_callback=None):
        """
        Авторизуется в Telegram
        
        Args:
            phone (str): Номер телефона
            code_callback (callable): Функция для получения кода
            password_callback (callable, optional): Функция для получения пароля 2FA
        
        Returns:
            bool: Успешность авторизации
        """
        if not self.is_connected:
            if not self.connect():
                return False
        
        if self.is_authorized:
            return True
        
        self.phone = phone
        
        try:
            logger.info(f"Отправка кода на номер {phone}")
            # Запросить код подтверждения
            self.client.send_code_request(phone)
            
            # Получить код от пользователя
            code = code_callback()
            
            # Войти с кодом
            try:
                self.client.sign_in(phone, code)
                self.is_authorized = True
            except SessionPasswordNeededError:
                # Если нужен пароль двухфакторной аутентификации
                if password_callback:
                    password = password_callback()
                    self.client.sign_in(password=password)
                    self.is_authorized = True
                else:
                    logger.error("Требуется пароль двухфакторной аутентификации!")
                    return False
            
            # Получаем информацию о клиенте
            if self.is_authorized:
                me = self.client.get_me()
                self.client_info = {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name or "",
                    "username": me.username or "",
                    "phone": me.phone or self.phone or ""
                }
                self.name = f"{me.first_name} {me.last_name or ''}".strip()
                if me.username:
                    self.name += f" (@{me.username})"
                
                logger.info(f"Успешный вход в аккаунт: {self.name}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}")
            return False
        
        return self.is_authorized
    
    def logout(self):
        """Выходит из аккаунта Telegram"""
        if self.client and self.is_connected:
            try:
                result = self.client.log_out()
                self.is_authorized = not result
                if result:
                    logger.info(f"Выход из аккаунта {self.name} выполнен успешно")
                    # Удаляем файл сессии
                    session_file = f"{self.get_session_path()}.session"
                    if os.path.exists(session_file):
                        os.remove(session_file)
                    
                    return True
                else:
                    logger.error(f"Не удалось выйти из аккаунта {self.name}")
            except Exception as e:
                logger.error(f"Ошибка при выходе из аккаунта: {e}")
        
        return False
    
    def send_message(self, recipient, message):
        """
        Отправляет сообщение получателю
        
        Args:
            recipient (str): Получатель (username или телефон)
            message (str): Текст сообщения
        
        Returns:
            bool: Успешность отправки
        """
        if not self.client or not self.is_connected or not self.is_authorized:
            logger.error("Клиент не подключен или не авторизован")
            return False
        
        try:
            self.client.send_message(recipient, message)
            return True
        except FloodWaitError as e:
            logger.warning(f"Ограничение на отправку: ждем {e.seconds} секунд")
            time.sleep(e.seconds)
            try:
                self.client.send_message(recipient, message)
                return True
            except Exception as e2:
                logger.error(f"Ошибка при повторной отправке: {e2}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            return False
    
    def to_dict(self):
        """Преобразует данные аккаунта в словарь для сохранения"""
        return {
            "phone": self.phone,
            "name": self.name,
            "session_name": self.session_name,
            "client_info": self.client_info
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создает объект аккаунта из словаря"""
        account = cls(
            phone=data.get("phone"),
            name=data.get("name"),
            session_name=data.get("session_name")
        )
        account.client_info = data.get("client_info", {})
        return account


class AccountManager:
    """Класс для управления аккаунтами Telegram"""
    def __init__(self):
        self.accounts = []
        self.current_account = None
        self.load_accounts()
    
    def load_accounts(self):
        """Загружает сохраненные аккаунты"""
        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
                
                for account_data in accounts_data:
                    account = TelegramAccount.from_dict(account_data)
                    self.accounts.append(account)
                
                logger.info(f"Загружено {len(self.accounts)} аккаунтов")
                
                # Проверяем наличие файлов сессий и удаляем аккаунты без сессий
                valid_accounts = []
                for account in self.accounts:
                    session_file = f"{account.get_session_path()}.session"
                    if os.path.exists(session_file):
                        valid_accounts.append(account)
                    else:
                        logger.warning(f"Удаление аккаунта {account.name} (сессия не найдена)")
                
                self.accounts = valid_accounts
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке аккаунтов: {e}")
    
    def save_accounts(self):
        """Сохраняет аккаунты в файл"""
        try:
            accounts_data = [account.to_dict() for account in self.accounts]
            with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(accounts_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Сохранено {len(self.accounts)} аккаунтов")
        except Exception as e:
            logger.error(f"Ошибка при сохранении аккаунтов: {e}")
    
    def add_account(self, account):
        """Добавляет новый аккаунт"""
        # Проверяем, есть ли аккаунт с таким же именем сессии
        for existing_account in self.accounts:
            if existing_account.session_name == account.session_name:
                logger.warning(f"Аккаунт с сессией {account.session_name} уже существует")
                return False
        
        self.accounts.append(account)
        self.save_accounts()
        return True
    
    def remove_account(self, account):
        """Удаляет аккаунт"""
        if account in self.accounts:
            # Выходим из аккаунта если он подключен
            if account.is_connected:
                account.logout()
            
            self.accounts.remove(account)
            self.save_accounts()
            return True
        return False
    
    def get_account_by_session(self, session_name):
        """Находит аккаунт по имени сессии"""
        for account in self.accounts:
            if account.session_name == session_name:
                return account
        return None
    
    def connect_account(self, account):
        """Подключает к аккаунту"""
        if account.connect():
            self.current_account = account
            return True
        return False
    
    def disconnect_current_account(self):
        """Отключается от текущего аккаунта"""
        if self.current_account:
            self.current_account.disconnect()
            self.current_account = None
    
    def scan_for_sessions(self):
        """Сканирует директорию с сессиями и добавляет новые аккаунты"""
        if not os.path.exists(SESSIONS_DIR):
            os.makedirs(SESSIONS_DIR)
            return
        
        # Получаем список файлов сессий
        session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
        
        # Получаем имена сессий без расширения
        session_names = [os.path.splitext(f)[0] for f in session_files]
        
        # Проверяем каждую сессию
        for session_name in session_names:
            # Пропускаем если аккаунт с такой сессией уже есть
            if self.get_account_by_session(session_name):
                continue
            
            # Создаем временный аккаунт для проверки
            temp_account = TelegramAccount(session_name=session_name)
            if temp_account.connect():
                if temp_account.is_authorized:
                    # Добавляем аккаунт в список
                    self.add_account(temp_account)
                    logger.info(f"Найден новый аккаунт: {temp_account.name}")
                temp_account.disconnect()


class RecipientManager:
    """Класс для управления получателями"""
    def __init__(self, recipients_file=RECIPIENTS_FILE):
        self.recipients_file = recipients_file
        self.recipients = []
        self.load_recipients()
    
    def load_recipients(self):
        """Загружает получателей из файла"""
        self.recipients = []
        
        if not os.path.exists(self.recipients_file):
            self.create_default_file()
            return
        
        try:
            with open(self.recipients_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.recipients.append(line)
            
            logger.info(f"Загружено {len(self.recipients)} получателей")
        except Exception as e:
            logger.error(f"Ошибка при загрузке получателей: {e}")
    
    def create_default_file(self):
        """Создает файл с получателями по умолчанию"""
        try:
            with open(self.recipients_file, 'w', encoding='utf-8') as f:
                f.write("# Список получателей сообщений Telegram\n")
                f.write("# Добавляйте по одному получателю на строку\n")
                f.write("# Можно указывать @username или номер телефона с '+'\n")
                f.write("# Пример:\n")
                f.write("# @username\n")
                f.write("# +79001234567\n")
            
            logger.info(f"Создан файл получателей: {self.recipients_file}")
        except Exception as e:
            logger.error(f"Ошибка при создании файла получателей: {e}")
    
    def add_recipient(self, recipient):
        """Добавляет получателя в список"""
        recipient = recipient.strip()
        if recipient and recipient not in self.recipients:
            self.recipients.append(recipient)
            self.save_recipients()
            return True
        return False
    
    def remove_recipient(self, recipient):
        """Удаляет получателя из списка"""
        if recipient in self.recipients:
            self.recipients.remove(recipient)
            self.save_recipients()
            return True
        return False
    
    def save_recipients(self):
        """Сохраняет получателей в файл"""
        try:
            with open(self.recipients_file, 'w', encoding='utf-8') as f:
                f.write("# Список получателей сообщений Telegram\n")
                f.write("# Добавлен: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
                for recipient in self.recipients:
                    f.write(recipient + "\n")
            
            logger.info(f"Сохранено {len(self.recipients)} получателей")
        except Exception as e:
            logger.error(f"Ошибка при сохранении получателей: {e}")


class TelegramSenderGUI:
    """Графический интерфейс для отправителя сообщений Telegram"""
    def __init__(self, root):
        self.root = root
        self.root.title("Отправитель сообщений Telegram")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Инициализируем менеджеры
        self.account_manager = AccountManager()
        self.recipient_manager = RecipientManager()
        
        # Текущий аккаунт
        self.current_account = None
        self.sending_in_progress = False
        
        # Создаем интерфейс
        self.create_ui()
        
        # Сканируем сессии
        self.account_manager.scan_for_sessions()
        self.update_account_list()
    
    def create_ui(self):
        """Создает пользовательский интерфейс"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill="both")
        
        # Верхняя панель: аккаунты
        account_frame = ttk.LabelFrame(main_frame, text="Аккаунты Telegram", padding="5")
        account_frame.pack(fill="x", pady=5)
        
        # Выбор аккаунта и кнопки
        account_select_frame = ttk.Frame(account_frame)
        account_select_frame.pack(fill="x", pady=5)
        
        ttk.Label(account_select_frame, text="Аккаунт:").pack(side="left", padx=5)
        
        self.account_combobox = ttk.Combobox(account_select_frame, width=30, state="readonly")
        self.account_combobox.pack(side="left", padx=5)
        self.account_combobox.bind("<<ComboboxSelected>>", self.on_account_select)
        
        account_buttons_frame = ttk.Frame(account_select_frame)
        account_buttons_frame.pack(side="right", padx=5)
        
        self.connect_button = ttk.Button(account_buttons_frame, text="Подключиться", command=self.connect_account)
        self.connect_button.pack(side="left", padx=2)
        
        self.add_account_button = ttk.Button(account_buttons_frame, text="Добавить аккаунт", command=self.add_account)
        self.add_account_button.pack(side="left", padx=2)
        
        self.remove_account_button = ttk.Button(account_buttons_frame, text="Удалить", command=self.remove_account)
        self.remove_account_button.pack(side="left", padx=2)
        
        self.logout_button = ttk.Button(account_buttons_frame, text="Выйти", command=self.logout_account)
        self.logout_button.pack(side="left", padx=2)
        self.logout_button["state"] = "disabled"
        
        # Информация об аккаунте
        self.account_info_frame = ttk.LabelFrame(account_frame, text="Информация об аккаунте", padding="5")
        self.account_info_frame.pack(fill="x", pady=5)
        
        self.account_info_label = ttk.Label(self.account_info_frame, text="Не подключен", justify="left")
        self.account_info_label.pack(fill="x", padx=5, pady=5)
        
        # Средняя панель: получатели
        recipients_frame = ttk.LabelFrame(main_frame, text="Получатели", padding="5")
        recipients_frame.pack(fill="x", pady=5)
        
        recipients_buttons_frame = ttk.Frame(recipients_frame)
        recipients_buttons_frame.pack(fill="x", pady=5)
        
        ttk.Label(recipients_buttons_frame, text="Получатели:").pack(side="left", padx=5)
        ttk.Label(recipients_buttons_frame, text=f"Загружено: {len(self.recipient_manager.recipients)}").pack(side="left", padx=5)
        
        ttk.Button(recipients_buttons_frame, text="Обновить", command=self.reload_recipients).pack(side="right", padx=2)
        ttk.Button(recipients_buttons_frame, text="Редактировать", command=self.edit_recipients).pack(side="right", padx=2)
        ttk.Button(recipients_buttons_frame, text="Добавить", command=self.add_recipient).pack(side="right", padx=2)
        
        # Список получателей
        recipients_list_frame = ttk.Frame(recipients_frame)
        recipients_list_frame.pack(fill="x", pady=5)
        
        self.recipients_listbox = tk.Listbox(recipients_list_frame, height=4, selectmode="multiple")
        self.recipients_listbox.pack(side="left", fill="both", expand=True, padx=5)
        
        recipients_scrollbar = ttk.Scrollbar(recipients_list_frame, orient="vertical", command=self.recipients_listbox.yview)
        recipients_scrollbar.pack(side="right", fill="y")
        self.recipients_listbox.config(yscrollcommand=recipients_scrollbar.set)
        
        # Кнопка выбора всех получателей
        recipients_select_frame = ttk.Frame(recipients_frame)
        recipients_select_frame.pack(fill="x", pady=5)
        
        ttk.Button(recipients_select_frame, text="Выбрать всех", command=self.select_all_recipients).pack(side="left", padx=5)
        ttk.Button(recipients_select_frame, text="Снять выбор", command=self.deselect_all_recipients).pack(side="left", padx=5)
        
        # Нижняя панель: сообщение
        message_frame = ttk.LabelFrame(main_frame, text="Сообщение", padding="5")
        message_frame.pack(fill="both", expand=True, pady=5)
        
        # Текст сообщения
        message_text_frame = ttk.Frame(message_frame)
        message_text_frame.pack(fill="both", expand=True, pady=5)
        
        self.message_text = scrolledtext.ScrolledText(message_text_frame, wrap="word", height=10)
        self.message_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Кнопки отправки
        send_buttons_frame = ttk.Frame(message_frame)
        send_buttons_frame.pack(fill="x", pady=5)
        
        self.send_button = ttk.Button(send_buttons_frame, text="Отправить сообщения", command=self.send_messages)
        self.send_button.pack(side="left", padx=5)
        self.send_button["state"] = "disabled"
        
        self.stop_button = ttk.Button(send_buttons_frame, text="Остановить отправку", command=self.stop_sending)
        self.stop_button.pack(side="left", padx=5)
        self.stop_button["state"] = "disabled"
        
        # Статус
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Готов к работе")
        self.status_label.pack(side="left", padx=5)
        
        # Логи
        log_frame = ttk.LabelFrame(main_frame, text="Логи", padding="5")
        log_frame.pack(fill="both", expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", height=5, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Перенаправляем логи
        self.log_handler = self.LogHandler(self.log_text)
        logger.addHandler(self.log_handler)
        
        # Обновляем списки
        self.update_account_list()
        self.update_recipients_list()
    
    class LogHandler(logging.Handler):
        """Обработчик логов для вывода в текстовое поле"""
        def __init__(self, text_widget):
            logging.Handler.__init__(self)
            self.text_widget = text_widget
        
        def emit(self, record):
            msg = self.format(record)
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg + "\n")
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
    
    def update_account_list(self):
        """Обновляет список аккаунтов"""
        accounts = [account.name for account in self.account_manager.accounts]
        accounts.append("Новый аккаунт...")
        
        self.account_combobox["values"] = accounts
        
        if accounts and accounts[0] != "Новый аккаунт...":
            self.account_combobox.current(0)
        else:
            # Если нет аккаунтов, выбираем "Новый аккаунт..."
            self.account_combobox.current(0)
    
    def update_recipients_list(self):
        """Обновляет список получателей"""
        self.recipients_listbox.delete(0, "end")
        for recipient in self.recipient_manager.recipients:
            self.recipients_listbox.insert("end", recipient)
    
    def update_account_info(self):
        """Обновляет информацию об аккаунте"""
        if not self.current_account or not self.current_account.is_connected:
            self.account_info_label.config(text="Не подключен")
            self.send_button["state"] = "disabled"
            self.logout_button["state"] = "disabled"
            return
        
        if self.current_account.is_authorized:
            info = self.current_account.client_info
            text = f"Имя: {info.get('first_name', '')} {info.get('last_name', '')}\n"
            if info.get('username'):
                text += f"Username: @{info.get('username')}\n"
            text += f"Телефон: {info.get('phone', '')}\n"
            text += f"ID: {info.get('id', '')}"
            
            self.account_info_label.config(text=text)
            self.send_button["state"] = "normal"
            self.logout_button["state"] = "normal"
        else:
            self.account_info_label.config(text="Аккаунт не авторизован")
            self.send_button["state"] = "disabled"
            self.logout_button["state"] = "disabled"
    
    def on_account_select(self, event=None):
        """Обработчик выбора аккаунта"""
        selection = self.account_combobox.get()
        
        if selection == "Новый аккаунт...":
            self.add_account()
            return
        
        # Находим аккаунт по имени
        for account in self.account_manager.accounts:
            if account.name == selection:
                # Отключаем текущий аккаунт если есть
                if self.current_account and self.current_account.is_connected:
                    self.current_account.disconnect()
                
                self.current_account = account
                self.update_account_info()
                return
    
    def connect_account(self):
        """Подключается к выбранному аккаунту"""
        if not self.current_account:
            messagebox.showerror("Ошибка", "Выберите аккаунт")
            return
        
        self.status_label.config(text="Подключение к аккаунту...")
        
        # Подключаемся к аккаунту
        if self.current_account.connect():
            self.update_account_info()
            self.status_label.config(text="Подключено к аккаунту")
        else:
            messagebox.showerror("Ошибка", "Не удалось подключиться к аккаунту")
            self.status_label.config(text="Ошибка подключения")
    
    def add_account(self):
        """Добавляет новый аккаунт"""
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление аккаунта")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрируем окно
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Содержимое окна
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Введите номер телефона для входа в Telegram:", justify="left").pack(anchor="w", pady=5)
        
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(frame, textvariable=phone_var, width=20)
        phone_entry.pack(anchor="w", pady=5, fill="x")
        phone_entry.focus_set()
        
        # Статус
        status_var = tk.StringVar(value="Введите номер телефона и нажмите 'Получить код'")
        status_label = ttk.Label(frame, textvariable=status_var, justify="left")
        status_label.pack(anchor="w", pady=5, fill="x")
        
        # Переменные для кода и пароля
        code_var = tk.StringVar()
        code_entry = None
        
        password_var = tk.StringVar()
        password_entry = None
        
        # Функция для запроса кода
        def request_code():
            phone = phone_var.get().strip()
            if not phone:
                messagebox.showerror("Ошибка", "Введите номер телефона")
                return
            
            # Создаем временный аккаунт
            temp_account = TelegramAccount(phone=phone)
            
            # Подключаемся
            if not temp_account.connect():
                messagebox.showerror("Ошибка", "Не удалось подключиться к Telegram")
                return
            
            # Если аккаунт уже авторизован
            if temp_account.is_authorized:
                # Добавляем аккаунт в список
                self.account_manager.add_account(temp_account)
                self.current_account = temp_account
                self.update_account_list()
                self.update_account_info()
                
                messagebox.showinfo("Успех", "Аккаунт уже авторизован и добавлен")
                dialog.destroy()
                return
            
            # Запрашиваем код
            try:
                status_var.set("Отправка запроса на код подтверждения...")
                temp_account.client.send_code_request(phone)
                status_var.set("Код отправлен. Введите его ниже:")
                
                # Скрываем кнопку запроса кода и показываем поле для ввода кода
                request_code_button.pack_forget()
                
                nonlocal code_entry
                ttk.Label(frame, text="Код из SMS или Telegram:").pack(anchor="w", pady=5)
                code_entry = ttk.Entry(frame, textvariable=code_var, width=10)
                code_entry.pack(anchor="w", pady=5, fill="x")
                code_entry.focus_set()
                
                # Показываем кнопку подтверждения кода
                confirm_code_button.pack(anchor="w", pady=5)
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при запросе кода: {e}")
                status_var.set("Ошибка при запросе кода")
                return
        
        # Функция для подтверждения кода
        def confirm_code():
            phone = phone_var.get().strip()
            code = code_var.get().strip()
            
            if not code:
                messagebox.showerror("Ошибка", "Введите код подтверждения")
                return
            
            # Создаем временный аккаунт
            temp_account = TelegramAccount(phone=phone)
            
            # Подключаемся
            if not temp_account.connect():
                messagebox.showerror("Ошибка", "Не удалось подключиться к Telegram")
                return
            
            # Пытаемся войти с кодом
            try:
                status_var.set("Проверка кода...")
                temp_account.client.sign_in(phone, code)
                
                # Добавляем аккаунт в список
                self.account_manager.add_account(temp_account)
                self.current_account = temp_account
                self.update_account_list()
                self.update_account_info()
                
                messagebox.showinfo("Успех", "Аккаунт успешно добавлен")
                dialog.destroy()
                
            except SessionPasswordNeededError:
                # Если требуется пароль двухфакторной аутентификации
                status_var.set("Требуется пароль двухфакторной аутентификации:")
                
                # Скрываем кнопку подтверждения кода
                confirm_code_button.pack_forget()
                
                nonlocal password_entry
                ttk.Label(frame, text="Пароль 2FA:").pack(anchor="w", pady=5)
                password_entry = ttk.Entry(frame, textvariable=password_var, show="*", width=20)
                password_entry.pack(anchor="w", pady=5, fill="x")
                password_entry.focus_set()
                
                # Показываем кнопку подтверждения пароля
                confirm_password_button.pack(anchor="w", pady=5)
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при входе: {e}")
                status_var.set("Ошибка при входе. Проверьте код.")
                return
        
        # Функция для подтверждения пароля
        def confirm_password():
            phone = phone_var.get().strip()
            password = password_var.get().strip()
            
            if not password:
                messagebox.showerror("Ошибка", "Введите пароль")
                return
            
            # Создаем временный аккаунт
            temp_account = TelegramAccount(phone=phone)
            
            # Подключаемся
            if not temp_account.connect():
                messagebox.showerror("Ошибка", "Не удалось подключиться к Telegram")
                return
            
            # Пытаемся войти с паролем
            try:
                status_var.set("Проверка пароля...")
                temp_account.client.sign_in(password=password)
                
                # Добавляем аккаунт в список
                self.account_manager.add_account(temp_account)
                self.current_account = temp_account
                self.update_account_list()
                self.update_account_info()
                
                messagebox.showinfo("Успех", "Аккаунт успешно добавлен")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при входе: {e}")
                status_var.set("Ошибка при входе. Проверьте пароль.")
                return
        
        # Кнопки
        request_code_button = ttk.Button(frame, text="Получить код", command=request_code)
        request_code_button.pack(anchor="w", pady=5)
        
        confirm_code_button = ttk.Button(frame, text="Подтвердить код", command=confirm_code)
        
        confirm_password_button = ttk.Button(frame, text="Подтвердить пароль", command=confirm_password)
        
        cancel_button = ttk.Button(frame, text="Отмена", command=dialog.destroy)
        cancel_button.pack(anchor="e", pady=5)
    
    def remove_account(self):
        """Удаляет выбранный аккаунт"""
        if not self.current_account:
            messagebox.showerror("Ошибка", "Выберите аккаунт")
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить аккаунт {self.current_account.name}?"):
            # Отключаемся от аккаунта
            if self.current_account.is_connected:
                self.current_account.disconnect()
            
            # Удаляем аккаунт
            self.account_manager.remove_account(self.current_account)
            self.current_account = None
            
            # Обновляем список
            self.update_account_list()
            self.update_account_info()
            
            self.status_label.config(text="Аккаунт удален")
    
    def logout_account(self):
        """Выходит из аккаунта Telegram"""
        if not self.current_account or not self.current_account.is_connected:
            messagebox.showerror("Ошибка", "Аккаунт не подключен")
            return
        
        if messagebox.askyesno("Подтверждение", f"Выйти из аккаунта {self.current_account.name}?"):
            # Выходим из аккаунта
            if self.current_account.logout():
                # Удаляем аккаунт из списка
                self.account_manager.remove_account(self.current_account)
                self.current_account = None
                
                # Обновляем список
                self.update_account_list()
                self.update_account_info()
                
                self.status_label.config(text="Выход из аккаунта выполнен")
            else:
                messagebox.showerror("Ошибка", "Не удалось выйти из аккаунта")
    
    def reload_recipients(self):
        """Перезагружает список получателей"""
        self.recipient_manager.load_recipients()
        self.update_recipients_list()
        
        # Обновляем метку
        self.status_label.config(text=f"Загружено {len(self.recipient_manager.recipients)} получателей")
    
    def edit_recipients(self):
        """Открывает файл с получателями для редактирования"""
        try:
            if sys.platform == "win32":
                os.startfile(self.recipient_manager.recipients_file)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.recipient_manager.recipients_file])
            else:
                subprocess.Popen(["xdg-open", self.recipient_manager.recipients_file])
            
            self.status_label.config(text=f"Открыт файл: {self.recipient_manager.recipients_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
    
    def add_recipient(self):
        """Добавляет нового получателя"""
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление получателя")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрируем окно
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Содержимое окна
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Введите получателя (@username или телефон с '+'):", justify="left").pack(anchor="w", pady=5)
        
        recipient_var = tk.StringVar()
        recipient_entry = ttk.Entry(frame, textvariable=recipient_var, width=30)
        recipient_entry.pack(anchor="w", pady=5, fill="x")
        recipient_entry.focus_set()
        
        # Функция для добавления получателя
        def add_recipient_action():
            recipient = recipient_var.get().strip()
            if not recipient:
                messagebox.showerror("Ошибка", "Введите получателя")
                return
            
            # Добавляем получателя
            if self.recipient_manager.add_recipient(recipient):
                self.update_recipients_list()
                messagebox.showinfo("Успех", f"Получатель {recipient} добавлен")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить получателя")
        
        # Кнопки
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill="x", pady=10)
        
        ttk.Button(buttons_frame, text="Добавить", command=add_recipient_action).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=dialog.destroy).pack(side="right", padx=5)
    
    def select_all_recipients(self):
        """Выбирает всех получателей"""
        self.recipients_listbox.selection_set(0, "end")
    
    def deselect_all_recipients(self):
        """Снимает выбор со всех получателей"""
        self.recipients_listbox.selection_clear(0, "end")
    
    def send_messages(self):
        """Отправляет сообщения выбранным получателям"""
        if not self.current_account or not self.current_account.is_connected or not self.current_account.is_authorized:
            messagebox.showerror("Ошибка", "Аккаунт не подключен или не авторизован")
            return
        
        # Получаем текст сообщения
        message = self.message_text.get("1.0", "end").strip()
        if not message:
            messagebox.showerror("Ошибка", "Введите текст сообщения")
            return
        
        # Получаем выбранных получателей
        selected_indices = self.recipients_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Ошибка", "Выберите получателей")
            return
        
        selected_recipients = [self.recipients_listbox.get(i) for i in selected_indices]
        
        # Подтверждение
        if not messagebox.askyesno("Подтверждение", f"Отправить сообщение {len(selected_recipients)} получателям?"):
            return
        
        # Отправляем сообщения
        self.sending_in_progress = True
        self.send_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        
        # Запускаем отправку в отдельном потоке
        import threading
        send_thread = threading.Thread(target=self.send_messages_thread, args=(message, selected_recipients))
        send_thread.daemon = True
        send_thread.start()
    
    def send_messages_thread(self, message, recipients):
        """Отправляет сообщения в отдельном потоке"""
        successful = 0
        failed = 0
        
        # Создаем лог-файл
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"отправка_{timestamp}.txt"
        
        with open(log_filename, 'w', encoding='utf-8') as log:
            log.write("===== ОТЧЕТ ОБ ОТПРАВКЕ СООБЩЕНИЙ =====\n\n")
            log.write(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"Аккаунт: {self.current_account.name}\n")
            log.write(f"Всего получателей: {len(recipients)}\n")
            log.write(f"Сообщение: {message}\n\n")
            
            logger.info(f"Начинаем отправку сообщений ({len(recipients)} получателей)...")
            self.status_label.config(text=f"Отправка... 0/{len(recipients)}")
            
            for i, recipient in enumerate(recipients, 1):
                # Проверяем флаг остановки
                if not self.sending_in_progress:
                    log.write("\nОтправка остановлена пользователем\n")
                    logger.info("Отправка остановлена пользователем")
                    break
                
                try:
                    # Обновляем статус
                    self.status_label.config(text=f"Отправка... {i}/{len(recipients)}")
                    
                    # Отправляем сообщение
                    if self.current_account.send_message(recipient, message):
                        successful += 1
                        status = f"✓ [{i}/{len(recipients)}] Отправлено: {recipient}"
                        logger.info(status)
                        log.write(f"{status}\n")
                    else:
                        failed += 1
                        status = f"✗ [{i}/{len(recipients)}] Ошибка отправки: {recipient}"
                        logger.error(status)
                        log.write(f"{status}\n")
                    
                    # Делаем паузу между сообщениями
                    if i < len(recipients) and self.sending_in_progress:
                        delay = 2 + random.uniform(0.5, 1.5)
                        time.sleep(delay)
                        
                except Exception as e:
                    failed += 1
                    status = f"✗ [{i}/{len(recipients)}] Ошибка: {recipient} - {str(e)}"
                    logger.error(status)
                    log.write(f"{status}\n")
                    time.sleep(2)
            
            # Записываем итоги
            log.write("\n===== ИТОГИ =====\n")
            log.write(f"Всего получателей: {len(recipients)}\n")
            log.write(f"Успешно отправлено: {successful}\n")
            log.write(f"Ошибок: {failed}\n")
            
            if recipients:
                success_rate = (successful / len(recipients)) * 100
                log.write(f"Процент успеха: {success_rate:.1f}%\n")
        
        logger.info(f"Отчет сохранен в файл: {log_filename}")
        
        # Обновляем интерфейс
        self.sending_in_progress = False
        self.send_button["state"] = "normal"
        self.stop_button["state"] = "disabled"
        
        if successful + failed > 0:
            self.status_label.config(text=f"Отправка завершена: {successful} успешно, {failed} ошибок")
            messagebox.showinfo("Результат", f"Отправка завершена\nУспешно: {successful}\nОшибок: {failed}")
        else:
            self.status_label.config(text="Отправка отменена")
    
    def stop_sending(self):
        """Останавливает отправку сообщений"""
        if self.sending_in_progress:
            if messagebox.askyesno("Подтверждение", "Остановить отправку сообщений?"):
                self.sending_in_progress = False
                self.status_label.config(text="Останавливаем отправку...")


class TelegramSenderConsole:
    """Консольный интерфейс для отправителя сообщений Telegram"""
    def __init__(self):
        self.account_manager = AccountManager()
        self.recipient_manager = RecipientManager()
        self.current_account = None
    
    def print_header(self):
        """Выводит заголовок программы"""
        print("=" * 60)
        print("МУЛЬТИ-АККАУНТ ОТПРАВИТЕЛЬ TELEGRAM")
        print("=" * 60)
        print("Версия для Windows и Android | by Replit Team")
        print("=" * 60)
    
    def print_accounts(self):
        """Выводит список аккаунтов"""
        print("\nСписок аккаунтов:")
        if not self.account_manager.accounts:
            print("  Нет доступных аккаунтов")
            return
        
        for i, account in enumerate(self.account_manager.accounts, 1):
            print(f"  {i}. {account.name}")
    
    def print_recipients(self):
        """Выводит список получателей"""
        print("\nСписок получателей:")
        if not self.recipient_manager.recipients:
            print("  Нет доступных получателей")
            return
        
        for i, recipient in enumerate(self.recipient_manager.recipients, 1):
            print(f"  {i}. {recipient}")
    
    def login_account(self):
        """Функция для входа в аккаунт"""
        print("\n=== ВХОД В АККАУНТ TELEGRAM ===")
        phone = input("\nВведите номер телефона (с +): ")
        
        # Создаем аккаунт
        account = TelegramAccount(phone=phone)
        
        # Подключаемся
        if not account.connect():
            print("Ошибка при подключении к Telegram")
            return None
        
        # Если аккаунт уже авторизован
        if account.is_authorized:
            print(f"Аккаунт уже авторизован: {account.name}")
            self.account_manager.add_account(account)
            self.account_manager.save_accounts()
            return account
        
        # Запрашиваем код
        try:
            account.client.send_code_request(phone)
            print("Код подтверждения отправлен")
            
            code = input("Введите код из Telegram: ")
            
            # Пытаемся войти с кодом
            try:
                account.client.sign_in(phone, code)
                
                # Если успешно
                self.account_manager.add_account(account)
                self.account_manager.save_accounts()
                print(f"Успешный вход: {account.name}")
                return account
                
            except SessionPasswordNeededError:
                # Если требуется пароль двухфакторной аутентификации
                print("Требуется пароль двухфакторной аутентификации")
                password = input("Введите пароль 2FA: ")
                
                try:
                    account.client.sign_in(password=password)
                    
                    # Если успешно
                    self.account_manager.add_account(account)
                    self.account_manager.save_accounts()
                    print(f"Успешный вход: {account.name}")
                    return account
                    
                except Exception as e:
                    print(f"Ошибка при входе с паролем: {e}")
                    return None
                
            except Exception as e:
                print(f"Ошибка при входе с кодом: {e}")
                return None
            
        except Exception as e:
            print(f"Ошибка при запросе кода: {e}")
            return None
    
    def select_account(self):
        """Функция для выбора аккаунта"""
        self.print_accounts()
        
        if not self.account_manager.accounts:
            print("\nНет доступных аккаунтов. Сначала войдите в аккаунт.")
            account = self.login_account()
            if account:
                self.current_account = account
                return True
            return False
        
        print("\n0. Войти в новый аккаунт")
        choice = input("Выберите аккаунт (номер) или 0 для нового: ")
        
        try:
            choice = int(choice)
            if choice == 0:
                account = self.login_account()
                if account:
                    self.current_account = account
                    return True
                return False
            
            if 1 <= choice <= len(self.account_manager.accounts):
                self.current_account = self.account_manager.accounts[choice - 1]
                
                # Подключаемся к выбранному аккаунту
                if self.current_account.connect():
                    print(f"Подключено к аккаунту: {self.current_account.name}")
                    return True
                else:
                    print("Ошибка при подключении к аккаунту")
                    return False
            else:
                print("Неверный номер аккаунта")
                return False
            
        except ValueError:
            print("Введите корректный номер")
            return False
    
    def logout_current_account(self):
        """Функция для выхода из текущего аккаунта"""
        if not self.current_account:
            print("Аккаунт не выбран")
            return False
        
        print(f"\nВыход из аккаунта {self.current_account.name}")
        if self.current_account.logout():
            self.account_manager.remove_account(self.current_account)
            self.account_manager.save_accounts()
            self.current_account = None
            print("Выход выполнен успешно")
            return True
        else:
            print("Ошибка при выходе из аккаунта")
            return False
    
    def send_messages(self):
        """Функция для отправки сообщений"""
        if not self.current_account or not self.current_account.is_connected or not self.current_account.is_authorized:
            print("Аккаунт не подключен или не авторизован")
            return
        
        # Загружаем получателей
        self.recipient_manager.load_recipients()
        recipients = self.recipient_manager.recipients
        
        if not recipients:
            print("\nНет получателей. Добавьте их в файл", self.recipient_manager.recipients_file)
            return
        
        # Выводим список получателей
        self.print_recipients()
        
        # Запрашиваем сообщение
        print("\nВведите текст сообщения (для завершения нажмите Enter, затем Ctrl+D или Ctrl+Z):")
        message_lines = []
        try:
            while True:
                line = input()
                message_lines.append(line)
        except (EOFError, KeyboardInterrupt):
            pass
        
        message = '\n'.join(message_lines)
        
        if not message.strip():
            print("\nСообщение не может быть пустым")
            return
        
        # Выбор получателей
        print("\nВыберите получателей:")
        print("1. Все получатели")
        print("2. Выбрать по номерам")
        
        choice = input("Ваш выбор (1/2): ")
        
        selected_recipients = []
        
        if choice == "1":
            selected_recipients = recipients
        elif choice == "2":
            print("\nВведите номера получателей через запятую (например, 1,3,5):")
            try:
                indices = [int(idx.strip()) for idx in input().split(",")]
                for idx in indices:
                    if 1 <= idx <= len(recipients):
                        selected_recipients.append(recipients[idx - 1])
            except:
                print("Неверный формат ввода")
                return
        else:
            print("Неверный выбор")
            return
        
        if not selected_recipients:
            print("Не выбраны получатели")
            return
        
        # Подтверждение
        print("\n" + "=" * 40)
        print(f"Аккаунт: {self.current_account.name}")
        print(f"Получателей: {len(selected_recipients)}")
        print(f"Текст: {message[:50]}{'...' if len(message) > 50 else ''}")
        print("=" * 40)
        
        confirm = input("\nНачать отправку сообщений? (да/нет): ").lower()
        if confirm not in ["да", "yes", "y", "д"]:
            print("\nОтправка отменена")
            return
        
        # Отправка сообщений
        successful = 0
        failed = 0
        stop_sending = False
        
        # Создаем лог-файл
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"отправка_{timestamp}.txt"
        
        with open(log_filename, 'w', encoding='utf-8') as log:
            log.write("===== ОТЧЕТ ОБ ОТПРАВКЕ СООБЩЕНИЙ =====\n\n")
            log.write(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"Аккаунт: {self.current_account.name}\n")
            log.write(f"Всего получателей: {len(selected_recipients)}\n")
            log.write(f"Сообщение: {message}\n\n")
            
            print(f"\n===== НАЧАЛО ОТПРАВКИ =====")
            
            for i, recipient in enumerate(selected_recipients, 1):
                try:
                    # Отправляем сообщение
                    if self.current_account.send_message(recipient, message):
                        successful += 1
                        status = f"✓ [{i}/{len(selected_recipients)}] Отправлено: {recipient}"
                        print(status)
                        log.write(f"{status}\n")
                    else:
                        failed += 1
                        status = f"✗ [{i}/{len(selected_recipients)}] Ошибка отправки: {recipient}"
                        print(status)
                        log.write(f"{status}\n")
                    
                    # Делаем паузу между сообщениями
                    if i < len(selected_recipients):
                        delay = 2 + random.uniform(0.5, 1.5)
                        time.sleep(delay)
                        
                except KeyboardInterrupt:
                    print("\nОтправка остановлена пользователем")
                    log.write("\nОтправка остановлена пользователем\n")
                    stop_sending = True
                    break
                        
                except Exception as e:
                    failed += 1
                    status = f"✗ [{i}/{len(selected_recipients)}] Ошибка: {recipient} - {str(e)}"
                    print(status)
                    log.write(f"{status}\n")
                    time.sleep(2)
            
            # Записываем итоги
            log.write("\n===== ИТОГИ =====\n")
            log.write(f"Всего получателей: {len(selected_recipients)}\n")
            log.write(f"Успешно отправлено: {successful}\n")
            log.write(f"Ошибок: {failed}\n")
            
            if selected_recipients and not stop_sending:
                success_rate = (successful / len(selected_recipients)) * 100
                log.write(f"Процент успеха: {success_rate:.1f}%\n")
        
        print(f"\nОтчет сохранен в файл: {log_filename}")
        
        # Выводим итоги
        print("\n" + "=" * 40)
        print("ИТОГИ:")
        print(f"Успешно отправлено: {successful}")
        print(f"Ошибок: {failed}")
        
        if selected_recipients and not stop_sending:
            success_rate = (successful / len(selected_recipients)) * 100
            print(f"Процент успеха: {success_rate:.1f}%")
        
        print("=" * 40)
    
    def main_menu(self):
        """Главное меню программы"""
        self.print_header()
        
        # Сканируем сессии
        self.account_manager.scan_for_sessions()
        
        while True:
            print("\nГЛАВНОЕ МЕНЮ:")
            
            if self.current_account and self.current_account.is_connected and self.current_account.is_authorized:
                print(f"Активный аккаунт: {self.current_account.name}")
                
                print("\n1. Отправить сообщения")
                print("2. Выбрать другой аккаунт")
                print("3. Выйти из аккаунта")
                print("4. Редактировать получателей")
                print("0. Выход из программы")
                
                choice = input("\nВыберите действие: ")
                
                if choice == "1":
                    self.send_messages()
                elif choice == "2":
                    self.select_account()
                elif choice == "3":
                    self.logout_current_account()
                elif choice == "4":
                    print(f"\nОткройте файл для редактирования: {self.recipient_manager.recipients_file}")
                    input("Нажмите Enter после редактирования...")
                    self.recipient_manager.load_recipients()
                    print(f"Загружено {len(self.recipient_manager.recipients)} получателей")
                elif choice == "0":
                    break
                else:
                    print("Неверный выбор")
            else:
                print("Аккаунт не подключен")
                
                print("\n1. Войти в аккаунт")
                print("2. Выбрать существующий аккаунт")
                print("0. Выход из программы")
                
                choice = input("\nВыберите действие: ")
                
                if choice == "1":
                    self.login_account()
                elif choice == "2":
                    self.select_account()
                elif choice == "0":
                    break
                else:
                    print("Неверный выбор")
        
        # Отключаемся от аккаунта при выходе
        if self.current_account and self.current_account.is_connected:
            self.current_account.disconnect()
        
        print("\nПрограмма завершена")


def check_and_install_telethon():
    """Проверяет и устанавливает библиотеку Telethon"""
    if TELETHON_AVAILABLE:
        return True
    
    print("Библиотека Telethon не установлена. Пытаемся установить...")
    
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])
        print("Telethon успешно установлен!")
        
        # Еще раз пытаемся импортировать
        try:
            global TelegramClient, FloodWaitError, SessionPasswordNeededError
            from telethon.sync import TelegramClient
            from telethon.errors import FloodWaitError, SessionPasswordNeededError
            return True
        except ImportError:
            pass
        
    except Exception as e:
        print(f"Ошибка при установке Telethon: {e}")
    
    print("Не удалось установить Telethon. Пожалуйста, установите его вручную:")
    print("pip install telethon")
    return False


def run_gui():
    """Запускает графический интерфейс"""
    root = tk.Tk()
    app = TelegramSenderGUI(root)
    root.mainloop()


def run_console():
    """Запускает консольный интерфейс"""
    console = TelegramSenderConsole()
    console.main_menu()


def main():
    """Основная функция программы"""
    # Проверяем наличие необходимых библиотек
    if not check_and_install_telethon():
        input("Нажмите Enter для выхода...")
        return
    
    # Определяем наличие графического интерфейса
    if HAVE_GUI and not IS_ANDROID:
        run_gui()
    else:
        run_console()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\nНепредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")