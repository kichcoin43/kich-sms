#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ЗАПУСК ВІДПРАВНИКА TELEGRAM
==========================

Спрощений скрипт для відправки повідомлень з командного рядка.
Приймає всі необхідні параметри через аргументи командного рядка.

ВИКОРИСТАННЯ:
   python запустити.py "Текст повідомлення" +380xxxxxxxxx 12345
   
Де:
   1. "Текст повідомлення" - текст, який буде відправлено
   2. +380xxxxxxxxx - номер телефону з "+" на початку
   3. 12345 - код підтвердження з Telegram
   4. (опціонально) пароль двофакторної аутентифікації
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
DEFAULT_RECIPIENTS_FILE = "recipients.txt"
SESSION_NAME = "ua_session"

# Константи API
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

def load_recipients():
    """Завантаження списку одержувачів з файлу"""
    try:
        if os.path.exists(DEFAULT_RECIPIENTS_FILE):
            with open(DEFAULT_RECIPIENTS_FILE, "r", encoding="utf-8") as f:
                recipients = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        recipients.append(line)
            logger.info(f"Завантажено {len(recipients)} одержувачів з файлу {DEFAULT_RECIPIENTS_FILE}")
            return recipients
        else:
            logger.error(f"Файл {DEFAULT_RECIPIENTS_FILE} не знайдено")
            return []
    except Exception as e:
        logger.error(f"Помилка завантаження одержувачів: {e}")
        return []

def main():
    """Основна функція програми"""
    # Перевіряємо аргументи
    if len(sys.argv) < 4:
        print(__doc__)
        return
        
    # Отримуємо параметри
    message = sys.argv[1]
    phone = sys.argv[2]
    code = sys.argv[3]
    password = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Перевіряємо формат телефону
    if not phone.startswith("+"):
        logger.error("Номер телефону повинен починатися з '+' (наприклад, +380xxxxxxxxx)")
        return
        
    # Завантажуємо одержувачів
    recipients = load_recipients()
    if not recipients:
        logger.error(f"Список одержувачів порожній. Створіть файл {DEFAULT_RECIPIENTS_FILE} з одержувачами")
        return
        
    # Створюємо відправника
    sender = UkrainianTelegramSender(
        api_id=API_ID,
        api_hash=API_HASH,
        session_name=SESSION_NAME
    )
    
    try:
        # Підключаємося
        logger.info("Підключення до Telegram...")
        if not sender.connect():
            logger.error("Помилка підключення до Telegram")
            return
            
        # Перевіряємо авторизацію
        if not sender.is_authorized():
            # Входимо з параметрами
            logger.info(f"Вхід з номером {phone} і кодом...")
            if not sender.login(phone, code, password):
                logger.error("Помилка входу в Telegram")
                return
                
            logger.info("Успішний вхід у Telegram!")
        else:
            logger.info("Вже авторизовано у Telegram")
            
        # Отримуємо інформацію про користувача
        user_info = sender.get_me()
        if user_info:
            logger.info(f"Авторизовано як: {user_info.first_name} {user_info.last_name or ''} (@{user_info.username or 'немає'})")
            
        # Починаємо відправку
        logger.info(f"\n===== ПОЧАТОК ВІДПРАВКИ =====")
        logger.info(f"Повідомлення: {message[:50]}{'...' if len(message) > 50 else ''}")
        logger.info(f"Одержувачів: {len(recipients)}")
        
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