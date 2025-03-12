#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ПРОСТОЙ TELEGRAM ОТПРАВИТЕЛЬ ДЛЯ ТЕЛЕФОНОВ
==========================================

Версия, оптимизированная для мобильных устройств:
- Работает на Android через Termux или Pydroid 3
- Поддерживает работу с несколькими аккаунтами
- Имеет простой и понятный интерфейс
- Не требует дополнительных библиотек кроме Telethon

ИСПОЛЬЗОВАНИЕ:
1. Установите Python на телефон (Termux или Pydroid 3)
2. Установите библиотеку: pip install telethon
3. Запустите скрипт: python mobile_easy_sender.py
"""

import os
import sys
import time
import json
import random
import logging
from datetime import datetime

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# API для Telegram
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

# Имена файлов
CONFIG_FILE = "telegram_config.json"
SESSIONS_DIR = "telegram_sessions"
RECIPIENTS_FILE = "recipients.txt"

# Проверяем наличие библиотеки Telethon
try:
    from telethon.sync import TelegramClient
    from telethon.errors import FloodWaitError, SessionPasswordNeededError
except ImportError:
    print("\n❌ Библиотека Telethon не установлена!")
    print("Установите её командой:")
    print("pip install telethon")
    sys.exit(1)

# Проверяем, запущено ли приложение на Android
IS_ANDROID = False
try:
    if "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ:
        IS_ANDROID = True
        print("📱 Обнаружена Android система")
except:
    pass

# Создаем директории если их нет
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Класс для работы с аккаунтами
class Account:
    def __init__(self, name="", phone="", session_name=""):
        self.name = name
        self.phone = phone
        self.session_name = session_name or self._generate_session_name(phone)
        self.client = None
    
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
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        """Отключается от Telegram API"""
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
            self.client = None
    
    def is_authorized(self):
        """Проверяет, авторизован ли клиент"""
        if not self.client:
            return False
        
        try:
            return self.client.is_user_authorized()
        except:
            return False
    
    def get_me(self):
        """Получает информацию о текущем пользователе"""
        if not self.client or not self.is_authorized():
            return None
        
        try:
            return self.client.get_me()
        except:
            return None
    
    def login(self, phone=None, code_callback=None, password_callback=None):
        """
        Выполняет вход в аккаунт Telegram
        
        Args:
            phone: Номер телефона (если не указан, используется сохраненный)
            code_callback: Функция для получения кода подтверждения
            password_callback: Функция для получения пароля 2FA
        
        Returns:
            bool: Успешность входа
        """
        if not self.client:
            if not self.connect():
                return False
        
        # Если уже авторизованы, то ничего не делаем
        if self.is_authorized():
            me = self.get_me()
            if me:
                self.name = f"{me.first_name} {me.last_name or ''}".strip()
                if me.username:
                    self.name += f" (@{me.username})"
                self.phone = me.phone or self.phone
            return True
        
        # Используем переданный номер телефона или сохраненный
        phone = phone or self.phone
        if not phone:
            logger.error("Номер телефона не указан")
            return False
        
        self.phone = phone
        
        try:
            # Запрашиваем код подтверждения
            logger.info(f"Отправка кода на номер {phone}")
            self.client.send_code_request(phone)
            
            # Получаем код от пользователя
            if not code_callback:
                logger.error("Не указана функция для получения кода")
                return False
            
            code = code_callback()
            
            # Пытаемся войти
            try:
                self.client.sign_in(phone, code)
                
                # Если успешно, сохраняем информацию
                me = self.get_me()
                if me:
                    self.name = f"{me.first_name} {me.last_name or ''}".strip()
                    if me.username:
                        self.name += f" (@{me.username})"
                    self.phone = me.phone or self.phone
                
                return True
                
            except SessionPasswordNeededError:
                # Если требуется пароль двухфакторной аутентификации
                if not password_callback:
                    logger.error("Не указана функция для получения пароля")
                    return False
                
                password = password_callback()
                self.client.sign_in(password=password)
                
                # Если успешно, сохраняем информацию
                me = self.get_me()
                if me:
                    self.name = f"{me.first_name} {me.last_name or ''}".strip()
                    if me.username:
                        self.name += f" (@{me.username})"
                    self.phone = me.phone or self.phone
                
                return True
                
        except Exception as e:
            logger.error(f"Ошибка при входе: {e}")
            return False
    
    def logout(self):
        """Выходит из аккаунта Telegram"""
        if not self.client or not self.is_authorized():
            return False
        
        try:
            result = self.client.log_out()
            
            # Удаляем файл сессии
            session_file = f"{self.get_session_path()}.session"
            if os.path.exists(session_file):
                os.remove(session_file)
            
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
        if not self.client or not self.is_authorized():
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


# Класс для управления конфигурацией
class Config:
    def __init__(self):
        self.accounts = []
        self.current_account_index = -1
        self.load()
    
    def load(self):
        """Загружает конфигурацию из файла"""
        if not os.path.exists(CONFIG_FILE):
            return
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Загружаем аккаунты
                self.accounts = [Account.from_dict(acc) for acc in data.get("accounts", [])]
                self.current_account_index = data.get("current_account_index", -1)
                
                # Проверяем индекс
                if self.current_account_index >= len(self.accounts):
                    self.current_account_index = -1
                
                logger.info(f"Загружено {len(self.accounts)} аккаунтов")
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации: {e}")
    
    def save(self):
        """Сохраняет конфигурацию в файл"""
        try:
            data = {
                "accounts": [acc.to_dict() for acc in self.accounts],
                "current_account_index": self.current_account_index
            }
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Сохранено {len(self.accounts)} аккаунтов")
        except Exception as e:
            logger.error(f"Ошибка при сохранении конфигурации: {e}")
    
    def get_current_account(self):
        """Возвращает текущий аккаунт"""
        if 0 <= self.current_account_index < len(self.accounts):
            return self.accounts[self.current_account_index]
        return None
    
    def set_current_account(self, index):
        """Устанавливает текущий аккаунт"""
        if 0 <= index < len(self.accounts):
            self.current_account_index = index
            self.save()
            return True
        return False
    
    def add_account(self, account):
        """Добавляет аккаунт в список"""
        self.accounts.append(account)
        self.current_account_index = len(self.accounts) - 1
        self.save()
    
    def remove_account(self, index):
        """Удаляет аккаунт из списка"""
        if 0 <= index < len(self.accounts):
            del self.accounts[index]
            
            # Корректируем текущий индекс
            if self.current_account_index >= len(self.accounts):
                self.current_account_index = len(self.accounts) - 1
            
            self.save()
            return True
        return False
    
    def scan_sessions(self):
        """Сканирует директорию с сессиями и добавляет новые аккаунты"""
        # Получаем список файлов сессий
        session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
        
        # Получаем имена сессий без расширения
        session_names = [os.path.splitext(f)[0] for f in session_files]
        
        # Получаем имена сессий для существующих аккаунтов
        existing_sessions = [acc.session_name for acc in self.accounts]
        
        # Находим новые сессии
        new_sessions = [s for s in session_names if s not in existing_sessions]
        
        # Добавляем новые аккаунты
        for session_name in new_sessions:
            account = Account(session_name=session_name)
            
            # Пробуем подключиться и получить информацию
            if account.connect() and account.is_authorized():
                me = account.get_me()
                if me:
                    account.name = f"{me.first_name} {me.last_name or ''}".strip()
                    if me.username:
                        account.name += f" (@{me.username})"
                    account.phone = me.phone or ""
                
                # Добавляем аккаунт
                self.accounts.append(account)
                logger.info(f"Добавлен аккаунт из сессии: {account.name}")
            
            # Отключаемся от аккаунта
            account.disconnect()
        
        # Если были добавлены новые аккаунты, сохраняем конфигурацию
        if new_sessions:
            self.save()


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


# Вспомогательные функции для вывода текста с учетом мобильного устройства
def clear_screen():
    """Очищает экран терминала"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Выводит заголовок программы"""
    clear_screen()
    print("=" * 50)
    print("TELEGRAM ОТПРАВИТЕЛЬ ДЛЯ ТЕЛЕФОНОВ")
    print("=" * 50)
    print("Версия 1.0 (для Android) | by Replit Team")
    print("=" * 50)

