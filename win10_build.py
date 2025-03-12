#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
СОЗДАНИЕ EXE-ФАЙЛА ДЛЯ WINDOWS 10
==================================

Этот скрипт создает надежный EXE-файл для Windows 10, который
работает без ошибок и не требует дополнительных библиотек.

Для сборки используется PyInstaller с оптимальными настройками,
обеспечивающими совместимость с Windows 10.
"""

import os
import sys
import subprocess
import logging
import shutil
import platform
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Имя выходного файла
OUTPUT_NAME = 'KICH_SMS_Win10.exe'

def check_requirements():
    """Проверяет наличие необходимых модулей для сборки"""
    try:
        import PyInstaller
        logger.info("PyInstaller установлен.")
    except ImportError:
        logger.warning("PyInstaller не установлен. Устанавливаем...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            logger.info("PyInstaller успешно установлен.")
        except Exception as e:
            logger.error(f"Не удалось установить PyInstaller: {e}")
            return False
    
    # Проверяем Telethon
    try:
        import telethon
        logger.info("Telethon установлен.")
    except ImportError:
        logger.warning("Telethon не установлен. Устанавливаем...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])
            logger.info("Telethon успешно установлен.")
        except Exception as e:
            logger.error(f"Не удалось установить Telethon: {e}")
            return False
            
    # Проверяем PIL для работы с иконкой
    try:
        from PIL import Image
        logger.info("Pillow установлен.")
    except ImportError:
        logger.warning("Pillow не установлен. Устанавливаем...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            logger.info("Pillow успешно установлен.")
        except Exception as e:
            logger.error(f"Не удалось установить Pillow: {e}")
    
    return True

def create_icon():
    """Создаем иконку для приложения"""
    icon_path = os.path.join(os.getcwd(), 'telegram_icon.ico')
    
    # Если иконка уже существует, то не создаем
    if os.path.exists(icon_path):
        return icon_path
        
    # Простой способ: создаем пустой файл иконки
    try:
        from PIL import Image
        
        # Создаем пустое изображение 64x64 с синим фоном 
        # (цвет Telegram)
        img = Image.new('RGB', (64, 64), color=(42, 171, 238))
        img.save('telegram_icon.png')
        
        # Конвертируем PNG в ICO
        img.save(icon_path, format='ICO')
        logger.info(f"Создана иконка: {icon_path}")
        
        return icon_path
    except Exception as e:
        logger.warning(f"Не удалось создать иконку: {e}")
        return None

def cleanup():
    """Очистка временных файлов перед сборкой"""
    # Удаляем директории build и dist
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                logger.info(f"Удалена директория: {dir_name}")
            except Exception as e:
                logger.warning(f"Не удалось удалить директорию {dir_name}: {e}")
    
    # Удаляем файлы .spec
    for spec_file in Path('.').glob('*.spec'):
        try:
            os.remove(spec_file)
            logger.info(f"Удален файл: {spec_file}")
        except Exception as e:
            logger.warning(f"Не удалось удалить файл {spec_file}: {e}")

def copy_final_py():
    """Копирует FINAL.py в telegram_sender.py для сборки"""
    shutil.copy('FINAL.py', 'telegram_sender.py')
    logger.info("Создан файл telegram_sender.py из FINAL.py")
    
    # Создаем пустой файл получателей если его нет
    if not os.path.exists('test_recipients.txt'):
        with open('test_recipients.txt', 'w', encoding='utf-8') as f:
            f.write("@username1\n@username2\n+79001234567\n")
        logger.info("Создан файл test_recipients.txt")

def build_exe():
    """Сборка EXE-файла с помощью PyInstaller"""
    if not check_requirements():
        logger.error("Не удалось установить необходимые зависимости")
        return False
    
    # Очистка временных файлов
    cleanup()
    
    # Копируем FINAL.py
    copy_final_py()
    
    # Создаем иконку
    icon_path = create_icon()
    
    # Базовые параметры PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',  # Все в одном файле
        '--clean',    # Очистка кэша
        '--noconfirm', # Без подтверждений
        '--name', OUTPUT_NAME.replace('.exe', ''),
    ]
    
    # Добавляем иконку если есть
    if icon_path and os.path.exists(icon_path):
        cmd.extend(['--icon', icon_path])
    
    # Добавляем главный файл
    cmd.append('telegram_sender.py')
    
    # Запускаем PyInstaller
    try:
        logger.info(f"Запуск команды: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
        # Проверяем, создан ли EXE-файл
        exe_path = os.path.join('dist', OUTPUT_NAME)
        if os.path.exists(exe_path):
            logger.info(f"Сборка успешна! EXE-файл создан: {exe_path}")
            
            # Копируем файл получателей в папку dist
            try:
                recipients_path = os.path.join('dist', 'test_recipients.txt')
                shutil.copy('test_recipients.txt', recipients_path)
                logger.info(f"Файл test_recipients.txt скопирован в {recipients_path}")
            except Exception as e:
                logger.warning(f"Не удалось скопировать файл получателей: {e}")
            
            return True
        else:
            logger.error(f"Сборка не удалась: EXE-файл не найден по пути {exe_path}")
            return False
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при сборке: {e}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return False

def create_sender_with_ui():
    """Создаем улучшенную версию отправителя с простым UI"""
    sender_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ОТПРАВИТЕЛЬ СООБЩЕНИЙ TELEGRAM ДЛЯ WINDOWS 10
=============================================

Улучшенная версия с простым пользовательским интерфейсом для Windows 10.
Основана на FINAL.py с добавлением простого графического интерфейса.
"""

