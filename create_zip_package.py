#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для создания ZIP-пакета с файлами отправителя Telegram для Windows 10
"""

import os
import zipfile
import shutil
import datetime

# Имя ZIP-файла
timestamp = datetime.datetime.now().strftime("%Y%m%d")
ZIP_FILENAME = f"Telegram_Sender_Win10_{timestamp}.zip"

# Список файлов для включения в архив
FILES_TO_INCLUDE = [
    "easy_telegram_sender.py",
    "windows10_sender.py",
    "WINDOWS10_EXE_GUIDE.md",
    "windows10_exe_build.bat"
]

# Создаем папку для дополнительных файлов
if not os.path.exists("dist"):
    os.makedirs("dist")

# Создаем текстовый файл с инструкциями
readme_content = """ОТПРАВИТЕЛЬ СООБЩЕНИЙ TELEGRAM ДЛЯ WINDOWS 10
================================================

Это набор файлов для создания работающего EXE-файла отправителя
сообщений Telegram, который гарантированно работает на Windows 10.

СОДЕРЖИМОЕ:
-----------
1. easy_telegram_sender.py - простая версия скрипта
2. windows10_sender.py - расширенная версия с подробными логами
3. WINDOWS10_EXE_GUIDE.md - подробное руководство в формате Markdown
4. windows10_exe_build.bat - автоматический сборщик EXE-файла
5. README.txt - этот файл

КАК ИСПОЛЬЗОВАТЬ:
----------------
Вариант 1 (самый простой):
1. Установите Python 3.8 или новее с сайта python.org
2. Установите библиотеку: pip install telethon
3. Запустите скрипт: python easy_telegram_sender.py
4. Следуйте инструкциям на экране

Вариант 2 (создание EXE):
1. Установите Python 3.8 или новее
2. Запустите файл windows10_exe_build.bat
3. Найдите готовый EXE-файл в папке dist

ПРОБЛЕМЫ:
---------
Если у вас возникли проблемы с запуском программы:
1. Проверьте, что Python установлен и доступен в системном пути
2. Убедитесь, что установлена библиотека telethon
3. Проверьте, не блокирует ли антивирус запуск программы
4. Попробуйте запустить от имени администратора

Более подробная информация доступна в файле WINDOWS10_EXE_GUIDE.md
"""

with open("dist/README.txt", "w", encoding="utf-8") as f:
    f.write(readme_content)

# Создаем файл с получателями
recipients_content = """# Список получателей сообщений Telegram
# Добавляйте по одному получателю на строку
# Можно указывать @username или номер телефона с '+'
# Пример:
# @username
# +79001234567
"""

with open("dist/recipients.txt", "w", encoding="utf-8") as f:
    f.write(recipients_content)

# Добавляем файлы в архив
print(f"Создание архива {ZIP_FILENAME}...")

with zipfile.ZipFile(ZIP_FILENAME, "w", zipfile.ZIP_DEFLATED) as zipf:
    # Добавляем основные файлы
    for file in FILES_TO_INCLUDE:
        if os.path.exists(file):
            zipf.write(file)
            print(f"Добавлен файл: {file}")
        else:
            print(f"Предупреждение: файл {file} не найден")
            
    # Добавляем дополнительные файлы из папки dist
    for file in os.listdir("dist"):
        file_path = os.path.join("dist", file)
        if os.path.isfile(file_path):
            zipf.write(file_path, file)  # Сохраняем без пути dist/
            print(f"Добавлен файл: {file}")

print(f"\nАрхив успешно создан: {ZIP_FILENAME}")
print(f"Размер: {os.path.getsize(ZIP_FILENAME) / 1024:.1f} КБ")
print("\nТеперь вы можете скачать этот архив и использовать файлы на Windows 10.")

# Вывод инструкции
print("\nИНСТРУКЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ:")
print("1. Скачайте архив")
print("2. Распакуйте все файлы в одну папку")
print("3. Используйте один из вариантов:")
print("   - Запустите скрипт Python: python easy_telegram_sender.py")
print("   - Создайте EXE-файл: запустите windows10_exe_build.bat")
print("4. Следуйте инструкциям программы")