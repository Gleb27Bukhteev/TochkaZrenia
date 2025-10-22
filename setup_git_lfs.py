#!/usr/bin/env python3
"""
Скрипт для настройки Git LFS для проекта мониторинга камер
"""

import os
import subprocess
import sys

def check_git_lfs():
    """Проверка установки Git LFS"""
    try:
        result = subprocess.run(['git', 'lfs', 'version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git LFS установлен")
            return True
        else:
            print("❌ Git LFS не установлен")
            return False
    except FileNotFoundError:
        print("❌ Git LFS не найден")
        return False

def install_git_lfs_instructions():
    """Инструкции по установке Git LFS"""
    print("\n📋 Инструкции по установке Git LFS:")
    print("=" * 50)
    print("Windows:")
    print("  - Скачайте Git for Windows (включает Git LFS)")
    print("  - Или: winget install Git.Git")
    print()
    print("Linux (Ubuntu/Debian):")
    print("  sudo apt update")
    print("  sudo apt install git-lfs")
    print()
    print("macOS:")
    print("  brew install git-lfs")
    print()
    print("После установки выполните:")
    print("  git lfs install")

def setup_git_lfs():
    """Настройка Git LFS"""
    print("🔧 Настройка Git LFS...")
    
    # Инициализация Git LFS
    try:
        subprocess.run(['git', 'lfs', 'install'], check=True)
        print("✅ Git LFS инициализирован")
    except subprocess.CalledProcessError:
        print("❌ Ошибка инициализации Git LFS")
        return False
    
    # Проверка .gitattributes
    if os.path.exists('.gitattributes'):
        print("✅ Файл .gitattributes найден")
    else:
        print("❌ Файл .gitattributes не найден")
        return False
    
    return True

def check_large_files():
    """Проверка больших файлов"""
    print("\n🔍 Проверка больших файлов...")
    
    large_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.startswith('.'):
                continue
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 10 * 1024 * 1024:  # 10MB
                    large_files.append((file_path, size))
            except:
                pass
    
    if large_files:
        print("📊 Найдены большие файлы:")
        for file_path, size in large_files:
            print(f"   {file_path}: {size / 1024 / 1024:.1f}MB")
    else:
        print("✅ Больших файлов не найдено")
    
    return large_files

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
    print("   git commit -m \"Initial commit: Camera monitoring system with OpenCV\"")
    print()
    print("4. Добавление удаленного репозитория:")
    print("   git remote add origin <URL_ВАШЕГО_РЕПОЗИТОРИЯ>")
    print()
    print("5. Загрузка в репозиторий:")
    print("   git push -u origin main")
    print()
    print("📖 Подробная инструкция в GIT_SOLUTIONS.md")

def main():
    print("🎥 Настройка Git LFS для проекта мониторинга камер")
    print("=" * 60)
    
    # Проверка Git LFS
    if not check_git_lfs():
        install_git_lfs_instructions()
        print("\n❌ Установите Git LFS и запустите скрипт снова")
        sys.exit(1)
    
    # Настройка Git LFS
    if not setup_git_lfs():
        print("\n❌ Ошибка настройки Git LFS")
        sys.exit(1)
    
    # Проверка больших файлов
    large_files = check_large_files()
    
    if large_files:
        print(f"\n⚠️  Найдено {len(large_files)} больших файлов")
        print("   Они будут загружены через Git LFS")
    else:
        print("\n✅ Больших файлов не найдено")
    
    # Показ команд
    show_git_commands()
    
    print("\n🎉 Git LFS настроен! Теперь можно загружать проект в Git")

if __name__ == "__main__":
    main()
