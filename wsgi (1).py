
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

try:
    # Проверяем и создаем директорию instance заранее
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(BASE_DIR, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    
    # Устанавливаем права доступа
    os.chmod(instance_dir, 0o777)
    logger.info(f"WSGI: директория instance создана с правами доступа")
    
    # Импортируем приложение
    from app import app
    
    # Экспортируем как application и app для совместимости
    application = app
    
    logger.info("WSGI: приложение успешно инициализировано")
except Exception as e:
    logger.error(f"WSGI: ошибка инициализации приложения: {e}")
    import traceback
    logger.error(traceback.format_exc())
    
    # Создаем простое приложение-заглушку для диагностики
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/')
    def error_handler():
        return jsonify({
            "error": "Возникла ошибка при инициализации приложения",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

