
#!/bin/bash

echo "===== Подготовка проекта для деплоя на Render.com ====="

# Убедимся, что скрипт выполняется
chmod +x render-deploy.sh

# Создание директории для базы данных
mkdir -p instance

# Копирование render.yaml в корень, если он не там
cp -f render.yaml ./render.yaml

echo "Файлы подготовлены для деплоя на Render.com"
echo "Следуйте инструкциям на Render.com для загрузки проекта"