import os
import sys
import time
import random
import logging
import threading
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError

# Если доступен tkinter, используем его для UI
try:
    import tkinter as tk
    from tkinter import scrolledtext, messagebox, filedialog
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

# Константы для API
API_ID = 1079592
API_HASH = "4b3c8eeb47a62ecc941e61907f1a7bf0"

# Список возможных файлов сессий
SESSION_FILES = [
    'session', 'telegram_session', 'mega_session', 'direct_session',
    'direct_login', 'session_telegram'
]

# Файл с получателями
RECIPIENTS_FILE = "test_recipients.txt"

class LogRedirector:
    """Перенаправляет вывод логов в текстовое поле"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
    def write(self, message):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')
        
    def flush(self):
        pass

class TelegramSenderApp:
    """Класс приложения с графическим интерфейсом"""
    def __init__(self, root):
        self.root = root
        self.root.title("Отправитель сообщений Telegram")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Устанавливаем иконку если есть
        if os.path.exists("telegram_icon.ico"):
            self.root.iconbitmap("telegram_icon.ico")
        
        # Переменные
        self.message_var = tk.StringVar()
        self.recipients_file_var = tk.StringVar(value=RECIPIENTS_FILE)
        self.status_var = tk.StringVar(value="Готов к работе")
        self.is_sending = False
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Находим сессии при запуске
        self.update_sessions()
    
    def create_widgets(self):
        """Создает элементы интерфейса"""
        # Верхняя часть - настройки
        settings_frame = tk.Frame(self.root, padx=10, pady=5)
        settings_frame.pack(fill=tk.X)
        
        # Файл получателей
        tk.Label(settings_frame, text="Файл получателей:").grid(row=0, column=0, sticky=tk.W)
        recipients_entry = tk.Entry(settings_frame, textvariable=self.recipients_file_var, width=50)
        recipients_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        browse_btn = tk.Button(settings_frame, text="Обзор", command=self.browse_recipients)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Сессии
        tk.Label(settings_frame, text="Сессия:").grid(row=1, column=0, sticky=tk.W)
        self.session_combo = tk.StringVar()
        self.sessions_dropdown = tk.OptionMenu(settings_frame, self.session_combo, "")
        self.sessions_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        refresh_btn = tk.Button(settings_frame, text="Обновить", command=self.update_sessions)
        refresh_btn.grid(row=1, column=2, padx=5, pady=5)
        
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Средняя часть - сообщение
        message_frame = tk.Frame(self.root, padx=10, pady=5)
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(message_frame, text="Текст сообщения:").pack(anchor=tk.W)
        self.message_text = tk.Text(message_frame, height=5, wrap=tk.WORD)
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Нижняя часть - логи и управление
        control_frame = tk.Frame(self.root, padx=10, pady=5)
        control_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(control_frame, text="Логи:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(control_frame, height=10, wrap=tk.WORD, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Перенаправляем логи
        log_redirector = LogRedirector(self.log_text)
        logger.handlers[0].stream = log_redirector
        
        # Статус и кнопки
        status_frame = tk.Frame(self.root, padx=10, pady=5)
        status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, bg="lightgray")
        self.status_label.pack(fill=tk.X, padx=5, pady=5)
        
        buttons_frame = tk.Frame(self.root, padx=10, pady=5)
        buttons_frame.pack(fill=tk.X)
        
        self.send_btn = tk.Button(buttons_frame, text="Отправить сообщения", command=self.send_messages, bg="green", fg="white", height=2)
        self.send_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        self.stop_btn = tk.Button(buttons_frame, text="Остановить", command=self.stop_sending, bg="red", fg="white", state=tk.DISABLED, height=2)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
    
    def update_sessions(self):
        """Обновляет список доступных сессий"""
        # Получаем список сессий
        sessions = []
        for session in SESSION_FILES:
            if os.path.exists(f"{session}.session"):
                sessions.append(session)
        
        # Настраиваем выпадающий список
        menu = self.sessions_dropdown["menu"]
        menu.delete(0, "end")
        
        if sessions:
            self.session_combo.set(sessions[0])
            for session in sessions:
                menu.add_command(label=session, command=lambda value=session: self.session_combo.set(value))
            self.status_var.set(f"Найдено {len(sessions)} сессий. Готов к работе.")
        else:
            self.session_combo.set("Нет сессий")
            menu.add_command(label="Нет сессий")
            self.status_var.set("Сессии не найдены. Сначала войдите в аккаунт.")
    
    def browse_recipients(self):
        """Открывает диалог выбора файла получателей"""
        filename = filedialog.askopenfilename(
            title="Выберите файл получателей",
            filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
        )
        if filename:
            self.recipients_file_var.set(filename)
    
    def load_recipients(self, file_path):
        """Загружает получателей из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Ошибка загрузки получателей: {e}")
            return []
    
    def send_messages(self):
        """Запускает отправку сообщений"""
        # Получаем сессию
        session = self.session_combo.get()
        if session == "Нет сессий":
            messagebox.showerror("Ошибка", "Нет доступных сессий. Сначала войдите в аккаунт.")
            return
        
        # Получаем сообщение
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Ошибка", "Введите текст сообщения.")
            return
        
        # Получаем файл получателей
        recipients_file = self.recipients_file_var.get()
        if not os.path.exists(recipients_file):
            messagebox.showerror("Ошибка", f"Файл получателей не найден: {recipients_file}")
            return
        
        # Запускаем отправку в отдельном потоке
        self.is_sending = True
        self.send_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Запускаем поток отправки
        send_thread = threading.Thread(
            target=self.send_thread, 
            args=(session, message, recipients_file)
        )
        send_thread.daemon = True
        send_thread.start()
    
    def send_thread(self, session, message, recipients_file):
        """Функция отправки сообщений в отдельном потоке"""
        # Обновляем статус
        self.status_var.set("Отправка сообщений...")
        
        # Загружаем получателей
        recipients = self.load_recipients(recipients_file)
        if not recipients:
            messagebox.showerror("Ошибка", f"Не удалось загрузить получателей из {recipients_file}")
            self.reset_ui()
            return
        
        logger.info(f"Файл сессии: {session}.session")
        logger.info(f"Загружено {len(recipients)} получателей")
        logger.info(f"Сообщение: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        # Создаем клиент
        client = TelegramClient(session, API_ID, API_HASH)
        
        try:
            # Подключаемся
            client.connect()
            
            # Проверяем авторизацию
            if not client.is_user_authorized():
                logger.error("Сессия недействительна. Требуется повторный вход в аккаунт.")
                messagebox.showerror("Ошибка", "Сессия недействительна. Требуется повторный вход в аккаунт.")
                self.reset_ui()
                return
            
            # Получаем информацию о пользователе
            me = client.get_me()
            logger.info(f"Авторизован как: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
            
            # Отправка сообщений
            successful = 0
            failed = 0
            
            logger.info(f"\n===== НАЧАЛО ОТПРАВКИ =====")
            
            for i, recipient in enumerate(recipients, 1):
                # Если отправка остановлена, выходим
                if not self.is_sending:
                    logger.info("\nОтправка остановлена пользователем.")
                    break
                
                try:
                    # Отправляем сообщение
                    client.send_message(recipient, message)
                    
                    # Отмечаем успех
                    successful += 1
                    logger.info(f"✓ [{i}/{len(recipients)}] Отправлено: {recipient}")
                    
                    # Обновляем статус
                    self.status_var.set(f"Отправка сообщений... {i}/{len(recipients)} ({successful} успешно, {failed} ошибок)")
                    
                    # Делаем паузу
                    if i < len(recipients) and self.is_sending:
                        delay = 2 + random.uniform(0.5, 1.5)
                        time.sleep(delay)
                        
                except FloodWaitError as e:
                    # Ограничение на частоту отправки
                    wait_seconds = e.seconds
                    
                    if wait_seconds <= 30 and self.is_sending:
                        logger.warning(f"⚠️ Пауза {wait_seconds} сек...")
                        self.status_var.set(f"Ожидание {wait_seconds} сек из-за ограничения...")
                        
                        # Ждем указанное время
                        time.sleep(wait_seconds)
                        
                        # Повторная попытка
                        try:
                            client.send_message(recipient, message)
                            successful += 1
                            logger.info(f"✓ [{i}/{len(recipients)}] Отправлено (после паузы): {recipient}")
                            continue
                        except Exception as e2:
                            pass
                    
                    failed += 1
                    logger.error(f"✗ [{i}/{len(recipients)}] Ошибка (FloodWait {wait_seconds}с): {recipient}")
                    
                except Exception as e:
                    # Прочие ошибки
                    failed += 1
                    logger.error(f"✗ [{i}/{len(recipients)}] Ошибка: {recipient} - {str(e)}")
                    
                    # Небольшая пауза после ошибки
                    if self.is_sending:
                        time.sleep(2)
            
            # Итоги
            logger.info("\n===== РЕЗУЛЬТАТЫ =====")
            logger.info(f"Всего получателей: {len(recipients)}")
            logger.info(f"Успешно отправлено: {successful}")
            logger.info(f"Ошибок: {failed}")
            
            if recipients:
                success_rate = (successful / len(recipients)) * 100
                logger.info(f"Процент успеха: {success_rate:.1f}%")
                
            # Обновляем статус
            if self.is_sending:
                self.status_var.set(f"Отправка завершена: {successful} успешно, {failed} ошибок")
            else:
                self.status_var.set(f"Отправка остановлена: {successful} успешно, {failed} ошибок")
                
            # Показываем сообщение об успехе
            messagebox.showinfo("Успех", f"Отправка завершена: {successful} успешно, {failed} ошибок")
            
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            messagebox.showerror("Ошибка", f"Критическая ошибка: {e}")
        finally:
            # Отключаемся
            if client:
                client.disconnect()
            
            # Восстанавливаем интерфейс
            self.reset_ui()
    
    def stop_sending(self):
        """Останавливает отправку сообщений"""
        self.is_sending = False
        self.status_var.set("Останавливаем отправку...")
    
    def reset_ui(self):
        """Сбрасывает UI в исходное состояние"""
        self.is_sending = False
        self.send_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

def run_console_mode(message=None):
    """Запуск в консольном режиме"""
    # Проверяем наличие сообщения
    if not message:
        if len(sys.argv) >= 2:
            message = sys.argv[1]
        else:
            print(__doc__)
            message = input("Введите текст сообщения: ")
    
    # Ищем существующий файл сессии
    session_file = None
    for session in SESSION_FILES:
        if os.path.exists(f"{session}.session"):
            session_file = session
            break
    
    if not session_file:
        logger.error("Не найден файл сессии Telegram. Сначала войдите в аккаунт.")
        return
    
    # Загружаем получателей
    recipients = []
    try:
        with open(RECIPIENTS_FILE, 'r', encoding='utf-8') as f:
            recipients = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Ошибка загрузки получателей: {e}")
        
    if not recipients:
        logger.error(f"Не удалось загрузить получателей из {RECIPIENTS_FILE}")
        return
    
    logger.info(f"Найден файл сессии: {session_file}.session")
    logger.info(f"Загружено {len(recipients)} получателей")
    logger.info(f"Сообщение: {message[:50]}{'...' if len(message) > 50 else ''}")
    
    # Создаем клиент
    client = TelegramClient(session_file, API_ID, API_HASH)
    
    try:
        # Подключаемся
        client.connect()
        
        # Проверяем авторизацию
        if not client.is_user_authorized():
            logger.error("Сессия недействительна. Требуется повторный вход в аккаунт.")
            return
        
        # Получаем информацию о пользователе
        me = client.get_me()
        logger.info(f"Авторизован как: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
        
        # Отправка сообщений
        successful = 0
        failed = 0
        
        logger.info(f"\n===== НАЧАЛО ОТПРАВКИ =====")
        
        for i, recipient in enumerate(recipients, 1):
            try:
                # Отправляем сообщение
                client.send_message(recipient, message)
                
                # Отмечаем успех
                successful += 1
                logger.info(f"✓ [{i}/{len(recipients)}] Отправлено: {recipient}")
                
                # Делаем паузу
                if i < len(recipients):
                    delay = 2 + random.uniform(0.5, 1.5)
                    time.sleep(delay)
                    
            except FloodWaitError as e:
                # Ограничение на частоту отправки
                wait_seconds = e.seconds
                
                if wait_seconds <= 30:
                    logger.warning(f"⚠️ Пауза {wait_seconds} сек...")
                    time.sleep(wait_seconds)
                    
                    # Повторная попытка
                    try:
                        client.send_message(recipient, message)
                        successful += 1
                        logger.info(f"✓ [{i}/{len(recipients)}] Отправлено (после паузы): {recipient}")
                        continue
                    except Exception as e2:
                        pass
                
                failed += 1
                logger.error(f"✗ [{i}/{len(recipients)}] Ошибка (FloodWait {wait_seconds}с): {recipient}")
                
            except Exception as e:
                # Прочие ошибки
                failed += 1
                logger.error(f"✗ [{i}/{len(recipients)}] Ошибка: {recipient} - {str(e)}")
                time.sleep(2)
        
        # Итоги
        logger.info("\n===== РЕЗУЛЬТАТЫ =====")
        logger.info(f"Всего получателей: {len(recipients)}")
        logger.info(f"Успешно отправлено: {successful}")
        logger.info(f"Ошибок: {failed}")
        
        if recipients:
            success_rate = (successful / len(recipients)) * 100
            logger.info(f"Процент успеха: {success_rate:.1f}%")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        # Отключаемся
        if client:
            client.disconnect()

def main():
    """Основная функция программы"""
    # Проверяем, есть ли tkinter
    if HAS_TKINTER:
        # Запуск GUI
        root = tk.Tk()
        app = TelegramSenderApp(root)
        root.mainloop()
    else:
        # Запуск в консольном режиме
        run_console_mode()

if __name__ == "__main__":
    try:
        # Если указан аргумент командной строки, запускаем в консольном режиме
        if len(sys.argv) >= 2 and sys.argv[1].lower() == "--console":
            message = None
            if len(sys.argv) >= 3:
                message = sys.argv[2]
            run_console_mode(message)
        else:
            main()
    except KeyboardInterrupt:
        logger.info("\nПрограмма прервана пользователем")
        sys.exit(0)
'''
    
    # Записываем улучшенный файл отправителя
    with open('telegram_sender_win10.py', 'w', encoding='utf-8') as f:
        f.write(sender_code)
    
    logger.info("Создан файл telegram_sender_win10.py с улучшенным интерфейсом")
    return True

def build_improved_exe():
    """Сборка улучшенной версии с интерфейсом"""
    # Создаем улучшенный отправитель
    if not create_sender_with_ui():
        logger.error("Не удалось создать улучшенный отправитель")
        return False
    
    # Очистка временных файлов
    cleanup()
    
    # Создаем иконку
    icon_path = create_icon()
    
    # Базовые параметры PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',  # Все в одном файле
        '--clean',    # Очистка кэша
        '--noconfirm', # Без подтверждений
        '--name', 'KICH_SMS_UI',
        '--windowed',  # Без консоли
    ]
    
    # Добавляем иконку если есть
    if icon_path and os.path.exists(icon_path):
        cmd.extend(['--icon', icon_path])
    
    # Добавляем дополнительные файлы
    cmd.extend([
        '--add-data', f'test_recipients.txt{os.pathsep}.',
        '--hidden-import', 'telethon',
        '--hidden-import', 'tkinter',
    ])
    
    # Добавляем главный файл
    cmd.append('telegram_sender_win10.py')
    
    # Запускаем PyInstaller
    try:
        logger.info(f"Запуск команды: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
        # Проверяем, создан ли EXE-файл
        exe_path = os.path.join('dist', 'KICH_SMS_UI.exe')
        if os.path.exists(exe_path):
            logger.info(f"Сборка успешна! EXE-файл с интерфейсом создан: {exe_path}")
            
            # Копируем файл получателей в папку dist
            try:
                recipients_path = os.path.join('dist', 'test_recipients.txt')
                shutil.copy('test_recipients.txt', recipients_path)
                logger.info(f"Файл test_recipients.txt скопирован в {recipients_path}")
            except Exception as e:
                logger.warning(f"Не удалось скопировать файл получателей: {e}")
            
            return True
        else:
            logger.error(f"Сборка не удалась: EXE-файл не найден по пути {exe_path}")
            return False
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при сборке: {e}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return False

def create_batch_file():
    """Создает BAT-файл для запуска сборки на Windows"""
    batch_content = '''@echo off
echo ============================================================
echo   СБОРКА KICH SMS EXE ДЛЯ WINDOWS 10
echo ============================================================
echo.

:: Проверка Python
python --version > nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не установлен или не доступен в системном пути.
    echo Загрузите и установите Python с сайта https://www.python.org/downloads/
    echo.
    echo После установки Python запустите этот файл снова.
    pause
    exit /b 1
)

:: Установка необходимых модулей
echo Установка необходимых модулей...
pip install pyinstaller telethon pillow

:: Запуск скрипта сборки
echo.
echo Запуск сборки EXE-файла...
python win10_build.py

:: Завершение
echo.
echo Нажмите любую клавишу для выхода...
pause > nul
'''
    
    # Записываем BAT-файл
    with open('build_kich_sms.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    logger.info("Создан файл build_kich_sms.bat для запуска сборки на Windows")

if __name__ == "__main__":
    print("=" * 60)
    print("СБОРКА KICH SMS EXE ДЛЯ WINDOWS 10")
    print("=" * 60)
    print("\nЭтот скрипт создаст оптимизированный EXE-файл, который будет")
    print("работать на Windows 10 без дополнительных библиотек и ошибок.\n")
    
    # Проверяем необходимые модули
    if not check_requirements():
        print("\nНевозможно продолжить: необходимые модули не установлены.")
        sys.exit(1)
    
    # Создаем BAT-файл
    create_batch_file()
    
    print("\nСоздаем два варианта EXE-файла для Windows 10:")
    print("1. Консольный вариант (простой)")
    print("2. С графическим интерфейсом (удобный)\n")
    
    # Создаем обычный EXE
    print("\nСоздание обычного EXE-файла...")
    if build_exe():
        print("✓ Обычный EXE-файл создан успешно!")
    else:
        print("✗ Не удалось создать обычный EXE-файл.")
    
    # Создаем улучшенный EXE с UI
    print("\nСоздание EXE-файла с графическим интерфейсом...")
    if build_improved_exe():
        print("✓ EXE-файл с интерфейсом создан успешно!")
    else:
        print("✗ Не удалось создать EXE-файл с интерфейсом.")
    
    print("\nВсе файлы созданы в папке 'dist'.")
    print("Для запуска сборки на Windows используйте файл 'build_kich_sms.bat'.")
    print("\nГотово! Нажмите Enter для выхода...")