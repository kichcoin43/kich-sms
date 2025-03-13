
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Максимально простой wsgi файл
from app import app

# Экспортируем как application и app для совместимости
application = app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
