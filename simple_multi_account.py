#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ПРОСТОЙ МУЛЬТИ-АККАУНТ TELEGRAM ОТПРАВИТЕЛЬ
==========================================

Упрощенная версия с явными кнопками для:
- Добавления нового аккаунта
- Выхода из аккаунта
- Управления несколькими аккаунтами

Полностью работает на Windows 10 без ошибок.
"""

import os
import sys
import time
import json
import random
import logging
import traceback
from datetime import datetime

# Проверяем наличие библиотеки Telethon
try:
    from telethon.sync import TelegramClient
    from telethon.errors import FloodWaitError, SessionPasswordNeededError
except ImportError:
    print("\n❌ Библиотека Telethon не установлена!")
    print("Установите её командой:")
    print("pip install telethon")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

# Проверяем наличие Tkinter
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    HAVE_GUI = True
except ImportError:
    HAVE_GUI = False
    print("\n⚠️ Библиотека tkinter не установлена!")
    print("Будет использован консольный режим")

# API для Telegram
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

# Имена файлов и директорий
SESSIONS_DIR = "telegram_sessions"
CONFIG_FILE = "telegram_accounts.json"
RECIPIENTS_FILE = "telegram_recipients.txt"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Создаем директории если их нет
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Класс для работы с аккаунтами
class TelegramAccount:
    def __init__(self, name="", phone="", session_name=""):
        self.name = name
        self.phone = phone
        self.session_name = session_name or self._generate_session_name(phone)
        self.client = None
        self.is_connected = False
        self.is_authorized = False
    
    def _generate_session_name(self, phone):
        """Создает имя сессии из номера телефона"""
        if not phone:
            import uuid
            return f"session_{uuid.uuid4().hex[:8]}"
        return f"session_{phone.replace('+', '').replace(' ', '')}"
    
    def get_session_path(self):
        """Получает полный путь к файлу сессии"""
        return os.path.join(SESSIONS_DIR, self.session_name)
    
    def connect(self):
        """Подключается к Telegram API"""
        if self.client:
            self.disconnect()
        
        try:
            self.client = TelegramClient(self.get_session_path(), API_ID, API_HASH)
            self.client.connect()
            self.is_connected = True
            self.is_authorized = self.client.is_user_authorized()
            
            if self.is_authorized:
                # Получаем информацию о пользователе
                me = self.get_me()
                if me:
                    self.name = f"{me.first_name} {me.last_name or ''}".strip()
                    if me.username:
                        self.name += f" (@{me.username})"
                    self.phone = me.phone or self.phone
            
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            self.is_connected = False
            self.is_authorized = False
            return False
    
    def disconnect(self):
        """Отключается от Telegram API"""
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
            self.client = None
            self.is_connected = False
    
    def get_me(self):
        """Получает информацию о текущем пользователе"""
        if not self.client or not self.is_authorized:
            return None
        
        try:
            return self.client.get_me()
        except:
            return None
    
    def login(self, phone, code=None, password=None):
        """
        Выполняет вход в аккаунт Telegram
        
        Args:
            phone: Номер телефона
            code: Код подтверждения (если None, только запрос кода)
            password: Пароль 2FA (если None и требуется, вернет False)
        
        Returns:
            tuple: (success, step, extra_data)
                success: bool - успешность операции
                step: str - текущий шаг ('code_requested', 'code_needed', 'password_needed', 'success')
                extra_data: dict - дополнительные данные
        """
        if not self.client:
            if not self.connect():
                return False, 'error', {'error': 'connect_failed'}
        
        # Если уже авторизованы, то ничего не делаем
        if self.is_authorized:
            return True, 'success', {'me': self.get_me()}
        
        # Сохраняем номер телефона
        self.phone = phone
        
        try:
            # Если не указан код, запрашиваем его
            if code is None:
                # Запрашиваем код подтверждения
                logger.info(f"Отправка кода на номер {phone}")
                self.client.send_code_request(phone)
                return True, 'code_requested', {}
            
            # Пытаемся войти с кодом
            try:
                self.client.sign_in(phone, code)
                
                # Если успешно, сохраняем информацию
                self.is_authorized = True
                me = self.get_me()
                if me:
                    self.name = f"{me.first_name} {me.last_name or ''}".strip()
                    if me.username:
                        self.name += f" (@{me.username})"
                    self.phone = me.phone or self.phone
                
                return True, 'success', {'me': me}
                
            except SessionPasswordNeededError:
                # Если требуется пароль двухфакторной аутентификации
                if password is None:
                    return True, 'password_needed', {}
                
                # Пытаемся войти с паролем
                try:
                    self.client.sign_in(password=password)
                    
                    # Если успешно, сохраняем информацию
                    self.is_authorized = True
                    me = self.get_me()
                    if me:
                        self.name = f"{me.first_name} {me.last_name or ''}".strip()
                        if me.username:
                            self.name += f" (@{me.username})"
                        self.phone = me.phone or self.phone
                    
                    return True, 'success', {'me': me}
                except Exception as e:
                    return False, 'error', {'error': str(e), 'step': 'password_validation'}
            
            except Exception as e:
                return False, 'error', {'error': str(e), 'step': 'code_validation'}
                
        except Exception as e:
            return False, 'error', {'error': str(e), 'step': 'code_request'}
    
    def logout(self):
        """Выходит из аккаунта Telegram"""
        if not self.client or not self.is_authorized:
            return False
        
        try:
            result = self.client.log_out()
            
            # Удаляем файл сессии
            session_file = f"{self.get_session_path()}.session"
            if os.path.exists(session_file):
                os.remove(session_file)
            
            self.is_authorized = False
            return result
        except Exception as e:
            logger.error(f"Ошибка при выходе: {e}")
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
        if not self.client or not self.is_authorized:
            return False
        
        try:
            self.client.send_message(recipient, message)
            return True
        except FloodWaitError as e:
            logger.warning(f"Ограничение на отправку, ждем {e.seconds} сек")
            time.sleep(e.seconds)
            
            # Пробуем еще раз
            try:
                self.client.send_message(recipient, message)
                return True
            except Exception as e2:
                logger.error(f"Ошибка при повторной отправке: {e2}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при отправке: {e}")
            return False
    
    def to_dict(self):
        """Преобразует аккаунт в словарь для сохранения"""
        return {
            "name": self.name,
            "phone": self.phone,
            "session_name": self.session_name
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создает аккаунт из словаря"""
        return cls(
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            session_name=data.get("session_name", "")
        )

