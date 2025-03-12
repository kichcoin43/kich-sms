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

:: Создание директории для результатов сборки
if not exist "bin" mkdir bin

:: Создание файла для получателей, если его нет
if not exist "recipients.txt" (
    echo # Список получателей сообщений Telegram > recipients.txt
    echo # Добавляйте по одному получателю на строку >> recipients.txt
    echo # Примеры: >> recipients.txt
    echo # @username >> recipients.txt
    echo # +79001234567 >> recipients.txt
)

:: Создание EXE-файла
echo.
echo Создание EXE-файла...
pyinstaller --onefile --clean --noconfirm --name "Telegram_Multi_Account" multi_account_telegram.py

:: Проверка успешности создания
if exist "dist\Telegram_Multi_Account.exe" (
    echo.
    echo ✅ EXE-файл успешно создан!
    echo Расположение: %cd%\dist\Telegram_Multi_Account.exe
    
    :: Копирование EXE-файла в папку bin
    copy "dist\Telegram_Multi_Account.exe" "bin\" > nul
    
    echo.
    echo Копирование файлов...
    
    :: Копирование других необходимых файлов
    if exist "recipients.txt" copy "recipients.txt" "bin\" > nul
    
    :: Создаем README файл
    echo МУЛЬТИ-АККАУНТ ОТПРАВИТЕЛЬ TELEGRAM > "bin\README.txt"
    echo ===================================== >> "bin\README.txt"
    echo. >> "bin\README.txt"
    echo Эта программа позволяет отправлять сообщения Telegram с нескольких аккаунтов. >> "bin\README.txt"
    echo. >> "bin\README.txt"
    echo Особенности: >> "bin\README.txt"
    echo - Поддержка нескольких аккаунтов Telegram >> "bin\README.txt"
    echo - Возможность входа и выхода из аккаунтов >> "bin\README.txt"
    echo - Работа с графическим интерфейсом или в консоли >> "bin\README.txt"
    echo - Безопасное хранение данных аккаунтов >> "bin\README.txt"
    echo. >> "bin\README.txt"
    echo Инструкция: >> "bin\README.txt"
    echo 1. Запустите Telegram_Multi_Account.exe >> "bin\README.txt"
    echo 2. Добавьте аккаунт, выполнив вход в Telegram >> "bin\README.txt"
    echo 3. Добавьте получателей в файл recipients.txt >> "bin\README.txt"
    echo 4. Выберите получателей и отправьте сообщение >> "bin\README.txt"
    echo. >> "bin\README.txt"
    echo При возникновении проблем обратитесь к разработчику. >> "bin\README.txt"
    
    echo ✅ Все файлы скопированы в папку bin!
    echo Теперь вы можете использовать программу из этой папки.
) else (
    echo.
    echo ❌ Не удалось создать EXE-файл.
    echo Проверьте, что PyInstaller установлен правильно.
)

:: Создание версии с консольным интерфейсом
echo.
echo Создание консольной версии EXE-файла...
pyinstaller --onefile --clean --noconfirm --name "Telegram_Multi_Account_Console" multi_account_telegram.py

:: Проверка успешности создания
if exist "dist\Telegram_Multi_Account_Console.exe" (
    :: Копирование EXE-файла в папку bin
    copy "dist\Telegram_Multi_Account_Console.exe" "bin\" > nul
    echo ✅ Консольная версия EXE-файла создана!
) else (
    echo ❌ Не удалось создать консольную версию EXE-файла.
)

:: Создание ZIP-архива с файлами
echo.
echo Создание ZIP-архива...
powershell Compress-Archive -Path bin\* -DestinationPath Telegram_Multi_Account.zip -Force

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