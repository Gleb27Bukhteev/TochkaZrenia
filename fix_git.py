#!/usr/bin/env python3
"""
Скрипт для исправления проблем с Git
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Выполнение команды с описанием"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout.strip():
                print(f"   Вывод: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - ошибка")
            if result.stderr.strip():
                print(f"   Ошибка: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def check_git_installed():
    """Проверка установки Git"""
    print("🔍 Проверка установки Git...")
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git установлен: {result.stdout.strip()}")
            return True
        else:
            print("❌ Git не установлен")
            return False
    except FileNotFoundError:
        print("❌ Git не найден в PATH")
        return False

def fix_git_repository():
    """Исправление Git репозитория"""
    print("\n🛠️ Исправление Git репозитория...")
    
    # Проверка существования .git
    if not os.path.exists('.git'):
        print("📁 Инициализация Git репозитория...")
        if not run_command('git init', 'Инициализация Git'):
            return False
    
    # Проверка статуса
    print("\n📊 Проверка статуса Git...")
    run_command('git status', 'Проверка статуса')
    
    # Добавление файлов
    print("\n📁 Добавление файлов...")
    if not run_command('git add .', 'Добавление файлов'):
        return False
    
    # Проверка коммитов
    print("\n📝 Проверка коммитов...")
    result = subprocess.run(['git', 'log', '--oneline'], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print("📝 Создание первого коммита...")
        if not run_command('git commit -m "Initial commit: Camera monitoring system with OpenCV"', 'Создание коммита'):
            return False
    else:
        print("✅ Коммиты уже существуют")
    
    # Проверка веток
    print("\n🌿 Проверка веток...")
    result = subprocess.run(['git', 'branch'], capture_output=True, text=True)
    if result.returncode == 0:
        branches = result.stdout.strip().split('\n')
        current_branch = None
        for branch in branches:
            if branch.startswith('*'):
                current_branch = branch[2:].strip()
                break
        
        print(f"📋 Текущая ветка: {current_branch}")
        
        if current_branch != 'main':
            print("🔄 Переименование ветки в main...")
            if not run_command('git branch -M main', 'Переименование ветки'):
                return False
    
    return True

def check_remote_repository():
    """Проверка удаленного репозитория"""
    print("\n🌐 Проверка удаленного репозитория...")
    result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        print("✅ Удаленный репозиторий настроен")
        print(f"   {result.stdout.strip()}")
        return True
    else:
        print("❌ Удаленный репозиторий не настроен")
        return False

def setup_remote_repository():
    """Настройка удаленного репозитория"""
    print("\n🌐 Настройка удаленного репозитория...")
    remote_url = "https://github.com/Gleb27Bukhteev/TochkaZrenia.git"
    
    print(f"🔗 Добавление удаленного репозитория: {remote_url}")
    if not run_command(f'git remote add origin {remote_url}', 'Добавление удаленного репозитория'):
        return False
    
    return True

def push_to_remote():
    """Загрузка в удаленный репозиторий"""
    print("\n🚀 Загрузка в удаленный репозиторий...")
    if not run_command('git push -u origin main', 'Загрузка в репозиторий'):
        return False
    return True

def main():
    print("🔧 Исправление проблем с Git")
    print("=" * 50)
    
    # Проверка Git
    if not check_git_installed():
        print("\n❌ Git не установлен!")
        print("📥 Установите Git for Windows: https://git-scm.com/download/win")
        print("   Или через winget: winget install Git.Git")
        sys.exit(1)
    
    # Исправление репозитория
    if not fix_git_repository():
        print("\n❌ Ошибка исправления репозитория")
        sys.exit(1)
    
    # Проверка удаленного репозитория
    if not check_remote_repository():
        if not setup_remote_repository():
            print("\n❌ Ошибка настройки удаленного репозитория")
            sys.exit(1)
    
    # Загрузка в репозиторий
    if not push_to_remote():
        print("\n❌ Ошибка загрузки в репозиторий")
        print("🔍 Проверьте:")
        print("   - Существует ли репозиторий на GitHub")
        print("   - Правильные ли права доступа")
        print("   - Правильный ли URL репозитория")
        sys.exit(1)
    
    print("\n🎉 Успешно! Проект загружен в Git!")
    print("🌐 Репозиторий: https://github.com/Gleb27Bukhteev/TochkaZrenia")

if __name__ == "__main__":
    main()