# Класс для управления аккаунтами
class AccountManager:
    def __init__(self):
        self.accounts = []
        self.current_account = None
        self.load_accounts()
    
    def load_accounts(self):
        """Загружает сохраненные аккаунты"""
        if not os.path.exists(CONFIG_FILE):
            return
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Загружаем аккаунты
                self.accounts = [TelegramAccount.from_dict(acc) for acc in data.get("accounts", [])]
                current_index = data.get("current_account_index", -1)
                
                # Устанавливаем текущий аккаунт
                if 0 <= current_index < len(self.accounts):
                    self.current_account = self.accounts[current_index]
                    
                logger.info(f"Загружено {len(self.accounts)} аккаунтов")
        except Exception as e:
            logger.error(f"Ошибка при загрузке аккаунтов: {e}")
    
    def save_accounts(self):
        """Сохраняет аккаунты в файл"""
        try:
            current_index = -1
            for i, acc in enumerate(self.accounts):
                if acc == self.current_account:
                    current_index = i
                    break
            
            data = {
                "accounts": [acc.to_dict() for acc in self.accounts],
                "current_account_index": current_index
            }
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Сохранено {len(self.accounts)} аккаунтов")
        except Exception as e:
            logger.error(f"Ошибка при сохранении аккаунтов: {e}")
    
    def add_account(self, account):
        """Добавляет аккаунт в список"""
        # Проверяем, есть ли аккаунт с таким же именем сессии
        for existing in self.accounts:
            if existing.session_name == account.session_name:
                # Обновляем существующий аккаунт
                existing.name = account.name
                existing.phone = account.phone
                self.current_account = existing
                self.save_accounts()
                return existing
        
        # Добавляем новый аккаунт
        self.accounts.append(account)
        self.current_account = account
        self.save_accounts()
        return account
    
    def remove_account(self, account):
        """Удаляет аккаунт из списка"""
        if account in self.accounts:
            self.accounts.remove(account)
            
            # Если удалили текущий аккаунт, сбрасываем его
            if account == self.current_account:
                self.current_account = None if not self.accounts else self.accounts[0]
            
            self.save_accounts()
            return True
        return False
    
    def connect_account(self, account):
        """Подключается к аккаунту"""
        if account.connect():
            self.current_account = account
            self.save_accounts()
            return True
        return False
    
    def scan_sessions(self):
        """Сканирует директорию с сессиями и добавляет новые аккаунты"""
        # Получаем список файлов сессий
        if not os.path.exists(SESSIONS_DIR):
            os.makedirs(SESSIONS_DIR)
            return []
        
        session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
        session_names = [os.path.splitext(f)[0] for f in session_files]
        
        # Получаем имена сессий для существующих аккаунтов
        existing_sessions = [acc.session_name for acc in self.accounts]
        
        # Находим новые сессии
        new_sessions = [s for s in session_names if s not in existing_sessions]
        new_accounts = []
        
        # Добавляем новые аккаунты
        for session_name in new_sessions:
            account = TelegramAccount(session_name=session_name)
            
            # Пробуем подключиться и получить информацию
            if account.connect() and account.is_authorized:
                me = account.get_me()
                if me:
                    account.name = f"{me.first_name} {me.last_name or ''}".strip()
                    if me.username:
                        account.name += f" (@{me.username})"
                    account.phone = me.phone or ""
                
                # Добавляем аккаунт
                self.accounts.append(account)
                new_accounts.append(account)
                logger.info(f"Добавлен аккаунт из сессии: {account.name}")
            
            # Отключаемся от аккаунта
            account.disconnect()
        
        # Если были добавлены новые аккаунты, сохраняем конфигурацию
        if new_accounts:
            self.save_accounts()
        
        return new_accounts

