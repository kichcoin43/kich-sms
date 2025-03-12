
"""
Відправник повідомлень Telegram для України
==========================================

Пакет для масової відправки повідомлень українським користувачам Telegram.
"""

# Экспортируем основной класс для прямого импорта
try:
    from .sender import UkrainianTelegramSender as UkraineTelegramSender
    # Обратная совместимость
    from .sender import UkrainianTelegramSender
except ImportError:
    UkraineTelegramSender = None
    UkrainianTelegramSender = None
