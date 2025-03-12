
import os
import sys
import subprocess
import webbrowser
import tempfile

def print_banner():
    print("\n" + "=" * 60)
    print("KICH SMS - Помощник установки для Windows")
    print("=" * 60)

def check_python():
    """Проверяет установлен ли Python и доступен ли в системном пути"""
    try:
        # Пробуем выполнить python --version
        subprocess.check_call(["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except:
        return False

def check_pip():
    """Проверяет установлен ли pip и доступен ли в системном пути"""
    try:
        # Пробуем выполнить pip --version
        subprocess.check_call(["pip", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except:
        return False

def download_python():
    """Открывает страницу загрузки Python"""
    print("\nОткрываю страницу загрузки Python...")
    python_url = "https://www.python.org/downloads/"
    webbrowser.open(python_url)
    
    print("\nПОЖАЛУЙСТА, СЛЕДУЙТЕ ЭТИМ ШАГАМ:")
    print("1. Скачайте последнюю версию Python для Windows")
    print("2. ОБЯЗАТЕЛЬНО отметьте опцию 'Add Python to PATH' при установке")
    print("3. Завершите установку Python")
    print("4. Закройте и снова откройте эту командную строку")
    print("5. Снова запустите этот скрипт: python windows_setup.py")

def install_dependencies():
    """Устанавливает необходимые зависимости через pip"""
    print("\nУстанавливаем необходимые зависимости...")
    dependencies = [
        "telethon",
        "flask",
        "flask-sqlalchemy",
        "pillow"
    ]
    
    for dep in dependencies:
        print(f"Установка {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ {dep} успешно установлен")
        except Exception as e:
            print(f"✗ Ошибка при установке {dep}: {str(e)}")
            return False
    
    # Устанавливаем PyInstaller отдельно, пробуя разные версии при необходимости
    print(f"Установка PyInstaller...")
    pyinstaller_versions = ["pyinstaller==5.13.2", "pyinstaller==5.13.0", "pyinstaller==5.12.0", "pyinstaller==6.0.0", "pyinstaller"]
    
    for version in pyinstaller_versions:
        try:
            print(f"Пробуем установить {version}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", version])
            print(f"✓ {version} успешно установлен")
            return True
        except Exception as e:
            print(f"✗ Не удалось установить {version}: {str(e)}")
            print("Пробуем другую версию...")
    
    print("Не удалось установить PyInstaller. Попробуйте выполнить установку вручную:")
    print("pip install pyinstaller")
    return False
    
    return True

def run_build_script():
    """Запускает скрипт сборки EXE"""
    print("\nЗапускаем сборку EXE файла...")
    try:
        subprocess.check_call([sys.executable, "build_portable.py"])
        return True
    except Exception as e:
        print(f"Ошибка при сборке: {str(e)}")
        return False

def create_batch_file():
    """Создает BAT-файл для запуска скрипта в будущем"""
    with open("установить.bat", "w") as f:
        f.write("@echo off\n")
        f.write("echo Запуск установщика ГУЦУЛЬСКОЙ РАССЫЛКИ...\n")
        f.write("python windows_setup.py\n")
        f.write("pause\n")
    
    print("\nСоздан файл 'установить.bat' для удобного запуска этого скрипта в будущем.")

if __name__ == "__main__":
    print_banner()
    
    # Проверяем установлен ли Python
    if not check_python():
        print("\nPython не установлен или не добавлен в системный путь!")
        download_python()
        input("\nНажмите Enter для выхода...")
        sys.exit(1)
    
    # Проверяем установлен ли pip
    if not check_pip():
        print("\npip не установлен или не добавлен в системный путь!")
        print("Попробуем установить pip с помощью Python...")
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip"])
            print("pip успешно установлен!")
        except:
            print("Не удалось установить pip автоматически.")
            download_python()
            input("\nНажмите Enter для выхода...")
            sys.exit(1)
    
    # Создаем BAT-файл для удобства
    create_batch_file()
    
    # Устанавливаем зависимости
    if not install_dependencies():
        print("\nНе удалось установить все зависимости.")
        print("Попробуйте запустить скрипт снова или выполните установку вручную:")
        print("pip install telethon flask flask-sqlalchemy pillow pyinstaller==5.13.2")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)
    
    # Запускаем сборку
    if run_build_script():
        print("\n" + "=" * 60)
        print("СБОРКА УСПЕШНО ЗАВЕРШЕНА!")
        print("=" * 60)
        print("\nEXE-файл создан в папке dist_windows")
        print("Теперь вы можете использовать ГУЦУЛЬСКАЯ_РАССЫЛКА.exe для отправки сообщений")
    else:
        print("\n" + "=" * 60)
        print("СБОРКА НЕ УДАЛАСЬ")
        print("=" * 60)
        print("\nПожалуйста, проверьте ошибки выше или используйте прямой запуск:")
        print("python app.py")
    
    input("\nНажмите Enter для выхода...")
