
@echo off
echo =====================================================
echo ГУЦУЛЬСКАЯ РАССЫЛКА - УСТАНОВКА ДЛЯ WINDOWS
echo =====================================================
echo.
echo Этот файл поможет установить все необходимое для работы программы
echo.

echo Проверка версии Python...
python --version 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Не удалось найти Python. Python не установлен или не добавлен в PATH.
  echo.
  echo Пожалуйста, установите Python с сайта www.python.org/downloads/
  echo При установке ОБЯЗАТЕЛЬНО отметьте галочку "Add Python to PATH"
  echo.
  echo После установки Python запустите этот файл снова.
  echo.
  pause
  exit /b 1
)

echo.
echo Обновление pip до последней версии...
python -m pip install --upgrade pip

echo.
echo Нажмите любую клавишу для начала установки...
pause > nul

python windows_setup.py

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Возникла ошибка при установке. 
  echo.
  echo Попробуйте запустить следующие команды вручную:
  echo python -m pip install telethon flask flask-sqlalchemy pillow
  echo python -m pip install pyinstaller
  echo.
  echo Затем запустите windows_setup.py снова:
  echo python windows_setup.py
  echo.
  pause
  exit /b 1
)

echo.
echo Установка завершена!
pause
