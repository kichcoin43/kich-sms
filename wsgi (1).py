
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Добавляем текущую директорию в sys.path для поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Импортируем app из app.py
from app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
