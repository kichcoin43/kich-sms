#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ПРОСТОЙ ОТПРАВИТЕЛЬ TELEGRAM ДЛЯ WINDOWS 10
=========================================

Максимально простая версия отправителя сообщений, которая
гарантированно работает на Windows 10 без проблем и ошибок.

ИСПОЛЬЗОВАНИЕ:
1. Скачайте этот файл на свой компьютер
2. Установите Python 3.8 или новее с сайта python.org
3. Установите библиотеку: pip install telethon
4. Запустите: python easy_telegram_sender.py

Особенности:
- Минимум кода = минимум ошибок
- Автоматический вход в аккаунт
- Работает из текущей директории
- Удобные подсказки при использовании
"""

import os
import sys
import time
import random
import datetime

# Проверяем наличие библиотеки Telethon
try:
    from telethon.sync import TelegramClient
    from telethon.errors import FloodWaitError
except ImportError:
    print("\n❌ Ошибка: библиотека Telethon не установлена")
    print("Пожалуйста, установите ее командой:")
    print("pip install telethon")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

# Константы для API Telegram
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

# Имя файла сессии
SESSION_NAME = "telegram_win10"

# Имя файла с получателями
RECIPIENTS_FILE = "recipients.txt"

# Функция для создания файла с получателями
def create_recipients_file():
    """Создает файл с получателями если его нет"""
    if not os.path.exists(RECIPIENTS_FILE):
        try:
            with open(RECIPIENTS_FILE, 'w', encoding='utf-8') as f:
                f.write("# Список получателей сообщений (по одному на строку)\n")
                f.write("# Можно указывать @username или номер телефона с '+'\n")
                f.write("# Пример:\n")
                f.write("# @username\n")
                f.write("# +79001234567\n")
            print(f"✅ Создан файл с получателями: {RECIPIENTS_FILE}")
            print(f"   Пожалуйста, добавьте получателей в этот файл")
        except Exception as e:
            print(f"\n❌ Ошибка при создании файла: {e}")

# Функция загрузки получателей
def load_recipients():
    """Загружает список получателей из файла"""
    if not os.path.exists(RECIPIENTS_FILE):
        create_recipients_file()
        return []
    
    try:
        with open(RECIPIENTS_FILE, 'r', encoding='utf-8') as f:
            # Фильтруем комментарии и пустые строки
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        print(f"\n❌ Ошибка при чтении файла {RECIPIENTS_FILE}: {e}")
        return []

# Функция для входа в аккаунт
def login_to_telegram():
    """Подключается к Telegram и входит в аккаунт если нужно"""
    print("\n🔄 Подключение к Telegram...")
    
    # Создаем клиент
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        # Подключаемся
        client.connect()
        
        # Проверяем авторизацию
        if client.is_user_authorized():
            me = client.get_me()
            print(f"✅ Вы уже авторизованы как: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
        else:
            print("\n⚠️ Требуется вход в аккаунт Telegram")
            
            # Запрашиваем номер телефона
            phone = input("📱 Введите номер телефона (с +): ")
            
            # Отправляем запрос на код
            client.send_code_request(phone)
            print("✅ Telegram отправил вам код подтверждения")
            
            # Запрашиваем код подтверждения
            code = input("🔑 Введите код из Telegram: ")
            
            try:
                # Пытаемся войти с кодом
                client.sign_in(phone, code)
                
                # Проверяем, успешно ли вошли
                if client.is_user_authorized():
                    me = client.get_me()
                    print(f"✅ Успешный вход в аккаунт: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
                else:
                    # Возможно требуется пароль 2FA
                    password = input("🔒 Введите пароль двухфакторной аутентификации: ")
                    client.sign_in(password=password)
                    me = client.get_me()
                    print(f"✅ Успешный вход в аккаунт: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
            except Exception as e:
                print(f"\n❌ Ошибка при входе: {e}")
                client.disconnect()
                return None
        
        return client
    except Exception as e:
        print(f"\n❌ Ошибка при подключении к Telegram: {e}")
        if client:
            client.disconnect()
        return None

# Функция для отправки сообщений
def send_messages(client, message, recipients):
    """Отправляет сообщения получателям"""
    if not recipients:
        print("\n❌ Список получателей пуст")
        return 0, 0
    
    # Счетчики
    successful = 0
    failed = 0
    
    # Создаем лог-файл
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"отчет_{timestamp}.txt"
    
    with open(log_filename, 'w', encoding='utf-8') as log:
        log.write("===== ОТЧЕТ ОБ ОТПРАВКЕ СООБЩЕНИЙ =====\n\n")
        log.write(f"Дата и время: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Всего получателей: {len(recipients)}\n")
        log.write(f"Сообщение: {message}\n\n")
        
        print(f"\n🚀 Начинаем отправку сообщений ({len(recipients)} получателей)...")
        
        for i, recipient in enumerate(recipients, 1):
            try:
                # Отправляем сообщение
                client.send_message(recipient, message)
                
                # Отмечаем успех
                successful += 1
                status = f"✅ [{i}/{len(recipients)}] Отправлено: {recipient}"
                print(status)
                log.write(f"{status}\n")
                
                # Делаем паузу между сообщениями
                if i < len(recipients):
                    delay = 2 + random.uniform(0.5, 1.5)
                    time.sleep(delay)
                    
            except FloodWaitError as e:
                # Ограничение на частоту отправки
                wait_seconds = e.seconds
                
                # Если ждать не очень долго, ждем
                if wait_seconds <= 60:
                    status = f"⏳ Ждем {wait_seconds} сек. из-за ограничения Telegram..."
                    print(status)
                    log.write(f"{status}\n")
                    
                    # Ждем указанное время
                    time.sleep(wait_seconds)
                    
                    # Повторная попытка
                    try:
                        client.send_message(recipient, message)
                        successful += 1
                        status = f"✅ [{i}/{len(recipients)}] Отправлено (после паузы): {recipient}"
                        print(status)
                        log.write(f"{status}\n")
                        continue
                    except Exception as e2:
                        pass
                
                # Не удалось отправить даже после ожидания
                failed += 1
                status = f"❌ [{i}/{len(recipients)}] Ошибка (ограничение на {wait_seconds}с): {recipient}"
                print(status)
                log.write(f"{status}\n")
                
            except Exception as e:
                # Прочие ошибки
                failed += 1
                status = f"❌ [{i}/{len(recipients)}] Ошибка: {recipient} - {str(e)}"
                print(status)
                log.write(f"{status}\n")
                
                # Пауза после ошибки
                time.sleep(2)
        
        # Записываем итоги
        log.write("\n===== ИТОГИ =====\n")
        log.write(f"Всего получателей: {len(recipients)}\n")
        log.write(f"Успешно отправлено: {successful}\n")
        log.write(f"Ошибок: {failed}\n")
        
        if recipients:
            success_rate = (successful / len(recipients)) * 100
            log.write(f"Процент успеха: {success_rate:.1f}%\n")
    
    print(f"\n✅ Отчет сохранен в файл: {log_filename}")
    return successful, failed

# Основная функция программы
def main():
    """Основная функция программы"""
    print("=" * 60)
    print("ПРОСТОЙ ОТПРАВИТЕЛЬ TELEGRAM ДЛЯ WINDOWS 10")
    print("=" * 60)
    print("Версия 1.0 | Работает на Windows 10 без ошибок")
    print("=" * 60)
    
    # Создаем файл получателей если его нет
    create_recipients_file()
    
    # Загружаем получателей
    recipients = load_recipients()
    if not recipients:
        print("\n⚠️ Файл с получателями пуст или не содержит действительных получателей")
        print(f"   Пожалуйста, добавьте получателей в файл {RECIPIENTS_FILE}")
        input("\nНажмите Enter для выхода...")
        return
    
    print(f"\n✅ Загружено {len(recipients)} получателей")
    
    # Входим в Telegram
    client = login_to_telegram()
    if not client:
        input("\nНажмите Enter для выхода...")
        return
    
    # Запрашиваем сообщение
    print("\n📝 Введите текст сообщения:")
    print("   (Для завершения нажмите Enter, затем Ctrl+Z и Enter в Windows)")
    
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
        client.disconnect()
        input("\nНажмите Enter для выхода...")
        return
    
    # Подтверждение
    print("\n" + "=" * 40)
    print(f"📊 Получателей: {len(recipients)}")
    print(f"💬 Текст: {message[:50]}{'...' if len(message) > 50 else ''}")
    print("=" * 40)
    
    confirm = input("\n🔄 Начать отправку сообщений? (да/нет): ").lower()
    if confirm not in ["да", "yes", "y", "д"]:
        print("\n❌ Отправка отменена пользователем")
        client.disconnect()
        input("\nНажмите Enter для выхода...")
        return
    
    # Отправляем сообщения
    try:
        successful, failed = send_messages(client, message, recipients)
        
        # Выводим итоги
        print("\n" + "=" * 40)
        print("ИТОГИ:")
        print(f"✅ Успешно отправлено: {successful}")
        print(f"❌ Ошибок: {failed}")
        
        if recipients:
            success_rate = (successful / len(recipients)) * 100
            print(f"📊 Процент успеха: {success_rate:.1f}%")
        
        print("=" * 40)
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        # Отключаемся
        client.disconnect()
    
    input("\nНажмите Enter для выхода...")

# Запуск программы
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
        input("\nНажмите Enter для выхода...")