def print_menu(title, options):
    """
    Выводит меню с опциями
    
    Args:
        title (str): Заголовок меню
        options (list): Список опций в формате [(key, text), ...]
    """
    print(f"\n{title}")
    print("-" * len(title))
    
    for key, text in options:
        print(f"{key}. {text}")


# Основные функции для работы с программой
def login_account():
    """Функция для входа в аккаунт Telegram"""
    print_header()
    print("\n=== ВХОД В АККАУНТ TELEGRAM ===")
    
    # Запрашиваем номер телефона
    phone = input("\nВведите номер телефона (с +): ")
    
    # Создаем новый аккаунт
    account = Account(phone=phone)
    
    # Функция для получения кода
    def code_callback():
        return input("Введите код из Telegram: ")
    
    # Функция для получения пароля
    def password_callback():
        return input("Введите пароль двухфакторной аутентификации: ")
    
    # Пытаемся войти
    if account.connect() and account.login(phone, code_callback, password_callback):
        print(f"\n✅ Успешный вход в аккаунт: {account.name}")
        return account
    else:
        print("\n❌ Не удалось войти в аккаунт")
        return None

def select_account(config):
    """Функция для выбора аккаунта"""
    print_header()
    print("\n=== ВЫБОР АККАУНТА ===")
    
    if not config.accounts:
        print("\nНет доступных аккаунтов. Сначала войдите в аккаунт.")
        input("\nНажмите Enter для продолжения...")
        return False
    
    print("\nДоступные аккаунты:")
    for i, account in enumerate(config.accounts):
        marker = "✓" if i == config.current_account_index else " "
        print(f"{marker} {i+1}. {account.name} ({account.phone})")
    
    try:
        choice = int(input("\nВыберите аккаунт (номер): ")) - 1
        
        if 0 <= choice < len(config.accounts):
            config.set_current_account(choice)
            print(f"\n✅ Выбран аккаунт: {config.accounts[choice].name}")
            return True
        else:
            print("\n❌ Неверный номер аккаунта")
            input("\nНажмите Enter для продолжения...")
            return False
    except ValueError:
        print("\n❌ Введите корректный номер")
        input("\nНажмите Enter для продолжения...")
        return False

