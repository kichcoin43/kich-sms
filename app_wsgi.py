
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Этот файл служит альтернативной точкой входа для gunicorn
# Импортируем app из app.py и экспортируем как application
from app import app as application

# Экспортируем как app для совместимости с gunicorn
app = application
