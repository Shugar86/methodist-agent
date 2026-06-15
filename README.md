# Methodist Agent

🤖 **Windows-first AI агент для помощи методистам учебных заведений**

Агент, вдохновлённый архитектурой [OpenCode](https://github.com/opencode-ai/opencode), но реализованный на Python с фокусом на Windows-интеграцию и работу с документами.

## Возможности

- 📄 **DOCX** — создание и редактирование Word-документов (учебные программы, отчёты, планы)
- 📊 **XLSX** — работа с Excel (ведомости, расписания, статистика)
- 🎯 **PPTX** — создание презентаций и методических материалов
- 📑 **PDF** — чтение, извлечение текста/таблиц, OCR, конвертация
- 🔍 **Web Search** — поиск методических материалов и нормативных документов
- 🔄 **Адаптация** — переделка существующих документов под новые требования
- 🪟 **Windows Integration** — System Tray, Context Menu, COM-автоматизация Office

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  System Tray│     │    CLI      │     │Context Menu │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
              ┌─────────────────────┐
              │    Core Engine      │
              │  (Orchestrator)     │
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Document   │ │   Web Search │ │    PDF       │
│  Specialist  │ │    Agent     │ │   Reader     │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Установка

```bash
# Клонировать репозиторий
git clone <repo-url>
cd methodist-agent

# Установить зависимости
pip install -r requirements.txt

# Инициализировать агента
python -m src.main init
```

## Использование

### Интерактивный режим
```bash
python -m src.main chat
```

### Однократные команды
```bash
# Создать рабочую программу
python -m src.main create curriculum --subject "Математика" --hours 144

# Поиск методички
python -m src.main search "рабочая программа математика ФГОС"

# Адаптировать документ
python -m src.main adapt "old.docx" --template "new_template.docx"

# Работа с PDF
python -m src.main pdf extract "document.pdf" --output "document.docx"
```

### System Tray
```bash
python -m src.main tray
```

## Структура проекта

```
methodist-agent/
├── src/
│   ├── core/              # Core Engine
│   │   ├── config.py      # Конфигурация
│   │   ├── model_router.py# LLM routing
│   │   ├── context_manager.py # Context & Skills
│   │   └── orchestrator.py    # Диспетчер
│   ├── agents/            # Specialist Agents
│   │   ├── document_specialist.py
│   │   ├── web_search.py
│   │   ├── pdf_reader.py
│   │   └── adaptation_agent.py
│   ├── windows/           # Windows Integration
│   │   └── tray_app.py
│   └── main.py            # CLI
├── skills/                # Skills Repository
│   ├── docx-creation/
│   ├── xlsx-creation/
│   ├── pptx-creation/
│   └── ...
├── templates/             # Document Templates
└── requirements.txt
```

## Конфигурация

Конфигурация хранится в `~/.methodist-agent/config.yaml`:

```yaml
agent:
  name: "methodist-agent"
  language: "ru"

models:
  primary:
    provider: "openai"
    model: "gpt-4o"
    api_key: "${OPENAI_API_KEY}"

windows:
  tray_icon: true
  context_menu: true
  com_automation: true

documents:
  preferred_mode: "com"  # com или native
  output_path: "~/Documents/Методист-Агент"
```

## Лицензия

MIT
