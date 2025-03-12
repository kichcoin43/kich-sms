#!/bin/bash

echo "===== Подготовка проекта для деплоя на Render.com ====="

# Создание директории для базы данных
mkdir -p instance

# Проверка и создание директории ua_telegram_sender
if [ ! -d "ua_telegram_sender" ]; then
  echo "Создание директории ua_telegram_sender..."
  mkdir -p ua_telegram_sender
fi

# Проверка __init__.py в модуле
if [ ! -f "ua_telegram_sender/__init__.py" ]; then
  echo "Создание __init__.py в директории ua_telegram_sender..."
  echo '"""Модуль отправителя сообщений Telegram для украинских пользователей"""' > ua_telegram_sender/__init__.py
fi

# Убедимся, что render.yaml находится в правильном месте
if [ ! -f "render.yaml" ]; then
  echo "ОШИБКА: render.yaml не найден в текущей директории"
  exit 1
fi

# Проверка содержимого render.yaml
if ! grep -q "services:" render.yaml; then
  echo "ОШИБКА: render.yaml не содержит необходимой конфигурации"
  exit 1
fi

# Проверка наличия файла sender.py
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

# Отображение файловой структуры для диагностики
echo "Текущая структура каталогов:"
ls -la
echo "Содержимое ua_telegram_sender:"
ls -la ua_telegram_sender

echo "Файлы подготовлены для деплоя на Render.com"