# 📤 Инструкция по загрузке в Git с OpenCV

## ✅ Решение: Git LFS (Large File Storage)

**НЕ УДАЛЯЙТЕ** папку `CamCode/opencv/` - она содержит необходимые библиотеки OpenCV!

### 1. Установка Git LFS

**Windows:**
```bash
# Git for Windows уже включает Git LFS
# Или установите отдельно:
winget install Git.Git
```

**Linux:**
```bash
sudo apt update
sudo apt install git-lfs
```

**macOS:**
```bash
brew install git-lfs
```

### 2. Настройка Git LFS

```bash
# Инициализация Git LFS
git lfs install

# Инициализация Git
git init

# Добавление файлов
git add .

# Первый коммит
git commit -m "Initial commit: Camera monitoring system with OpenCV"
```

### 3. Добавление удаленного репозитория

```bash
# Добавление удаленного репозитория (замените на ваш URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Загрузка в репозиторий
git push -u origin main
```

### 4. Автоматическая настройка

Запустите скрипт для автоматической настройки:

```bash
python setup_git_lfs.py
```

## 📁 Что попадет в Git

✅ **Включено:**
- `CamCode/index.py` - основной скрипт
- `CamCode/server.py` - Flask сервер
- `Site/` - веб-интерфейс
- `README.md` - документация
- `requirements.txt` - зависимости
- `.gitignore` - исключения

❌ **Исключено:**
- `CamCode/opencv/` - папка OpenCV
- `Site/templates/log.txt` - файл логов
- `__pycache__/` - кэш Python
- Большие медиафайлы

## 🚀 Установка на новом сервере

После клонирования репозитория:

```bash
# Клонирование
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd Khakaton_TochkaZrenia

# Установка зависимостей
pip install -r requirements.txt

# Создание файла логов
touch Site/templates/log.txt

# Запуск
python CamCode/server.py
```

## 📋 Проверка размера

Перед загрузкой проверьте размер файлов:

```bash
# Проверка размера папки
du -sh .

# Проверка больших файлов
find . -type f -size +10M
```

## 🔧 Альтернативное решение

Если нужно сохранить OpenCV:

1. **Используйте Git LFS** (Large File Storage):
```bash
git lfs install
git lfs track "*.dll"
git lfs track "*.so"
git add .gitattributes
```

2. **Или загрузите OpenCV отдельно** на сервер после клонирования

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте размер репозитория: `du -sh .`
2. Проверьте `.gitignore` файл
3. Убедитесь, что большие файлы исключены
4. Проверьте права доступа к файлам

---

**🎉 Готово! Теперь ваш проект готов к загрузке в Git!**