def logout_account(config):
    """Функция для выхода из аккаунта"""
    print_header()
    print("\n=== ВЫХОД ИЗ АККАУНТА ===")
    
    account = config.get_current_account()
    if not account:
        print("\nНет выбранного аккаунта")
        input("\nНажмите Enter для продолжения...")
        return False
    
    print(f"\nТекущий аккаунт: {account.name}")
    confirm = input("\nВы действительно хотите выйти из этого аккаунта? (да/нет): ").lower()
    
    if confirm in ["да", "д", "yes", "y"]:
        if account.connect() and account.logout():
            print("\n✅ Успешный выход из аккаунта")
            
            # Удаляем аккаунт из списка
            config.remove_account(config.current_account_index)
            
            input("\nНажмите Enter для продолжения...")
            return True
        else:
            print("\n❌ Не удалось выйти из аккаунта")
            input("\nНажмите Enter для продолжения...")
            return False
    else:
        print("\nВыход отменен")
        input("\nНажмите Enter для продолжения...")
        return False

def view_recipients():
    """Функция для просмотра списка получателей"""
    print_header()
    print("\n=== СПИСОК ПОЛУЧАТЕЛЕЙ ===")
    
    recipients = load_recipients()
    
    if not recipients:
        print(f"\nСписок получателей пуст. Добавьте получателей в файл {RECIPIENTS_FILE}")
        input("\nНажмите Enter для продолжения...")
        return
    
    print(f"\nВсего получателей: {len(recipients)}")
    for i, recipient in enumerate(recipients, 1):
        print(f"{i}. {recipient}")
    
    print(f"\nДля редактирования списка откройте файл {RECIPIENTS_FILE}")
    input("\nНажмите Enter для продолжения...")

