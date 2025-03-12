
#!/bin/bash

echo "===== Подготовка проекта для деплоя на Render.com ====="

# Убедимся, что скрипт выполняется
chmod +x render-deploy.sh

# Создание директории для базы данных
mkdir -p instance

# Проверка наличия файла render.yaml
if [ ! -f "/opt/render/project/src/render.yaml" ]; then
  echo "Файл render.yaml не найден в /opt/render/project/src/, копируем..."
  cp -f render.yaml /opt/render/project/src/render.yaml 2>/dev/null || echo "Не удалось скопировать render.yaml"
fi

echo "Файлы подготовлены для деплоя на Render.com"
echo "Следуйте инструкциям на Render.com для загрузки проекта"
