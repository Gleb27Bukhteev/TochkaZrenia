#!/usr/bin/env python3
"""
Скрипт для подготовки проекта к загрузке в Git
Удаляет большие файлы и создает необходимые структуры
"""

import os
import shutil
import sys

def remove_large_files():
    """Удаление больших файлов, которые не должны попасть в Git"""
    print("🗑️  Удаление больших файлов...")
    
    # Удаляем папку OpenCV
    opencv_path = "CamCode/opencv"
    if os.path.exists(opencv_path):
        print(f"   Удаляем {opencv_path}")
        shutil.rmtree(opencv_path)
    
    # Удаляем файл логов
    log_file = "Site/templates/log.txt"
    if os.path.exists(log_file):
        print(f"   Удаляем {log_file}")
        os.remove(log_file)
    
    # Удаляем кэш Python
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                print(f"   Удаляем {cache_path}")
                shutil.rmtree(cache_path)
    
    print("✅ Большие файлы удалены")

def create_git_structure():
    """Создание структуры для Git"""
    print("📁 Создание структуры для Git...")
    
    # Создаем пустой файл логов
    log_file = "Site/templates/log.txt"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("# Логи мониторинга камер\n")
        f.write("# Этот файл будет автоматически заполняться при работе системы\n")
    
    print("✅ Структура создана")

def check_git_ready():
    """Проверка готовности к Git"""
    print("🔍 Проверка готовности к Git...")
    
    # Проверяем наличие .gitignore
    if not os.path.exists(".gitignore"):
        print("❌ Файл .gitignore не найден!")
        return False
    
    # Проверяем наличие requirements.txt
    if not os.path.exists("requirements.txt"):
        print("❌ Файл requirements.txt не найден!")
        return False
    
    # Проверяем размер файлов
    large_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.startswith('.'):
                continue
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 50 * 1024 * 1024:  # 50MB
                    large_files.append((file_path, size))
            except:
                pass
    
    if large_files:
        print("⚠️  Найдены большие файлы:")
        for file_path, size in large_files:
            print(f"   {file_path}: {size / 1024 / 1024:.1f}MB")
        return False
    
    print("✅ Проект готов к Git!")
    return True

def show_git_commands():
    """Показ команд для Git"""
    print("\n🚀 Команды для загрузки в Git:")
    print("=" * 50)
    print("1. Инициализация Git:")
    print("   git init")
    print()
    print("2. Добавление файлов:")
    print("   git add .")
    print()
    print("3. Первый коммит:")
    print("   git commit -m \"Initial commit: Camera monitoring system\"")
    print()
    print("4. Добавление удаленного репозитория:")
    print("   git remote add origin <URL_ВАШЕГО_РЕПОЗИТОРИЯ>")
    print()
    print("5. Загрузка в репозиторий:")
    print("   git push -u origin main")
    print()
    print("📖 Подробная инструкция в DEPLOYMENT.md")

def main():
    print("🎥 Подготовка проекта мониторинга камер к Git")
    print("=" * 50)
    
    # Удаляем большие файлы
    remove_large_files()
    
    # Создаем структуру
    create_git_structure()
    
    # Проверяем готовность
    if check_git_ready():
        show_git_commands()
    else:
        print("\n❌ Проект не готов к Git. Исправьте ошибки выше.")
        sys.exit(1)

if __name__ == "__main__":
    main()
