
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Утилита для импорта получателей в базу данных
"""

import os
import sys
import logging
from app import db
from models import Recipient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def import_recipients_from_file(file_path):
    """Импортирует получателей из файла в базу данных"""
    if not os.path.exists(file_path):
        logger.error(f"Файл {file_path} не найден")
        return False
        
    try:
        # Считываем получателей из файла
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Фильтруем пустые строки и комментарии
        recipients = [line.strip() for line in lines 
                     if line.strip() and not line.strip().startswith('#')]
        
        logger.info(f"Найдено {len(recipients)} получателей в файле")
        
        # Добавляем получателей в базу данных
        added_count = 0
        skipped_count = 0
        
        for recipient in recipients:
            # Проверяем существование получателя
            existing = Recipient.query.filter_by(identifier=recipient).first()
            if not existing:
                new_recipient = Recipient(identifier=recipient)
                db.session.add(new_recipient)
                added_count += 1
            else:
                skipped_count += 1
                
        # Сохраняем изменения
        db.session.commit()
        
        logger.info(f"Добавлено {added_count} получателей, пропущено {skipped_count} дубликатов")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка импорта получателей: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    print("\n==== ИМПОРТ ПОЛУЧАТЕЛЕЙ В БАЗУ ДАННЫХ ====\n")
    
    # Проверяем наличие файла получателей
    file_path = "recipients.txt"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    print(f"Импорт получателей из файла: {file_path}\n")
    
    if import_recipients_from_file(file_path):
        print("\n✅ Импорт успешно завершен!")
    else:
        print("\n❌ Ошибка импорта получателей!")
