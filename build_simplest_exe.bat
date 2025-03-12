@echo off
echo ============================================================
echo   СОЗДАНИЕ EXE-ФАЙЛА МУЛЬТИ-АККАУНТ TELEGRAM ОТПРАВИТЕЛЯ
echo ============================================================
echo.

:: Проверка Python
python --version > nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не установлен или не доступен в системном пути.
    echo Загрузите и установите Python с сайта https://www.python.org/downloads/
    echo.
    echo После установки Python запустите этот файл снова.
    pause
    exit /b 1
)

:: Установка необходимых модулей
echo Установка необходимых модулей...
pip install pyinstaller telethon

:: Создание директории для сессий
if not exist "telegram_sessions" mkdir telegram_sessions

:: Создание файла для получателей, если его нет
if not exist "telegram_recipients.txt" (
    echo # Список получателей сообщений Telegram > telegram_recipients.txt
    echo # Добавляйте по одному получателю на строку >> telegram_recipients.txt
    echo # Примеры: >> telegram_recipients.txt
    echo # @username >> telegram_recipients.txt
    echo # +79001234567 >> telegram_recipients.txt
)

:: Создание EXE-файла
echo.
echo Создание EXE-файла...
pyinstaller --onefile --clean --noconfirm --name "Telegram_Multi_Account" simple_multi_account.py

:: Проверка успешности создания
if exist "dist\Telegram_Multi_Account.exe" (
    echo.
    echo ✅ EXE-файл успешно создан!
    echo Расположение: %cd%\dist\Telegram_Multi_Account.exe
    
    :: Копирование необходимых файлов 
    mkdir "dist\telegram_sessions" 2>nul
    
    echo.
    echo Создание README файла...
    
    echo МУЛЬТИ-АККАУНТ ОТПРАВИТЕЛЬ TELEGRAM > "dist\README.txt"
    echo ===================================== >> "dist\README.txt"
    echo. >> "dist\README.txt"
    echo Эта программа позволяет отправлять сообщения Telegram с нескольких аккаунтов. >> "dist\README.txt"
    echo. >> "dist\README.txt"
    echo ВАЖНАЯ ИНФОРМАЦИЯ О КНОПКАХ: >> "dist\README.txt"
    echo - "Добавить аккаунт" - создает новый аккаунт Telegram >> "dist\README.txt"
    echo - "Выйти из аккаунта" - полностью удаляет аккаунт из программы >> "dist\README.txt"
    echo. >> "dist\README.txt"
    echo Инструкция: >> "dist\README.txt"
    echo 1. Запустите Telegram_Multi_Account.exe >> "dist\README.txt"
    echo 2. Нажмите "Добавить аккаунт" и следуйте инструкциям >> "dist\README.txt"
    echo 3. Добавьте получателей в поле "Получатели" >> "dist\README.txt"
    echo 4. Введите текст сообщения и нажмите "Отправить сообщения" >> "dist\README.txt"
    
    echo ✅ Готово! Теперь вы можете использовать программу из папки dist.
) else (
    echo.
    echo ❌ Не удалось создать EXE-файл.
    echo Проверьте, что PyInstaller установлен правильно.
)

:: Создание ZIP-архива с файлами
echo.
echo Создание ZIP-архива...
powershell Compress-Archive -Path dist\* -DestinationPath Telegram_Multi_Account.zip -Force

if exist "Telegram_Multi_Account.zip" (
    echo ✅ ZIP-архив успешно создан: %cd%\Telegram_Multi_Account.zip
) else (
    echo ❌ Не удалось создать ZIP-архив.
)

:: Завершение
echo.
echo ✅ Сборка завершена!
echo.
echo Нажмите любую клавишу для выхода...
pause > nul