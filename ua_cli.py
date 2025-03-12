#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
КОНСОЛЬНА ВЕРСІЯ ВІДПРАВНИКА TELEGRAM ДЛЯ УКРАЇНИ
================================================

Консольна версія програми для відправки повідомлень українським користувачам Telegram.
Призначена для використання в середовищах без графічного інтерфейсу або для автоматизації.

ВИКОРИСТАННЯ:
   python ua_cli.py --phone="+380xxxxxxxxx" --code="12345" --message="Ваше повідомлення"
   python ua_cli.py --session="ua_session" --message="Ваше повідомлення" --recipients="recipients.txt"

ПАРАМЕТРИ:
   --phone - номер телефону з '+' на початку (наприклад, +380xxxxxxxxx)
   --code - код підтвердження з Telegram
   --message - текст повідомлення (у лапках)
   --password - пароль двофакторної аутентифікації (якщо є)
   --recipients - шлях до файлу зі списком одержувачів (за замовчуванням "recipients.txt")
   --delay - затримка між повідомленнями у секундах (за замовчуванням 2.0)
   --session - ім'я файлу сесії (за замовчуванням "ua_session")
   --help - показати цю довідку
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime

# Імпортуємо клас відправника
from ua_telegram_sender.sender import UkrainianTelegramSender

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Константи API
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

def load_recipients(file_path):
    """
    Завантаження списку одержувачів з файлу
    
    Args:
        file_path (str): Шлях до файлу зі списком одержувачів
        
    Returns:
        list: Список одержувачів
    """
    recipients = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    recipients.append(line)
        logger.info(f"Завантажено {len(recipients)} одержувачів з файлу {file_path}")
        return recipients
    except Exception as e:
        logger.error(f"Помилка завантаження одержувачів з файлу {file_path}: {e}")
        return []

def save_log(message, recipients, successful, failed, error_details):
    """
    Збереження результатів у файл логу
    
    Args:
        message (str): Текст повідомлення
        recipients (list): Список одержувачів
        successful (int): Кількість успішних відправок
        failed (int): Кількість помилок
        error_details (dict): Словник з деталями помилок
    """
    log_file = "sending_log.txt"
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, "a", encoding="utf-8") as f:
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
            
        logger.info(f"Лог збережено у файл {log_file}")
    except Exception as e:
        logger.error(f"Помилка збереження логу: {e}")

def parse_arguments():
    """
    Розбір аргументів командного рядка
    
    Returns:
        argparse.Namespace: Об'єкт з аргументами
    """
    parser = argparse.ArgumentParser(description="Відправник Telegram для України")
    
    parser.add_argument("--phone", help="Номер телефону з '+' на початку")
    parser.add_argument("--code", help="Код підтвердження з Telegram")
    parser.add_argument("--message", help="Текст повідомлення")
    parser.add_argument("--password", help="Пароль двофакторної аутентифікації")
    parser.add_argument("--recipients", default="recipients.txt", help="Шлях до файлу зі списком одержувачів")
    parser.add_argument("--delay", type=float, default=2.0, help="Затримка між повідомленнями у секундах")
    parser.add_argument("--session", default="ua_session", help="Ім'я файлу сесії")
    parser.add_argument("--help", action="store_true", help="Показати довідку")
    
    if len(sys.argv) == 1 or "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
        
    return parser.parse_args()

def main():
    """Основна функція програми"""
    # Розбір аргументів
    args = parse_arguments()
    
    # Перевіряємо наявність повідомлення
    if not args.message:
        logger.error("Не вказано текст повідомлення (параметр --message)")
        return
    
    # Створюємо відправника
    sender = UkrainianTelegramSender(
        api_id=API_ID,
        api_hash=API_HASH,
        session_name=args.session
    )
    
    try:
        # Підключаємося до Telegram
        logger.info("Підключення до Telegram...")
        if not sender.connect():
            logger.error("Помилка підключення до Telegram")
            return
            
        # Перевіряємо авторизацію
        if not sender.is_authorized():
            logger.info("Потрібна авторизація у Telegram")
            
            # Перевіряємо наявність телефону і коду
            if not args.phone or not args.code:
                logger.error("Для авторизації необхідно вказати номер телефону (--phone) і код підтвердження (--code)")
                return
                
            # Виконуємо вхід
            logger.info(f"Вхід з номером {args.phone} і кодом...")
            if not sender.login(args.phone, args.code, args.password):
                logger.error("Помилка входу у Telegram")
                return
                
            logger.info("Успішний вхід у Telegram!")
        else:
            logger.info("Вже авторизовано у Telegram")
            
        # Отримуємо інформацію про користувача
        user_info = sender.get_me()
        if user_info:
            logger.info(f"Авторизовано як: {user_info.first_name} {user_info.last_name or ''} (@{user_info.username or 'немає'})")
            
        # Завантажуємо список одержувачів
        recipients = load_recipients(args.recipients)
        if not recipients:
            logger.error(f"Список одержувачів порожній. Перевірте файл {args.recipients}")
            return
            
        # Починаємо відправку
        logger.info(f"\n===== ПОЧАТОК ВІДПРАВКИ =====")
        logger.info(f"Повідомлення: {args.message[:50]}{'...' if len(args.message) > 50 else ''}")
        logger.info(f"Одержувачів: {len(recipients)}")
        logger.info(f"Затримка між повідомленнями: {args.delay} сек")
        
        # Засікаємо час
        start_time = time.time()
        
        # Відправляємо повідомлення
        successful, failed, error_details = sender.send_messages(recipients, args.message, args.delay)
        
        # Обчислюємо час
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        # Виводимо підсумки
        logger.info("\n===== РЕЗУЛЬТАТИ ВІДПРАВКИ =====")
        logger.info(f"Всього одержувачів: {len(recipients)}")
        logger.info(f"Успішно відправлено: {successful}")
        logger.info(f"Помилок: {failed}")
        logger.info(f"Час відправки: {minutes} хв {seconds} сек")
        
        # Процент успіху
        if recipients:
            success_rate = (successful / len(recipients)) * 100
            logger.info(f"Процент успіху: {success_rate:.1f}%")
            
        # Зберігаємо лог
        save_log(args.message, recipients, successful, failed, error_details)
        
    except KeyboardInterrupt:
        logger.info("\nВідправку перервано користувачем")
    except Exception as e:
        logger.error(f"Критична помилка: {e}")
    finally:
        # Відключаємося від Telegram
        if sender:
            sender.disconnect()

if __name__ == "__main__":
    main()