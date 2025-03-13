
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Получаем текущий путь
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Импортируем app из app.py
from app import app as application

# Чтобы gunicorn мог найти приложение
app = application

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
