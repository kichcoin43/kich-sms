@echo off
echo ============================================================
echo   СОЗДАНИЕ EXE-ФАЙЛА TELEGRAM-ОТПРАВИТЕЛЯ ДЛЯ WINDOWS 10
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
pip install pyinstaller telethon pillow

:: Создание EXE-файла
echo.
echo Создание EXE-файла для отправителя Telegram...
pyinstaller --onefile --clean --noconfirm --name "Telegram_Sender_Win10" easy_telegram_sender.py

:: Проверка успешности создания
if exist "dist\Telegram_Sender_Win10.exe" (
    echo.
    echo ✅ EXE-файл успешно создан!
    echo Расположение: %cd%\dist\Telegram_Sender_Win10.exe
    echo.
    echo Теперь вы можете скопировать этот файл куда угодно и запустить.
) else (
    echo.
    echo ❌ Не удалось создать EXE-файл.
    echo Проверьте, что PyInstaller установлен правильно.
)

:: Создание версии с графическим интерфейсом
echo.
echo Создание EXE-файла с графическим интерфейсом...
pyinstaller --onefile --windowed --clean --noconfirm --name "Telegram_Sender_Win10_UI" windows10_sender.py

:: Проверка успешности создания
if exist "dist\Telegram_Sender_Win10_UI.exe" (
    echo.
    echo ✅ EXE-файл с графическим интерфейсом успешно создан!
    echo Расположение: %cd%\dist\Telegram_Sender_Win10_UI.exe
    echo.
    echo Рекомендуется использовать эту версию для более удобной работы.
) else (
    echo.
    echo ❌ Не удалось создать EXE-файл с графическим интерфейсом.
)

:: Создание readme.txt
echo Создание справочного файла...
echo ============================================================ > "dist\Как использовать.txt"
echo   ОТПРАВИТЕЛЬ СООБЩЕНИЙ TELEGRAM ДЛЯ WINDOWS 10 >> "dist\Как использовать.txt"
echo ============================================================ >> "dist\Как использовать.txt"
echo. >> "dist\Как использовать.txt"
echo Инструкция по использованию: >> "dist\Как использовать.txt"
echo. >> "dist\Как использовать.txt"
echo 1. Создайте файл recipients.txt в той же папке, где находится EXE-файл >> "dist\Как использовать.txt"
echo 2. Добавьте в этот файл получателей (по одному на строку) >> "dist\Как использовать.txt"
echo    Например: @username или +79001234567 >> "dist\Как использовать.txt"
echo 3. Запустите EXE-файл >> "dist\Как использовать.txt"
echo 4. Войдите в аккаунт Telegram, если нужно >> "dist\Как использовать.txt"
echo 5. Введите текст сообщения и следуйте инструкциям >> "dist\Как использовать.txt"
echo. >> "dist\Как использовать.txt"
echo ============================================================ >> "dist\Как использовать.txt"

echo Создание пустого файла для получателей...
echo # Список получателей (по одному на строку) > "dist\recipients.txt"
echo # Примеры: >> "dist\recipients.txt"
echo # @username >> "dist\recipients.txt"
echo # +79001234567 >> "dist\recipients.txt"

:: Завершение
echo.
echo ✅ Файлы успешно созданы в папке dist!
echo.
echo Нажмите любую клавишу для выхода...
pause > nul