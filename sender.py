#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль відправника повідомлень Telegram для українських користувачів
====================================================================

Цей модуль надає клас UkrainianTelegramSender для взаємодії з API Telegram
та відправки повідомлень українським користувачам.
"""

import os
import time
import logging
import random
from telethon.sync import TelegramClient
from telethon.errors import (
    PhoneCodeExpiredError, PhoneCodeInvalidError, 
    SessionPasswordNeededError, FloodWaitError,
    UserBannedInChannelError, ChatWriteForbiddenError
)

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UkrainianTelegramSender:
    """
    Клас для відправки повідомлень українським користувачам Telegram
    
    Атрибути:
        api_id (int): API ID з Telegram
        api_hash (str): API Hash з Telegram
        session_name (str): Ім'я файлу сесії
        client: Клієнт Telegram
    """
    
    def __init__(self, api_id, api_hash, session_name="ua_session"):
        """
        Ініціалізація відправника
        
        Args:
            api_id (int): API ID з Telegram
            api_hash (str): API Hash з Telegram
            session_name (str, optional): Ім'я файлу сесії
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = None
        self.phone_code_hash = None
        
    def connect(self):
        """
        Підключення до API Telegram
        
        Returns:
            bool: True у разі успіху, False у разі помилки
        """
        try:
            # Створюємо клієнт
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            
            # Підключаємось
            self.client.connect()
            logger.info("Підключено до API Telegram")
            return True
        except Exception as e:
            logger.error(f"Помилка підключення до Telegram: {e}")
            return False
            
    def is_connected(self):
        """
        Перевірка підключення до Telegram
        
        Returns:
            bool: True якщо підключено, False якщо ні
        """
        if not self.client:
            return False
            
        try:
            return self.client.is_connected()
        except:
            return False
            
    def connect_and_check(self):
        """
        Підключення і перевірка авторизації
        
        Returns:
            bool: True якщо авторизовано, False якщо ні
        """
        if not self.is_connected():
            if not self.connect():
                return False
                
        return self.is_authorized()
        
    def is_authorized(self):
        """
        Перевірка авторизації
        
        Returns:
            bool: True якщо авторизовано, False якщо ні
        """
        if not self.client:
            return False
            
        try:
            return self.client.is_user_authorized()
        except:
            return False
            
    def disconnect(self):
        """Відключення від Telegram API"""
        if self.client:
            try:
                self.client.disconnect()
                logger.info("Відключено від Telegram API")
            except:
                pass
                
    def request_code(self, phone):
        """
        Запит коду підтвердження
        
        Args:
            phone (str): Номер телефону з '+' на початку
            
        Returns:
            bool: True у разі успіху, False у разі помилки
        """
        if not self.is_connected():
            if not self.connect():
                return False
                
        try:
            # Відправляємо запит на код
            logger.info(f"Запит коду для номера {phone}")
            sent_code = self.client.send_code_request(phone)
            self.phone_code_hash = sent_code.phone_code_hash
            logger.info(f"Код відправлено, hash: {self.phone_code_hash}")
            return True
        except Exception as e:
            logger.error(f"Помилка запиту коду: {e}")
            return False
            
    def login(self, phone, code, password=None):
        """
        Вхід у акаунт Telegram
        
        Args:
            phone (str): Номер телефону
            code (str): Код підтвердження
            password (str, optional): Пароль двофакторної аутентифікації
            
        Returns:
            bool: True у разі успіху, False у разі помилки
        """
        if not self.is_connected():
            if not self.connect():
                return False
                
        # Якщо вже авторизовані, повертаємо успіх
        if self.is_authorized():
            logger.info("Вже авторизовано")
            return True
            
        try:
            # Спроба входу з кодом
            logger.info(f"Вхід з номером {phone} і кодом")
            self.client.sign_in(phone=phone, code=code, phone_code_hash=self.phone_code_hash)
            logger.info("Успішний вхід!")
            return True
        except PhoneCodeInvalidError:
            logger.error("Введено невірний код підтвердження")
            return False
        except PhoneCodeExpiredError:
            logger.error("Код підтвердження протермінований")
            
            # Автоматично запитуємо новий код
            try:
                sent_code = self.client.send_code_request(phone)
                self.phone_code_hash = sent_code.phone_code_hash
                logger.info(f"Відправлено новий код, hash: {self.phone_code_hash}")
                logger.info("Потрібно ввести новий код")
            except Exception as e:
                logger.error(f"Помилка запиту нового коду: {e}")
                
            return False
        except SessionPasswordNeededError:
            # Потрібен пароль двофакторної аутентифікації
            logger.info("Потрібен пароль двофакторної аутентифікації")
            
            if not password:
                logger.error("Пароль двофакторної аутентифікації не вказано")
                return False
                
            try:
                # Вхід з паролем
                self.client.sign_in(password=password)
                logger.info("Успішний вхід з 2FA!")
                return True
            except Exception as e:
                logger.error(f"Помилка входу з 2FA: {e}")
                return False
        except Exception as e:
            logger.error(f"Помилка входу: {e}")
            return False
            
    def get_me(self):
        """
        Отримання інформації про поточного користувача
        
        Returns:
            User: Об'єкт користувача або None у разі помилки
        """
        if not self.is_authorized():
            logger.error("Не авторизовано")
            return None
            
        try:
            # Отримуємо інформацію
            return self.client.get_me()
        except Exception as e:
            logger.error(f"Помилка отримання інформації про користувача: {e}")
            return None
            
    def is_phone_number(self, recipient):
        """
        Перевірка, чи є одержувач номером телефону
        
        Args:
            recipient (str): Ідентифікатор одержувача
            
        Returns:
            bool: True якщо це номер телефону, False якщо ні
        """
        return recipient.startswith("+")
        
    def is_ukrainian_phone(self, phone):
        """
        Перевірка, чи є номер телефону українським
        
        Args:
            phone (str): Номер телефону
            
        Returns:
            bool: True якщо це український номер, False якщо ні
        """
        if not self.is_phone_number(phone):
            return False
            
        # Український код країни +380
        return phone.startswith("+380")
        
    def validate_recipient(self, recipient):
        """
        Валідація одержувача повідомлення
        
        Args:
            recipient (str): Ідентифікатор одержувача (@username або телефон)
            
        Returns:
            bool: True якщо одержувач валідний, False якщо ні
        """
        if not recipient:
            return False
            
        # Перевіряємо формат
        if self.is_phone_number(recipient):
            # Це номер телефону, перевіряємо формат
            return len(recipient) >= 10 and recipient.startswith("+")
        else:
            # Це username, перевіряємо формат
            return recipient.startswith("@") and len(recipient) >= 5
            
    def send_message(self, recipient, message):
        """
        Відправка повідомлення одержувачу
        
        Args:
            recipient (str): Ідентифікатор одержувача (@username або телефон)
            message (str): Текст повідомлення
            
        Returns:
            bool: True у разі успіху, False у разі помилки
        """
        if not self.is_authorized():
            logger.error("Не авторизовано, повідомлення не відправлено")
            return False
            
        if not self.validate_recipient(recipient):
            logger.error(f"Невірний формат одержувача: {recipient}")
            return False
            
        try:
            # Відправляємо повідомлення
            self.client.send_message(recipient, message)
            logger.info(f"Повідомлення відправлено для {recipient}")
            return True
        except FloodWaitError as e:
            # Обмеження частоти відправки
            wait_time = e.seconds
            logger.warning(f"Обмеження частоти відправки, очікування {wait_time} сек")
            
            if wait_time <= 30:
                # Якщо очікування невелике, чекаємо і пробуємо знову
                time.sleep(wait_time)
                try:
                    self.client.send_message(recipient, message)
                    logger.info(f"Повідомлення відправлено для {recipient} після паузи")
                    return True
                except Exception as e2:
                    logger.error(f"Помилка повторної відправки: {e2}")
                    return False
            else:
                # Занадто довге очікування
                logger.error(f"Занадто довге очікування: {wait_time} сек")
                return False
        except UserBannedInChannelError:
            logger.error(f"Користувач {recipient} заблокував вас або обмежив повідомлення")
            return False
        except ChatWriteForbiddenError:
            logger.error(f"Відправка повідомлень користувачу {recipient} заборонена")
            return False
        except Exception as e:
            logger.error(f"Помилка відправки повідомлення для {recipient}: {e}")
            return False
            
    def send_messages(self, recipients, message, delay=2.0):
        """
        Відправка повідомлень списку одержувачів
        
        Args:
            recipients (list): Список одержувачів
            message (str): Текст повідомлення
            delay (float, optional): Затримка між повідомленнями у секундах
            
        Returns:
            tuple: (успішно, помилки, {'одержувач': 'помилка'})
        """
        if not self.is_authorized():
            logger.error("Не авторизовано, повідомлення не відправлені")
            return 0, len(recipients), {}
            
        # Лічильники
        successful = 0
        failed = 0
        error_details = {}
        
        # Відправляємо повідомлення
        for i, recipient in enumerate(recipients, 1):
            # Очищаємо одержувача
            recipient = recipient.strip()
            if not recipient:
                continue
                
            # Валідуємо одержувача
            if not self.validate_recipient(recipient):
                failed += 1
                error_details[recipient] = "Невірний формат одержувача"
                logger.error(f"Невірний формат одержувача: {recipient}")
                continue
                
            # Виводимо прогрес
            logger.info(f"[{i}/{len(recipients)}] Відправка для {recipient}...")
            
            try:
                # Відправляємо повідомлення
                self.client.send_message(recipient, message)
                
                # Відмічаємо успіх
                successful += 1
                logger.info(f"Успішно відправлено: {recipient}")
                
                # Розумна пауза між повідомленнями
                if i < len(recipients):
                    # Базова затримка
                    pause = delay
                    
                    # Додаємо випадковість для обходу анти-спам систем
                    pause += random.uniform(0.5, 1.5)
                    
                    # Збільшуємо паузу, якщо багато успішних відправок
                    if successful > 10:
                        pause += 0.5
                    
                    # Пауза
                    time.sleep(pause)
                    
            except FloodWaitError as e:
                # Обмеження частоти відправки
                wait_time = e.seconds
                
                if wait_time <= 30:
                    # Короткочасне очікування
                    logger.warning(f"Обмеження частоти відправки, очікування {wait_time} сек")
                    time.sleep(wait_time)
                    
                    # Повторна спроба
                    try:
                        self.client.send_message(recipient, message)
                        successful += 1
                        logger.info(f"Успішно відправлено після паузи: {recipient}")
                        continue
                    except Exception as e2:
                        logger.error(f"Помилка повторної відправки: {e2}")
                else:
                    logger.error(f"Занадто довге очікування: {wait_time} сек")
                
                # Відмічаємо помилку
                failed += 1
                error_details[recipient] = f"FloodWaitError: {wait_time} сек"
                
            except UserBannedInChannelError:
                failed += 1
                error_details[recipient] = "Користувач заблокував вас або обмежив повідомлення"
                logger.error(f"Користувач {recipient} заблокував вас або обмежив повідомлення")
                
            except ChatWriteForbiddenError:
                failed += 1
                error_details[recipient] = "Відправка повідомлень заборонена"
                logger.error(f"Відправка повідомлень користувачу {recipient} заборонена")
                
            except Exception as e:
                # Інші помилки
                failed += 1
                error_details[recipient] = str(e)
                logger.error(f"Помилка відправки для {recipient}: {e}")
                
                # Пауза після помилки
                time.sleep(2)
        
        # Повертаємо результат
        return successful, failed, error_details