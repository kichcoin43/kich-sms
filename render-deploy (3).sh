#!/bin/bash

echo "===== Подготовка проекта для деплоя на Render.com ====="

# Проверка структуры проекта
echo "Проверка структуры проекта..."

# Проверяем и создаём необходимые директории
mkdir -p instance
mkdir -p templates
mkdir -p static

# Проверяем наличие шаблонов и копируем их если нужно
if [ ! -f "templates/index.html" ]; then
  echo "Копирую шаблоны..."
  cp -r /opt/render/project/src/templates/* templates/ || echo "Ошибка копирования шаблонов!"
fi

# Проверяем права доступа
chmod -R 777 instance
echo "Права доступа установлены для директории instance"

# Проверка наличия статических файлов
if [ -d "static" ]; then
  echo "Статические файлы найдены"
else
  echo "Директория static не найдена, создаю..."
  mkdir -p static
fi


# Создание директории для базы данных (from original)

# Проверка и создание директории ua_telegram_sender (from original)
if [ ! -d "ua_telegram_sender" ]; then
  echo "Создание директории ua_telegram_sender..."
  mkdir -p ua_telegram_sender
fi

# Проверка __init__.py в модуле (from original)
if [ ! -f "ua_telegram_sender/__init__.py" ]; then
  echo "Создание __init__.py в директории ua_telegram_sender..."
  echo '"""Модуль отправителя сообщений Telegram для украинских пользователей"""' > ua_telegram_sender/__init__.py
fi

# Убедимся, что render.yaml находится в правильном месте (from original)
if [ ! -f "render.yaml" ]; then
  echo "ОШИБКА: render.yaml не найден в текущей директории"
  exit 1
fi

# Проверка содержимого render.yaml (from original)
if ! grep -q "services:" render.yaml; then
  echo "ОШИБКА: render.yaml не содержит необходимой конфигурации"
  exit 1
fi

# Проверка наличия файла sender.py (from original)
if [ ! -f "ua_telegram_sender/sender.py" ]; then
  echo "ВНИМАНИЕ: файл ua_telegram_sender/sender.py не найден"
  if [ -f "sender.py" ]; then
    echo "Копирование sender.py в ua_telegram_sender/..."
    cp sender.py ua_telegram_sender/
  fi
fi

echo "Файл render.yaml найден и корректен"
echo "Структура модуля проверена и подготовлена"
echo "Корневой каталог службы должен быть установлен как '/'"

# Отображение файловой структуры для диагностики (from original)
echo "Текущая структура каталогов:"
ls -la
echo "Содержимое ua_telegram_sender:"
ls -la ua_telegram_sender

echo "Файлы подготовлены для деплоя на Render.com"
echo "Проверка файлов завершена"
