# Инструкция по установке Methodist Agent

## Системные требования

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.11 или выше
- **Microsoft Office**: 2019/2021/365 (опционально, для COM-режима)
- **RAM**: 4 GB минимум, 8 GB рекомендуется

## Быстрая установка

### Шаг 1: Установка Python

1. Скачайте Python 3.11+ с [python.org](https://python.org)
2. При установке отметьте **"Add Python to PATH"**
3. Проверьте установку:
   ```cmd
   python --version
   ```

### Шаг 2: Создание виртуального окружения

```cmd
cd methodist-agent
python -m venv venv
venv\Scripts\activate
```

### Шаг 3: Установка зависимостей

```cmd
pip install -r requirements.txt
```

### Шаг 4: Установка Tesseract OCR (опционально)

Для работы с сканированными PDF:

1. Скачайте установщик с [GitHub tesseract-ocr](https://github.com/UB-Mannheim/tesseract/wiki)
2. Установите в `C:\Program Files\Tesseract-OCR`
3. Добавьте в PATH или установите переменную окружения:
   ```cmd
   setx TESSDATA_PREFIX "C:\Program Files\Tesseract-OCR\tessdata"
   ```

### Шаг 5: Установка Poppler (опционально)

Для конвертации PDF в изображения:

1. Скачайте [poppler для Windows](https://github.com/oschwartz10612/poppler-windows/releases)
2. Распакуйте и добавьте `bin` папку в PATH

### Шаг 6: Инициализация агента

```cmd
python -m src.main init
```

Это создаст:
- `~/.methodist-agent/config.yaml` — конфигурация
- `~/.methodist-agent/templates/` — шаблоны документов
- `~/.methodist-agent/skills/` — skills репозиторий
- `~/.methodist-agent/output/` — выходные файлы

### Шаг 7: Настройка API ключей

Откройте `~/.methodist-agent\config.yaml` и добавьте API ключи:

```yaml
models:
  primary:
    provider: "openai"
    model: "gpt-4o"
    api_key: "sk-your-openai-key-here"
  fallback:
    provider: "anthropic"
    model: "claude-3-5-sonnet"
    api_key: "sk-ant-your-anthropic-key-here"
```

Или используйте переменные окружения:
```cmd
setx OPENAI_API_KEY "sk-your-key"
setx ANTHROPIC_API_KEY "sk-ant-your-key"
```

### Шаг 8: Установка в систему (опционально)

```cmd
pip install -e .
```

Теперь агент доступен как команда:
```cmd
methodist-agent --help
```

## Первый запуск

### Интерактивный режим

```cmd
python -m src.main chat
```

### System Tray

```cmd
python -m src.main tray
```

### Создание документа

```cmd
python -m src.main create curriculum --subject "Matematika" --hours 144
```

## Устранение неполадок

### Ошибка: "No module named 'win32com'"

```cmd
pip install pywin32
```

### Ошибка: "Tesseract not found"

Убедитесь, что Tesseract установлен и добавлен в PATH. Или отключите OCR в config:
```yaml
windows:
  ocr_enabled: false
```

### Ошибка: "Office not found"

Агент автоматически переключится на native-режим (python-docx/openpyxl). Для COM-режима установите Microsoft Office.

### Ошибка API ключей

Если нет API ключей, настройте локальную модель через Ollama:
```yaml
models:
  primary:
    provider: "ollama"
    model: "llama3.1"
    api_base: "http://localhost:11434"
```

## Обновление

```cmd
git pull
pip install -r requirements.txt --upgrade
```

## Удаление

```cmd
pip uninstall methodist-agent
rmdir /s %USERPROFILE%\.methodist-agent
```

---

*Установка v1.0.0 | Windows-first AI Agent for Education*