def send_messages(config):
    """Функция для отправки сообщений"""
    print_header()
    print("\n=== ОТПРАВКА СООБЩЕНИЙ ===")
    
    # Проверяем аккаунт
    account = config.get_current_account()
    if not account:
        print("\n❌ Нет выбранного аккаунта")
        input("\nНажмите Enter для продолжения...")
        return
    
    # Подключаемся к аккаунту
    if not account.connect():
        print("\n❌ Не удалось подключиться к Telegram")
        input("\nНажмите Enter для продолжения...")
        return
    
    # Проверяем авторизацию
    if not account.is_authorized():
        print("\n❌ Аккаунт не авторизован. Выполните вход.")
        input("\nНажмите Enter для продолжения...")
        account.disconnect()
        return
    
    # Загружаем получателей
    recipients = load_recipients()
    
    if not recipients:
        print(f"\n❌ Список получателей пуст. Добавьте получателей в файл {RECIPIENTS_FILE}")
        input("\nНажмите Enter для продолжения...")
        account.disconnect()
        return
    
    # Выводим информацию
    me = account.get_me()
    if me:
        print(f"\nОтправка с аккаунта: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
    else:
        print(f"\nОтправка с аккаунта: {account.name}")
    
    print(f"Всего получателей: {len(recipients)}")
    
    # Выбор получателей
    print("\nВыберите получателей:")
    print("1. Все получатели")
    print("2. Выбрать по номерам")
    
    choice = input("\nВаш выбор (1/2): ")
    
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
            print("\n❌ Неверный формат ввода")
            input("\nНажмите Enter для продолжения...")
            account.disconnect()
            return
    else:
        print("\n❌ Неверный выбор")
        input("\nНажмите Enter для продолжения...")
        account.disconnect()
        return
    
    if not selected_recipients:
        print("\n❌ Не выбраны получатели")
        input("\nНажмите Enter для продолжения...")
        account.disconnect()
        return
    
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
        print("\n❌ Сообщение не может быть пустым")
        input("\nНажмите Enter для продолжения...")
        account.disconnect()
        return
    
    # Подтверждение
    print("\n" + "=" * 40)
    print(f"Аккаунт: {account.name}")
    print(f"Получателей: {len(selected_recipients)}")
    print(f"Текст: {message[:50]}{'...' if len(message) > 50 else ''}")
    print("=" * 40)
    
    confirm = input("\nНачать отправку сообщений? (да/нет): ").lower()
    if confirm not in ["да", "yes", "y", "д"]:
        print("\n❌ Отправка отменена")
        input("\nНажмите Enter для продолжения...")
        account.disconnect()
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
        log.write(f"Аккаунт: {account.name}\n")
        log.write(f"Всего получателей: {len(selected_recipients)}\n")
        log.write(f"Сообщение: {message}\n\n")
        
        print(f"\n===== НАЧАЛО ОТПРАВКИ =====")
        
        for i, recipient in enumerate(selected_recipients, 1):
            try:
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
    
    # Отключаемся от аккаунта
    account.disconnect()
    
    input("\nНажмите Enter для продолжения...")

def main_menu():
    """Главное меню программы"""
    # Инициализируем конфигурацию
    config = Config()
    
    # Сканируем сессии
    config.scan_sessions()
    
    while True:
        print_header()
        
        # Показываем текущий аккаунт
        account = config.get_current_account()
        if account:
            print(f"\nТекущий аккаунт: {account.name}")
        else:
            print("\nАккаунт не выбран")
        
        # Выводим меню
        print_menu("ГЛАВНОЕ МЕНЮ", [
            ("1", "Войти в новый аккаунт"),
            ("2", "Выбрать аккаунт"),
            ("3", "Выйти из аккаунта"),
            ("4", "Отправить сообщения"),
            ("5", "Просмотреть получателей"),
            ("0", "Выход")
        ])
        
        choice = input("\nВыберите действие: ")
        
        if choice == "1":
            # Вход в новый аккаунт
            account = login_account()
            if account:
                config.add_account(account)
        elif choice == "2":
            # Выбор аккаунта
            select_account(config)
        elif choice == "3":
            # Выход из аккаунта
            logout_account(config)
        elif choice == "4":
            # Отправка сообщений
            send_messages(config)
        elif choice == "5":
            # Просмотр получателей
            view_recipients()
        elif choice == "0":
            # Выход из программы
            break
        else:
            print("\n❌ Неверный выбор")
            input("\nНажмите Enter для продолжения...")

# Запуск программы
if __name__ == "__main__":
    try:
        main_menu()
        print("\nПрограмма завершена")
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\n\nНепредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")