# Функции для работы с получателями
def load_recipients():
    """Загружает список получателей из файла"""
    if not os.path.exists(RECIPIENTS_FILE):
        # Создаем файл по умолчанию
        with open(RECIPIENTS_FILE, 'w', encoding='utf-8') as f:
            f.write("# Список получателей сообщений Telegram\n")
            f.write("# Добавляйте по одному получателю на строку\n")
            f.write("# Примеры:\n")
            f.write("# @username\n")
            f.write("# +79001234567\n")
        
        return []
    
    try:
        with open(RECIPIENTS_FILE, 'r', encoding='utf-8') as f:
            # Фильтруем пустые строки и комментарии
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        logger.error(f"Ошибка при загрузке получателей: {e}")
        return []

def save_recipients(recipients):
    """Сохраняет список получателей в файл"""
    try:
        with open(RECIPIENTS_FILE, 'w', encoding='utf-8') as f:
            f.write("# Список получателей сообщений Telegram\n")
            f.write("# Добавлен: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            for recipient in recipients:
                f.write(recipient + "\n")
        
        logger.info(f"Сохранено {len(recipients)} получателей")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении получателей: {e}")
        return False

# Класс графического интерфейса
class TelegramSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мульти-аккаунт Telegram")
        self.root.geometry("800x600")
        
        # Инициализируем менеджер аккаунтов
        self.account_manager = AccountManager()
        
        # Загружаем получателей
        self.recipients = load_recipients()
        
        # Флаг отправки сообщений
        self.sending = False
        
        # Создаем интерфейс
        self.create_interface()
        
        # Сканируем сессии
        new_accounts = self.account_manager.scan_sessions()
        if new_accounts:
            self.update_account_list()
    
    def create_interface(self):
        """Создает интерфейс программы"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель - управление аккаунтами
        account_frame = ttk.LabelFrame(main_frame, text="Аккаунты Telegram", padding=10)
        account_frame.pack(fill=tk.X, pady=5)
        
        # Фрейм для выбора аккаунта
        account_select_frame = ttk.Frame(account_frame)
        account_select_frame.pack(fill=tk.X, pady=5)
        
        # Выпадающий список аккаунтов
        ttk.Label(account_select_frame, text="Аккаунт:").pack(side=tk.LEFT, padx=5)
        
        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(account_select_frame, textvariable=self.account_var, width=30, state="readonly")
        self.account_combo.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.account_combo.bind("<<ComboboxSelected>>", self.on_account_select)
        
        # Кнопки для аккаунтов
        buttons_frame = ttk.Frame(account_select_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=5)
        
        # ДОБАВЛЕНЫ ЯВНЫЕ КНОПКИ ДЛЯ УПРАВЛЕНИЯ АККАУНТАМИ
        self.connect_button = ttk.Button(buttons_frame, text="Подключиться", command=self.connect_account)
        self.connect_button.pack(side=tk.LEFT, padx=2)
        
        self.add_account_button = ttk.Button(buttons_frame, text="Добавить аккаунт", command=self.add_account)
        self.add_account_button.pack(side=tk.LEFT, padx=2)
        
        self.logout_button = ttk.Button(buttons_frame, text="Выйти из аккаунта", command=self.logout_account)
        self.logout_button.pack(side=tk.LEFT, padx=2)
        
        # Информация об аккаунте
        info_frame = ttk.Frame(account_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Статус:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.status_label = ttk.Label(info_frame, text="Не подключен")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Средняя панель - получатели
        recipients_frame = ttk.LabelFrame(main_frame, text="Получатели", padding=10)
        recipients_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Список получателей
        recipients_list_frame = ttk.Frame(recipients_frame)
        recipients_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.recipients_listbox = tk.Listbox(recipients_list_frame, selectmode=tk.MULTIPLE)
        self.recipients_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        recipients_scrollbar = ttk.Scrollbar(recipients_list_frame, orient=tk.VERTICAL, command=self.recipients_listbox.yview)
        recipients_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recipients_listbox.config(yscrollcommand=recipients_scrollbar.set)
        
        # Кнопки для получателей
        recipients_buttons_frame = ttk.Frame(recipients_frame)
        recipients_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(recipients_buttons_frame, text="Добавить", command=self.add_recipient).pack(side=tk.LEFT, padx=2)
        ttk.Button(recipients_buttons_frame, text="Удалить выбранные", command=self.remove_recipients).pack(side=tk.LEFT, padx=2)
        ttk.Button(recipients_buttons_frame, text="Выбрать всех", command=self.select_all_recipients).pack(side=tk.LEFT, padx=2)
        ttk.Button(recipients_buttons_frame, text="Снять выбор", command=self.deselect_all_recipients).pack(side=tk.LEFT, padx=2)
        
        # Нижняя панель - отправка сообщений
        message_frame = ttk.LabelFrame(main_frame, text="Сообщение", padding=10)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Текст сообщения
        ttk.Label(message_frame, text="Текст сообщения:").pack(anchor=tk.W)
        
        self.message_text = scrolledtext.ScrolledText(message_frame, height=6)
        self.message_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопки отправки
        send_frame = ttk.Frame(message_frame)
        send_frame.pack(fill=tk.X, pady=5)
        
        self.send_button = ttk.Button(send_frame, text="Отправить сообщения", command=self.send_messages)
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(send_frame, text="Остановить отправку", command=self.stop_sending, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Статусная строка
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=5)
        
        # Обновляем список аккаунтов
        self.update_account_list()
        
        # Обновляем список получателей
        self.update_recipients_list()
        
        # Обновляем состояние интерфейса
        self.update_interface_state()
    
    def update_account_list(self):
        """Обновляет список аккаунтов"""
        accounts = ["Выберите аккаунт..."]
        accounts.extend([acc.name for acc in self.account_manager.accounts])
        accounts.append("+ Добавить новый аккаунт")
        
        self.account_combo["values"] = accounts
        
        # Выбираем текущий аккаунт
        if self.account_manager.current_account:
            index = self.account_manager.accounts.index(self.account_manager.current_account) + 1
            self.account_combo.current(index)
        else:
            self.account_combo.current(0)
    
    def update_recipients_list(self):
        """Обновляет список получателей"""
        self.recipients_listbox.delete(0, tk.END)
        for recipient in self.recipients:
            self.recipients_listbox.insert(tk.END, recipient)
    
    def update_interface_state(self):
        """Обновляет состояние интерфейса в зависимости от текущего аккаунта"""
        current_account = self.account_manager.current_account
        
        if current_account and current_account.is_connected and current_account.is_authorized:
            # Аккаунт подключен и авторизован
            self.status_label.config(text=f"Подключен: {current_account.name}")
            self.connect_button.config(state=tk.NORMAL)
            self.logout_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
        elif current_account and current_account.is_connected:
            # Аккаунт подключен, но не авторизован
            self.status_label.config(text="Подключен, но не авторизован")
            self.connect_button.config(state=tk.NORMAL)
            self.logout_button.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
        else:
            # Аккаунт не подключен
            self.status_label.config(text="Не подключен")
            self.connect_button.config(state=tk.NORMAL)
            self.logout_button.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
    
    def on_account_select(self, event=None):
        """Обработчик выбора аккаунта из списка"""
        selection = self.account_var.get()
        
        if selection == "Выберите аккаунт...":
            # Ничего не делаем
            pass
        elif selection == "+ Добавить новый аккаунт":
            # Добавляем новый аккаунт
            self.add_account()
        else:
            # Находим выбранный аккаунт
            for account in self.account_manager.accounts:
                if account.name == selection:
                    # Подключаемся к аккаунту
                    self.account_manager.current_account = account
                    self.update_interface_state()
                    break
    
    def connect_account(self):
        """Подключается к выбранному аккаунту"""
        account = self.account_manager.current_account
        
        if not account:
            messagebox.showerror("Ошибка", "Выберите аккаунт")
            return
        
        # Подключаемся к аккаунту
        self.status_var.set("Подключение к аккаунту...")
        
        if account.connect():
            self.account_manager.save_accounts()
            self.update_interface_state()
            self.status_var.set(f"Подключен к аккаунту: {account.name}")
        else:
            messagebox.showerror("Ошибка", "Не удалось подключиться к аккаунту")
            self.status_var.set("Ошибка подключения")
    
    def add_account(self):
        """Добавляет новый аккаунт"""
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление аккаунта")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрируем окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Создаем элементы интерфейса
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Номер телефона
        ttk.Label(frame, text="Номер телефона (с +):").pack(anchor=tk.W, pady=5)
        
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(frame, textvariable=phone_var)
        phone_entry.pack(fill=tk.X, pady=5)
        phone_entry.focus()
        
        # Код подтверждения (изначально скрыт)
        code_frame = ttk.Frame(frame)
        code_var = tk.StringVar()
        code_entry = ttk.Entry(frame, textvariable=code_var)
        
        # Пароль двухфакторной аутентификации (изначально скрыт)
        password_frame = ttk.Frame(frame)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(frame, textvariable=password_var, show="*")
        
        # Статус
        status_var = tk.StringVar(value="Введите номер телефона и нажмите 'Запросить код'")
        status_label = ttk.Label(frame, textvariable=status_var)
        status_label.pack(fill=tk.X, pady=10)
        
        # Текущий аккаунт
        account = TelegramAccount()
        
        # Обработчик запроса кода
        def request_code():
            phone = phone_var.get().strip()
            if not phone:
                messagebox.showerror("Ошибка", "Введите номер телефона")
                return
            
            # Подключаемся и запрашиваем код
            account.phone = phone
            success, step, data = account.login(phone)
            
            if not success:
                messagebox.showerror("Ошибка", f"Не удалось запросить код: {data.get('error', 'Неизвестная ошибка')}")
                return
            
            if step == 'success':
                # Уже авторизован
                self.account_manager.add_account(account)
                self.update_account_list()
                self.update_interface_state()
                messagebox.showinfo("Успех", "Аккаунт уже авторизован")
                dialog.destroy()
                return
            
            if step == 'code_requested':
                # Показываем поле для ввода кода
                request_button.pack_forget()
                
                ttk.Label(frame, text="Код подтверждения:").pack(anchor=tk.W, pady=5)
                code_entry.pack(fill=tk.X, pady=5)
                code_entry.focus()
                
                confirm_button.pack(pady=10)
                status_var.set("Введите код, отправленный в Telegram")
            else:
                messagebox.showerror("Ошибка", "Неизвестный шаг авторизации")
        
        # Обработчик подтверждения кода
        def confirm_code():
            code = code_var.get().strip()
            if not code:
                messagebox.showerror("Ошибка", "Введите код подтверждения")
                return
            
            # Подтверждаем код
            success, step, data = account.login(account.phone, code)
            
            if step == 'password_needed':
                # Показываем поле для ввода пароля
                confirm_button.pack_forget()
                
                ttk.Label(frame, text="Пароль двухфакторной аутентификации:").pack(anchor=tk.W, pady=5)
                password_entry.pack(fill=tk.X, pady=5)
                password_entry.focus()
                
                password_button.pack(pady=10)
                status_var.set("Введите пароль двухфакторной аутентификации")
                return
            
            if not success:
                messagebox.showerror("Ошибка", f"Не удалось войти: {data.get('error', 'Неизвестная ошибка')}")
                return
            
            if step == 'success':
                # Успешный вход
                self.account_manager.add_account(account)
                self.update_account_list()
                self.update_interface_state()
                messagebox.showinfo("Успех", f"Аккаунт {account.name} успешно добавлен")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Неизвестный шаг авторизации")
        
        # Обработчик подтверждения пароля
        def confirm_password():
            password = password_var.get()
            if not password:
                messagebox.showerror("Ошибка", "Введите пароль")
                return
            
            # Подтверждаем пароль
            success, step, data = account.login(account.phone, code_var.get(), password)
            
            if not success:
                messagebox.showerror("Ошибка", f"Не удалось войти: {data.get('error', 'Неизвестная ошибка')}")
                return
            
            if step == 'success':
                # Успешный вход
                self.account_manager.add_account(account)
                self.update_account_list()
                self.update_interface_state()
                messagebox.showinfo("Успех", f"Аккаунт {account.name} успешно добавлен")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Неизвестный шаг авторизации")
        
        # Кнопки
        request_button = ttk.Button(frame, text="Запросить код", command=request_code)
        request_button.pack(pady=10)
        
        confirm_button = ttk.Button(frame, text="Подтвердить код", command=confirm_code)
        password_button = ttk.Button(frame, text="Подтвердить пароль", command=confirm_password)
        
        ttk.Button(frame, text="Отмена", command=dialog.destroy).pack(side=tk.BOTTOM, pady=5)
    
    def logout_account(self):
        """Выход из текущего аккаунта"""
        account = self.account_manager.current_account
        
        if not account:
            messagebox.showerror("Ошибка", "Нет активного аккаунта")
            return
        
        if not messagebox.askyesno("Подтверждение", f"Вы действительно хотите выйти из аккаунта {account.name}?"):
            return
        
        # Выходим из аккаунта
        self.status_var.set("Выход из аккаунта...")
        
        if account.connect() and account.logout():
            # Удаляем аккаунт из списка
            self.account_manager.remove_account(account)
            self.update_account_list()
            self.update_interface_state()
            self.status_var.set("Выход из аккаунта выполнен")
        else:
            messagebox.showerror("Ошибка", "Не удалось выйти из аккаунта")
            self.status_var.set("Ошибка при выходе из аккаунта")
    
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
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Создаем элементы интерфейса
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Получатель (@username или телефон с '+'):").pack(anchor=tk.W, pady=5)
        
        recipient_var = tk.StringVar()
        recipient_entry = ttk.Entry(frame, textvariable=recipient_var)
        recipient_entry.pack(fill=tk.X, pady=5)
        recipient_entry.focus()
        
        # Обработчик добавления
        def add_recipient_action():
            recipient = recipient_var.get().strip()
            if not recipient:
                messagebox.showerror("Ошибка", "Введите получателя")
                return
            
            # Добавляем получателя
            if recipient not in self.recipients:
                self.recipients.append(recipient)
                save_recipients(self.recipients)
                self.update_recipients_list()
                self.status_var.set(f"Добавлен получатель: {recipient}")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Такой получатель уже есть в списке")
        
        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Добавить", command=add_recipient_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def remove_recipients(self):
        """Удаляет выбранных получателей"""
        selected = self.recipients_listbox.curselection()
        
        if not selected:
            messagebox.showerror("Ошибка", "Выберите получателей для удаления")
            return
        
        # Удаляем получателей (в обратном порядке, чтобы не сбивались индексы)
        for i in sorted(selected, reverse=True):
            del self.recipients[i]
        
        # Сохраняем и обновляем список
        save_recipients(self.recipients)
        self.update_recipients_list()
        self.status_var.set(f"Удалено получателей: {len(selected)}")
    
    def select_all_recipients(self):
        """Выбирает всех получателей"""
        self.recipients_listbox.selection_set(0, tk.END)
    
    def deselect_all_recipients(self):
        """Снимает выбор со всех получателей"""
        self.recipients_listbox.selection_clear(0, tk.END)
    
    def send_messages(self):
        """Отправляет сообщения выбранным получателям"""
        # Проверяем аккаунт
        account = self.account_manager.current_account
        if not account or not account.is_connected or not account.is_authorized:
            messagebox.showerror("Ошибка", "Не выбран активный аккаунт")
            return
        
        # Проверяем получателей
        selected = self.recipients_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите получателей")
            return
        
        # Получаем выбранных получателей
        selected_recipients = [self.recipients[i] for i in selected]
        
        # Проверяем сообщение
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Ошибка", "Введите текст сообщения")
            return
        
        # Подтверждение
        if not messagebox.askyesno("Подтверждение", f"Отправить сообщение {len(selected_recipients)} получателям?"):
            return
        
        # Подготовка к отправке
        self.sending = True
        self.send_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Запускаем отправку в отдельном потоке
        import threading
        threading.Thread(target=self.send_messages_thread, args=(account, selected_recipients, message), daemon=True).start()
    
    def send_messages_thread(self, account, recipients, message):
        """Отправляет сообщения в отдельном потоке"""
        successful = 0
        failed = 0
        
        # Создаем лог-файл
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"telegram_sent_{timestamp}.txt"
        
        with open(log_filename, 'w', encoding='utf-8') as log:
            log.write(f"===== ОТЧЕТ ОБ ОТПРАВКЕ СООБЩЕНИЙ =====\n\n")
            log.write(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"Аккаунт: {account.name}\n")
            log.write(f"Всего получателей: {len(recipients)}\n")
            log.write(f"Сообщение: {message}\n\n")
            
            # Отправляем сообщения
            for i, recipient in enumerate(recipients, 1):
                # Проверяем флаг отправки
                if not self.sending:
                    log.write("\nОтправка остановлена пользователем\n")
                    break
                
                # Статус
                self.status_var.set(f"Отправка {i}/{len(recipients)}: {recipient}")
                
                try:
                    # Отправляем сообщение
                    if account.send_message(recipient, message):
                        successful += 1
                        status = f"✓ [{i}/{len(recipients)}] Отправлено: {recipient}"
                        log.write(f"{status}\n")
                    else:
                        failed += 1
                        status = f"✗ [{i}/{len(recipients)}] Ошибка отправки: {recipient}"
                        log.write(f"{status}\n")
                except Exception as e:
                    failed += 1
                    status = f"✗ [{i}/{len(recipients)}] Ошибка: {recipient} - {str(e)}"
                    log.write(f"{status}\n")
                
                # Делаем паузу, если это не последнее сообщение
                if i < len(recipients) and self.sending:
                    delay = 2 + random.uniform(0.5, 1.5)
                    time.sleep(delay)
            
            # Записываем итоги
            log.write("\n===== ИТОГИ =====\n")
            log.write(f"Всего получателей: {len(recipients)}\n")
            log.write(f"Успешно отправлено: {successful}\n")
            log.write(f"Ошибок: {failed}\n")
            
            if recipients and self.sending:
                success_rate = (successful / len(recipients)) * 100
                log.write(f"Процент успеха: {success_rate:.1f}%\n")
        
        # Обновляем интерфейс
        self.sending = False
        self.send_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if successful + failed > 0:
            self.status_var.set(f"Отправка завершена: {successful} успешно, {failed} ошибок. Отчет: {log_filename}")
            messagebox.showinfo("Отправка завершена", f"Успешно: {successful}\nОшибок: {failed}\n\nОтчет сохранен в файл {log_filename}")
        else:
            self.status_var.set("Отправка отменена")
    
    def stop_sending(self):
        """Останавливает отправку сообщений"""
        if self.sending:
            if messagebox.askyesno("Подтверждение", "Остановить отправку сообщений?"):
                self.sending = False
                self.status_var.set("Останавливаем отправку...")

# Функция для консольного режима
def run_console_mode():
    """Запускает программу в консольном режиме"""
    print("=" * 60)
    print("МУЛЬТИ-АККАУНТ TELEGRAM ОТПРАВИТЕЛЬ")
    print("=" * 60)
    print("Версия для Windows и Android")
    print("=" * 60)
    
    # Инициализируем менеджер аккаунтов
    account_manager = AccountManager()
    
    # Сканируем сессии
    new_accounts = account_manager.scan_sessions()
    if new_accounts:
        print(f"\nНайдено {len(new_accounts)} новых аккаунтов:")
        for account in new_accounts:
            print(f"  - {account.name}")
    
    while True:
        print("\nГЛАВНОЕ МЕНЮ:")
        
        # Показываем текущий аккаунт
        current_account = account_manager.current_account
        if current_account:
            print(f"Текущий аккаунт: {current_account.name}")
            if current_account.is_connected and current_account.is_authorized:
                print("Статус: Подключен и авторизован")
            elif current_account.is_connected:
                print("Статус: Подключен, но не авторизован")
            else:
                print("Статус: Не подключен")
        else:
            print("Текущий аккаунт: Не выбран")
        
        # Выводим меню
        print("\nДоступные действия:")
        print("1. Добавить новый аккаунт")
        print("2. Выбрать аккаунт")
        print("3. Выйти из аккаунта")
        print("4. Подключиться к аккаунту")
        print("5. Отправить сообщения")
        print("6. Управление получателями")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ")
        
        if choice == "1":
            # Добавление нового аккаунта
            print("\n=== ДОБАВЛЕНИЕ АККАУНТА ===")
            phone = input("Введите номер телефона (с +): ")
            
            # Создаем аккаунт
            account = TelegramAccount(phone=phone)
            
            # Подключаемся и запрашиваем код
            success, step, data = account.login(phone)
            
            if not success:
                print(f"Ошибка: {data.get('error', 'Неизвестная ошибка')}")
                continue
            
            if step == 'success':
                # Уже авторизован
                account_manager.add_account(account)
                print(f"Аккаунт {account.name} добавлен (уже авторизован)")
                continue
            
            if step == 'code_requested':
                # Запрашиваем код
                code = input("Введите код из Telegram: ")
                
                # Подтверждаем код
                success, step, data = account.login(phone, code)
                
                if step == 'password_needed':
                    # Запрашиваем пароль
                    password = input("Введите пароль двухфакторной аутентификации: ")
                    
                    # Подтверждаем пароль
                    success, step, data = account.login(phone, code, password)
                
                if not success:
                    print(f"Ошибка: {data.get('error', 'Неизвестная ошибка')}")
                    continue
                
                if step == 'success':
                    # Успешный вход
                    account_manager.add_account(account)
                    print(f"Аккаунт {account.name} успешно добавлен")
                else:
                    print(f"Ошибка: Неизвестный шаг авторизации: {step}")
            
        elif choice == "2":
            # Выбор аккаунта
            if not account_manager.accounts:
                print("\nНет доступных аккаунтов")
                continue
            
            print("\n=== ВЫБОР АККАУНТА ===")
            for i, account in enumerate(account_manager.accounts, 1):
                print(f"{i}. {account.name}")
            
            try:
                index = int(input("\nВыберите аккаунт (номер): ")) - 1
                
                if 0 <= index < len(account_manager.accounts):
                    account_manager.current_account = account_manager.accounts[index]
                    account_manager.save_accounts()
                    print(f"Выбран аккаунт: {account_manager.current_account.name}")
                else:
                    print("Неверный номер аккаунта")
            except ValueError:
                print("Введите корректный номер")
            
        elif choice == "3":
            # Выход из аккаунта
            if not account_manager.current_account:
                print("\nНет активного аккаунта")
                continue
            
            print(f"\nВыход из аккаунта: {account_manager.current_account.name}")
            confirm = input("Вы уверены? (да/нет): ").lower()
            
            if confirm in ["да", "д", "yes", "y"]:
                account = account_manager.current_account
                
                if account.connect() and account.logout():
                    # Удаляем аккаунт из списка
                    account_manager.remove_account(account)
                    print("Выход из аккаунта выполнен")
                else:
                    print("Ошибка при выходе из аккаунта")
            
        elif choice == "4":
            # Подключение к аккаунту
            if not account_manager.current_account:
                print("\nНет активного аккаунта")
                continue
            
            print(f"\nПодключение к аккаунту: {account_manager.current_account.name}")
            
            if account_manager.current_account.connect():
                print("Подключение выполнено")
            else:
                print("Ошибка при подключении")
            
        elif choice == "5":
            # Отправка сообщений
            if not account_manager.current_account:
                print("\nНет активного аккаунта")
                continue
            
            account = account_manager.current_account
            
            if not account.is_connected:
                print("\nАккаунт не подключен")
                continue
            
            if not account.is_authorized:
                print("\nАккаунт не авторизован")
                continue
            
            # Загружаем получателей
            recipients = load_recipients()
            
            if not recipients:
                print(f"\nНет получателей. Добавьте их в файл {RECIPIENTS_FILE}")
                continue
            
            print("\n=== ОТПРАВКА СООБЩЕНИЙ ===")
            print(f"Аккаунт: {account.name}")
            print(f"Получатели ({len(recipients)}):")
            
            for i, recipient in enumerate(recipients, 1):
                print(f"{i}. {recipient}")
            
            # Выбор получателей
            print("\nВыберите получателей:")
            print("1. Все получатели")
            print("2. Выбрать по номерам")
            
            select_choice = input("\nВаш выбор (1/2): ")
            
            selected_recipients = []
            
            if select_choice == "1":
                selected_recipients = recipients
            elif select_choice == "2":
                try:
                    indices_str = input("\nВведите номера через запятую (например, 1,3,5): ")
                    indices = [int(idx.strip()) - 1 for idx in indices_str.split(",")]
                    
                    for idx in indices:
                        if 0 <= idx < len(recipients):
                            selected_recipients.append(recipients[idx])
                except:
                    print("Неверный формат ввода")
                    continue
            else:
                print("Неверный выбор")
                continue
            
            if not selected_recipients:
                print("Не выбраны получатели")
                continue
            
            # Запрашиваем сообщение
            print("\nВведите текст сообщения (для завершения нажмите Enter, затем Ctrl+Z или Ctrl+D):")
            message_lines = []
            try:
                while True:
                    line = input()
                    message_lines.append(line)
            except (EOFError, KeyboardInterrupt):
                pass
            
            message = "\n".join(message_lines)
            
            if not message.strip():
                print("Сообщение не может быть пустым")
                continue
            
            # Подтверждение
            print("\n" + "=" * 40)
            print(f"Аккаунт: {account.name}")
            print(f"Получателей: {len(selected_recipients)}")
            print(f"Текст: {message[:50]}{'...' if len(message) > 50 else ''}")
            print("=" * 40)
            
            confirm = input("\nНачать отправку сообщений? (да/нет): ").lower()
            
            if confirm not in ["да", "д", "yes", "y"]:
                print("Отправка отменена")
                continue
            
            # Отправка сообщений
            successful = 0
            failed = 0
            
            # Создаем лог-файл
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_filename = f"telegram_sent_{timestamp}.txt"
            
            with open(log_filename, 'w', encoding='utf-8') as log:
                log.write(f"===== ОТЧЕТ ОБ ОТПРАВКЕ СООБЩЕНИЙ =====\n\n")
                log.write(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log.write(f"Аккаунт: {account.name}\n")
                log.write(f"Всего получателей: {len(selected_recipients)}\n")
                log.write(f"Сообщение: {message}\n\n")
                
                print(f"\n===== НАЧАЛО ОТПРАВКИ =====")
                
                for i, recipient in enumerate(selected_recipients, 1):
                    try:
                        print(f"Отправка {i}/{len(selected_recipients)}: {recipient}")
                        
                        # Отправляем сообщение
                        if account.send_message(recipient, message):
                            successful += 1
                            status = f"✓ [{i}/{len(selected_recipients)}] Отправлено: {recipient}"
                            print(status)
                            log.write(f"{status}\n")
                        else:
                            failed += 1
                            status = f"✗ [{i}/{len(selected_recipients)}] Ошибка отправки: {recipient}"
                            print(status)
                            log.write(f"{status}\n")
                    except KeyboardInterrupt:
                        print("\nОтправка остановлена пользователем")
                        log.write("\nОтправка остановлена пользователем\n")
                        break
                    except Exception as e:
                        failed += 1
                        status = f"✗ [{i}/{len(selected_recipients)}] Ошибка: {recipient} - {str(e)}"
                        print(status)
                        log.write(f"{status}\n")
                    
                    # Делаем паузу
                    if i < len(selected_recipients):
                        delay = 2 + random.uniform(0.5, 1.5)
                        time.sleep(delay)
                
                # Записываем итоги
                log.write("\n===== ИТОГИ =====\n")
                log.write(f"Всего получателей: {len(selected_recipients)}\n")
                log.write(f"Успешно отправлено: {successful}\n")
                log.write(f"Ошибок: {failed}\n")
                
                if selected_recipients:
                    success_rate = (successful / len(selected_recipients)) * 100
                    log.write(f"Процент успеха: {success_rate:.1f}%\n")
            
            # Выводим итоги
            print("\n" + "=" * 40)
            print("ИТОГИ:")
            print(f"Успешно отправлено: {successful}")
            print(f"Ошибок: {failed}")
            
            if selected_recipients:
                success_rate = (successful / len(selected_recipients)) * 100
                print(f"Процент успеха: {success_rate:.1f}%")
            
            print("=" * 40)
            print(f"Отчет сохранен в файл: {log_filename}")
            
        elif choice == "6":
            # Управление получателями
            recipients = load_recipients()
            
            while True:
                print("\n=== УПРАВЛЕНИЕ ПОЛУЧАТЕЛЯМИ ===")
                print(f"Всего получателей: {len(recipients)}")
                
                for i, recipient in enumerate(recipients, 1):
                    print(f"{i}. {recipient}")
                
                print("\nДействия:")
                print("1. Добавить получателя")
                print("2. Удалить получателя")
                print("3. Вернуться в главное меню")
                
                sub_choice = input("\nВыберите действие: ")
                
                if sub_choice == "1":
                    # Добавление получателя
                    recipient = input("\nВведите получателя (@username или телефон с '+'): ")
                    
                    if recipient and recipient not in recipients:
                        recipients.append(recipient)
                        save_recipients(recipients)
                        print(f"Получатель {recipient} добавлен")
                    elif recipient in recipients:
                        print("Такой получатель уже есть в списке")
                    else:
                        print("Некорректный получатель")
                
                elif sub_choice == "2":
                    # Удаление получателя
                    try:
                        index = int(input("\nВведите номер получателя для удаления: ")) - 1
                        
                        if 0 <= index < len(recipients):
                            recipient = recipients[index]
                            del recipients[index]
                            save_recipients(recipients)
                            print(f"Получатель {recipient} удален")
                        else:
                            print("Неверный номер получателя")
                    except ValueError:
                        print("Введите корректный номер")
                
                elif sub_choice == "3":
                    # Возврат в главное меню
                    break
                
                else:
                    print("Неверный выбор")
            
        elif choice == "0":
            # Выход из программы
            print("\nВыход из программы...")
            break
        
        else:
            print("\nНеверный выбор")

def main():
    """Главная функция программы"""
    # Проверяем наличие tkinter
    if HAVE_GUI:
        # Запускаем графический интерфейс
        root = tk.Tk()
        app = TelegramSenderApp(root)
        root.mainloop()
    else:
        # Запускаем консольный режим
        run_console_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\nНепредвиденная ошибка: {e}")
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")