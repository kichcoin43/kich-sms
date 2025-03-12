#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ОТПРАВИТЕЛЬ СООБЩЕНИЙ TELEGRAM ДЛЯ WINDOWS 10
=============================================

Простая, надежная версия отправителя сообщений для Windows 10.
Работает без проблем на Windows 10 и не требует дополнительных библиотек.

ИСПОЛЬЗОВАНИЕ:
1. Скачайте этот файл на свой компьютер
2. Установите Python 3.8 или новее с сайта python.org
3. Установите библиотеки: pip install telethon
4. Запустите: python windows10_sender.py

Программа автоматически создаст файл для списка получателей
и поможет вам войти в аккаунт Telegram, если нужно.
"""

import os
import sys
import time
import random
import logging
import datetime
import traceback

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s', 
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('telegram_sender.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Константы для API
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

# Имя файла сессии
SESSION_NAME = "windows10_session"

# Файл с получателями
RECIPIENTS_FILE = "recipients.txt"

def check_telethon():
    """Проверяет установлена ли библиотека Telethon"""
    try:
        import telethon
        logger.info(f"Telethon установлен (версия {telethon.__version__})")
        return True
    except ImportError:
        logger.error("Telethon не установлен!")
        logger.info("Пожалуйста, установите библиотеку командой:")
        logger.info("pip install telethon")
        return False

def create_recipients_file():
    """Создает файл получателей, если он не существует"""
    if not os.path.exists(RECIPIENTS_FILE):
        try:
            with open(RECIPIENTS_FILE, 'w', encoding='utf-8') as f:
                f.write("# Список получателей (по одному на строку)\n")
                f.write("# Можно указывать @username или номер телефона\n")
                f.write("# Пример:\n")
                f.write("# @username\n")
                f.write("# +79001234567\n")
            logger.info(f"Создан файл получателей: {RECIPIENTS_FILE}")
            logger.info(f"Пожалуйста, добавьте получателей в файл {RECIPIENTS_FILE}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при создании файла: {e}")
            return False
    return True

def load_recipients():
    """Загрузка получателей из файла"""
    try:
        with open(RECIPIENTS_FILE, 'r', encoding='utf-8') as f:
            # Фильтруем пустые строки и комментарии
            recipients = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    recipients.append(line)
            return recipients
    except Exception as e:
        logger.error(f"Ошибка загрузки получателей: {e}")
        return []

def connect_to_telegram():
    """Подключение к Telegram API"""
    try:
        from telethon.sync import TelegramClient
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        client.connect()
        return client
    except Exception as e:
        logger.error(f"Ошибка подключения к Telegram: {e}")
        traceback.print_exc()
        return None

def login_telegram(client):
    """Вход в аккаунт Telegram"""
    if client.is_user_authorized():
        me = client.get_me()
        logger.info(f"Вы уже авторизованы как: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
        return True
    
    try:
        logger.info("Требуется вход в аккаунт Telegram")
        phone = input("Введите номер телефона (с +): ")
        client.send_code_request(phone)
        code = input("Введите код подтверждения из Telegram: ")
        client.sign_in(phone, code)
        
        # Проверяем, нужен ли пароль двухфакторной аутентификации
        if client.is_user_authorized():
            me = client.get_me()
            logger.info(f"Успешный вход в аккаунт: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
            return True
        else:
            password = input("Введите пароль двухфакторной аутентификации: ")
            client.sign_in(password=password)
            me = client.get_me()
            logger.info(f"Успешный вход в аккаунт: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
            return True
    except Exception as e:
        logger.error(f"Ошибка входа в аккаунт: {e}")
        traceback.print_exc()
        return False

def send_messages(client, message, recipients):
    """Отправка сообщений получателям"""
    from telethon.errors import FloodWaitError
    
    # Счетчики
    successful = 0
    failed = 0
    
    # Логирование для результатов
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"results_{timestamp}.txt"
    
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write(f"===== РЕЗУЛЬТАТЫ ОТПРАВКИ =====\n")
        log_file.write(f"Дата и время: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Всего получателей: {len(recipients)}\n")
        log_file.write(f"Текст сообщения: {message}\n\n")
        log_file.write("Детальный отчет:\n")
        
        logger.info(f"\n===== НАЧАЛО ОТПРАВКИ =====")
        
        for i, recipient in enumerate(recipients, 1):
            try:
                # Отправляем сообщение
                client.send_message(recipient, message)
                
                # Отмечаем успех
                successful += 1
                result = f"✓ [{i}/{len(recipients)}] Отправлено: {recipient}"
                logger.info(result)
                log_file.write(f"{result}\n")
                
                # Делаем паузу
                if i < len(recipients):
                    delay = 2 + random.uniform(0.5, 2.0)
                    time.sleep(delay)
                    
            except FloodWaitError as e:
                # Ограничение на частоту отправки
                wait_seconds = e.seconds
                
                if wait_seconds <= 60:
                    logger.warning(f"⚠️ Пауза {wait_seconds} сек из-за ограничения...")
                    
                    # Ждем указанное время
                    time.sleep(wait_seconds)
                    
                    # Повторная попытка
                    try:
                        client.send_message(recipient, message)
                        successful += 1
                        result = f"✓ [{i}/{len(recipients)}] Отправлено (после паузы): {recipient}"
                        logger.info(result)
                        log_file.write(f"{result}\n")
                        continue
                    except Exception as e2:
                        pass
                
                failed += 1
                result = f"✗ [{i}/{len(recipients)}] Ошибка (FloodWait {wait_seconds}с): {recipient}"
                logger.error(result)
                log_file.write(f"{result}\n")
                
            except Exception as e:
                # Прочие ошибки
                failed += 1
                result = f"✗ [{i}/{len(recipients)}] Ошибка: {recipient} - {str(e)}"
                logger.error(result)
                log_file.write(f"{result}\n")
                time.sleep(2)
        
        # Итоги
        logger.info("\n===== РЕЗУЛЬТАТЫ =====")
        logger.info(f"Всего получателей: {len(recipients)}")
        logger.info(f"Успешно отправлено: {successful}")
        logger.info(f"Ошибок: {failed}")
        
        log_file.write(f"\n===== ИТОГИ =====\n")
        log_file.write(f"Всего получателей: {len(recipients)}\n")
        log_file.write(f"Успешно отправлено: {successful}\n")
        log_file.write(f"Ошибок: {failed}\n")
        
        if recipients:
            success_rate = (successful / len(recipients)) * 100
            logger.info(f"Процент успеха: {success_rate:.1f}%")
            log_file.write(f"Процент успеха: {success_rate:.1f}%\n")
    
    logger.info(f"Отчет сохранен в файл: {log_filename}")
    return successful, failed

def main():
    """Основная функция программы"""
    print("=" * 60)
    print("ОТПРАВИТЕЛЬ СООБЩЕНИЙ TELEGRAM ДЛЯ WINDOWS 10")
    print("=" * 60)
    print("Версия 1.0 | Март 2025")
    print("=" * 60)
    
    # Проверяем наличие библиотеки Telethon
    if not check_telethon():
        print("\nНевозможно продолжить без библиотеки Telethon.")
        print("Пожалуйста, установите ее командой: pip install telethon")
        input("\nНажмите Enter для выхода...")
        return
    
    # Проверяем/создаем файл получателей
    if not create_recipients_file():
        print("\nПожалуйста, добавьте получателей в файл и запустите программу снова.")
        input("\nНажмите Enter для выхода...")
        return
    
    # Загружаем получателей
    recipients = load_recipients()
    if not recipients:
        print("\nНе удалось загрузить получателей из файла.")
        print(f"Убедитесь, что файл {RECIPIENTS_FILE} содержит список получателей.")
        input("\nНажмите Enter для выхода...")
        return
    
    logger.info(f"Загружено {len(recipients)} получателей")
    
    # Подключаемся к Telegram
    client = connect_to_telegram()
    if not client:
        print("\nНе удалось подключиться к Telegram API.")
        input("\nНажмите Enter для выхода...")
        return
    
    # Проверяем авторизацию
    if not login_telegram(client):
        print("\nНе удалось войти в аккаунт Telegram.")
        client.disconnect()
        input("\nНажмите Enter для выхода...")
        return
    
    # Запрашиваем текст сообщения
    print("\nВведите текст сообщения (для завершения ввода нажмите Enter, затем Ctrl+D или Ctrl+Z):")
    message_lines = []
    try:
        while True:
            line = input()
            message_lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    
    message = "\n".join(message_lines)
    
    if not message.strip():
        print("\nСообщение не может быть пустым.")
        client.disconnect()
        input("\nНажмите Enter для выхода...")
        return
    
    # Подтверждение отправки
    print("\n" + "=" * 40)
    print(f"Получателей: {len(recipients)}")
    print(f"Текст сообщения: {message[:50]}{'...' if len(message) > 50 else ''}")
    print("=" * 40)
    
    confirm = input("\nНачать отправку сообщений? (да/нет): ").lower()
    if confirm not in ["да", "yes", "y", "д"]:
        print("\nОтправка отменена.")
        client.disconnect()
        input("\nНажмите Enter для выхода...")
        return
    
    # Отправляем сообщения
    try:
        successful, failed = send_messages(client, message, recipients)
        
        print("\n" + "=" * 40)
        print(f"Отправка завершена!")
        print(f"Успешно: {successful} | Ошибок: {failed}")
        print("=" * 40)
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        traceback.print_exc()
    finally:
        # Отключаемся
        client.disconnect()
    
    # Задержка перед выходом
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nПрограмма прервана пользователем")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        traceback.print_exc()
        input("\nПроизошла ошибка. Нажмите Enter для выхода...")