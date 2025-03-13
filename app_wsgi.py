
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Простой wsgi файл для gunicorn
from app import app

# Экспортируем как application для совместимости со стандартами WSGI
application = app
