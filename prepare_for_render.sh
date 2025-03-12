
#!/bin/bash

echo "===== Подготовка проекта для деплоя на Render.com ====="

# Создание необходимых директорий
mkdir -p instance

# Проверка наличия всех необходимых файлов
echo "Проверка файлов проекта..."
REQUIRED_FILES=("main.py" "app.py" "requirements.txt" "render.yaml")
MISSING=0

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "ОШИБКА: Файл $file не найден!"
    MISSING=1
  else
    echo "OK: Файл $file найден"
  fi
done

if [ $MISSING -eq 1 ]; then
  echo "Пожалуйста, убедитесь, что все необходимые файлы существуют."
  exit 1
fi

# Проверка requirements.txt
echo "Проверка файла requirements.txt..."
if ! grep -q "gunicorn" requirements.txt; then
  echo "Добавление gunicorn в requirements.txt..."
  echo "gunicorn>=20.1.0" >> requirements.txt
fi

echo "Проверка файла .gitignore..."
if [ ! -f ".gitignore" ]; then
  echo "Создание файла .gitignore..."
  cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
*.session
*.session-journal
EOF
fi

echo "===== Проект готов к деплою на Render.com! ====="
echo "Следуйте инструкциям в файле RENDER_DEPLOYMENT_GUIDE.md для деплоя."
