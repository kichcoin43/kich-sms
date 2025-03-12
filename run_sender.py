#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ШВИДКИЙ ЗАПУСК ВІДПРАВНИКА ПОВІДОМЛЕНЬ TELEGRAM
=============================================

Найпростіший скрипт для відправки повідомлень з існуючої сесії.
Не потребує введення кодів підтвердження, якщо сесія вже існує.

ВИКОРИСТАННЯ:
  python run_sender.py "Текст повідомлення"
"""

import os
import sys
import time
import random
import logging

# Імпортуємо клас відправника
from ua_telegram_sender.sender import UkrainianTelegramSender

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Константи
DEFAULT_SESSION_NAME = "ua_session"
DEFAULT_RECIPIENTS_FILE = "recipients.txt"

# Константи API
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

def load_recipients():
    """Завантаження списку одержувачів з файлу"""
    if not os.path.exists(DEFAULT_RECIPIENTS_FILE):
        # Створюємо файл-приклад
        try:
            with open(DEFAULT_RECIPIENTS_FILE, "w", encoding="utf-8") as f:
                f.write("# Список одержувачів (по одному на рядок)\n")
                f.write("# Можна використовувати @username або телефон у форматі +380xxxxxxxxx\n\n")
                f.write("@username1\n")
                f.write("@username2\n")
                f.write("+380xxxxxxxxx\n")
            logger.warning(f"Створено файл-приклад {DEFAULT_RECIPIENTS_FILE}. Відредагуйте його і запустіть скрипт знову.")
            return None
        except Exception as e:
            logger.error(f"Помилка створення файлу-прикладу: {e}")
            return None
    
    # Завантажуємо одержувачів
    try:
        with open(DEFAULT_RECIPIENTS_FILE, "r", encoding="utf-8") as f:
            recipients = []
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    recipients.append(line)
        return recipients
    except Exception as e:
        logger.error(f"Помилка завантаження одержувачів: {e}")
        return None

def main():
    """Основна функція програми"""
    # Перевіряємо аргументи
    if len(sys.argv) < 2:
        print(__doc__)
        return
        
    # Отримуємо повідомлення
    message = sys.argv[1]
    
    # Перевіряємо наявність файлу сесії
    session_file = f"{DEFAULT_SESSION_NAME}.session"
    if not os.path.exists(session_file):
        logger.error(f"Файл сесії {session_file} не знайдено. Спочатку авторизуйтеся через ua_cli.py або main.py")
        return
        
    # Завантажуємо одержувачів
    recipients = load_recipients()
    if not recipients:
        return
        
    # Створюємо відправника
    sender = UkrainianTelegramSender(
        api_id=API_ID,
        api_hash=API_HASH,
        session_name=DEFAULT_SESSION_NAME
    )
    
    try:
        # Підключаємося і перевіряємо авторизацію
        if not sender.connect_and_check():
            logger.error("Помилка підключення або авторизації. Спочатку авторизуйтеся через ua_cli.py або main.py")
            return
            
        # Отримуємо інформацію про користувача
        user_info = sender.get_me()
        if user_info:
            logger.info(f"Авторизовано як: {user_info.first_name} {user_info.last_name or ''} (@{user_info.username or 'немає'})")
        
        # Виводимо інформацію
        logger.info(f"Завантажено {len(recipients)} одержувачів")
        logger.info(f"Повідомлення: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        # Засікаємо час
        start_time = time.time()
        
        # Відправляємо повідомлення
        successful = 0
        failed = 0
        
        for i, recipient in enumerate(recipients, 1):
            recipient = recipient.strip()
            if not recipient:
                continue
                
            try:
                # Виводимо прогрес
                logger.info(f"[{i}/{len(recipients)}] Відправка для {recipient}...")
                
                # Відправляємо повідомлення
                if sender.send_message(recipient, message):
                    # Успіх
                    successful += 1
                    logger.info(f"✓ Успішно відправлено: {recipient}")
                else:
                    # Помилка
                    failed += 1
                    logger.error(f"✗ Помилка відправки: {recipient}")
                    
                # Пауза між повідомленнями
                if i < len(recipients):
                    delay = 2.0 + random.uniform(0.5, 1.5)
                    time.sleep(delay)
                    
            except Exception as e:
                # Помилка
                failed += 1
                logger.error(f"✗ Помилка відправки для {recipient}: {e}")
                time.sleep(2)
                
        # Обчислюємо час
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        # Виводимо підсумки
        logger.info("\n===== РЕЗУЛЬТАТИ =====")
        logger.info(f"Всього одержувачів: {len(recipients)}")
        logger.info(f"Успішно відправлено: {successful}")
        logger.info(f"Помилок: {failed}")
        logger.info(f"Час відправки: {minutes} хв {seconds} сек")
        
        # Процент успіху
        if recipients:
            success_rate = (successful / len(recipients)) * 100
            logger.info(f"Процент успіху: {success_rate:.1f}%")
            
    except KeyboardInterrupt:
        logger.info("\nВідправку перервано користувачем")
    except Exception as e:
        logger.error(f"Критична помилка: {e}")
    finally:
        # Відключаємося
        if sender:
            sender.disconnect()
            
    # Затримка перед виходом
    print("\nГотово! Перегляньте результати вище.")

if __name__ == "__main__":
    main()