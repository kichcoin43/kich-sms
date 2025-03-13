
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import shutil

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Проверяем и копируем шаблоны
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(BASE_DIR, "templates")
instance_dir = os.path.join(BASE_DIR, "instance")

# Создаем директории
os.makedirs(template_dir, exist_ok=True)
os.makedirs(instance_dir, exist_ok=True)

# Устанавливаем права доступа
os.chmod(instance_dir, 0o777)
logger.info(f"Установлены права доступа для директорий {instance_dir}")

# Проверяем наличие шаблонов
if not os.path.exists(os.path.join(template_dir, "index.html")):
    logger.error(f"Шаблон index.html не найден! Содержимое директории templates: {os.listdir(template_dir)}")
    # Пытаемся создать базовый шаблон, если его нет
    with open(os.path.join(template_dir, "index.html"), "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>KICH SMS</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>KICH SMS</h1>
        <p>Приложение успешно запущено!</p>
        <div class="mt-4">
            <a href="/auth" class="btn btn-primary">Авторизация в Telegram</a>
            <a href="/recipients" class="btn btn-success">Управление получателями</a>
            <a href="/send" class="btn btn-info">Отправить сообщения</a>
        </div>
    </div>
</body>
</html>
        """)
    logger.info("Создан базовый шаблон index.html")

# Простой wsgi файл для gunicorn
from app import app

# Экспортируем как application для совместимости со стандартами WSGI
application = app
