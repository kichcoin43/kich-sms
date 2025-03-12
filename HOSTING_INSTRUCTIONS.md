
# Перенос KICH SMS на Render.com

## Шаги по переносу:

1. Создайте аккаунт на [Render.com](https://render.com) (бесплатно)
2. Нажмите "New" -> "Web Service"
3. Подключите GitHub или загрузите код напрямую
4. Укажите следующие настройки:
   - Name: kich-sms-telegram
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
   - Plan: Free

## Настройка переменных окружения:
1. В разделе "Environment" добавьте следующие переменные:
   - TELEGRAM_API_ID
   - TELEGRAM_API_HASH
   - SESSION_SECRET (произвольное значение)
   - DATABASE_URL=sqlite:///instance/telegram_sender.db

## Преимущества Render.com:
- Полностью бесплатный план
- Без необходимости обновления
- Автоматический перезапуск при сбоях
- SSL-сертификат включен
- Персональный домен формата https://kich-sms-telegram.onrender.com
