@echo off
echo ============================================================
echo   СБОРКА ОТПРАВИТЕЛЯ TELEGRAM EXE ДЛЯ WINDOWS 10
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

:: Запуск скрипта сборки
echo.
echo Запуск сборки EXE-файла...
python win10_build.py

:: Завершение
echo.
echo Нажмите любую клавишу для выхода...
pause > nul
