# Methodist Agent

> Спокойный и компетентный помощник, который берёт на себя документную рутину методиста — прямо в его рабочем окружении.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](./pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![LLM: Claude · OpenAI](https://img.shields.io/badge/LLM-Claude%20·%20OpenAI-D97757?logo=anthropic)](#конфигурация)
[![Windows](https://img.shields.io/badge/Windows-integration-0078D6?logo=windows)](#возможности)

## Что это

**Methodist Agent** — Windows-first AI-агент для методистов учебных заведений. Он создаёт и переделывает рабочие программы, ведомости, презентации и отчёты, ищет нормативные материалы и автоматизирует Office прямо на рабочем месте — через системный трей, контекстное меню и COM-интеграцию.

Идея проста: методист тратит часы на однотипную возню с документами по меняющимся шаблонам. Агент берёт эту рутину на себя, оставляя человеку решение и контроль. Архитектура вдохновлена [OpenCode](https://github.com/opencode-ai/opencode), но реализована на Python с фокусом на Windows и работу с документами.

### Для кого

- **Методисты вузов и ссузов** — рабочие программы, ведомости, отчёты по ФГОС без ручной возни с шаблонами.
- **Учебные отделы** — массовая адаптация документов под новые требования.
- **Преподаватели** — быстрая сборка презентаций и методических материалов.

### Вайб

`calm professional` — спокойный профессионал. Никакой суеты и «вау-ИИ»: агент говорит по делу, всегда показывает, что собирается сделать, и ждёт подтверждения на необратимых действиях. Подробнее — [`docs/UX_GUIDE.md`](./docs/UX_GUIDE.md).

## Возможности

- 📄 **DOCX** — создание и редактирование Word (учебные программы, отчёты, планы).
- 📊 **XLSX** — ведомости, расписания, статистика.
- 🎯 **PPTX** — презентации и методические материалы.
- 📑 **PDF** — чтение, извлечение текста/таблиц, OCR, конвертация.
- 🔍 **Web Search** — поиск методических и нормативных документов.
- 🔄 **Адаптация** — переделка готовых документов под новые требования.
- 🪟 **Windows Integration** — System Tray, контекстное меню, COM-автоматизация Office.

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  System Tray│     │     CLI     │     │Context Menu │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
              ┌─────────────────────┐
              │     Core Engine     │
              │    (Orchestrator)   │
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Document   │ │  Web Search  │ │     PDF      │
│  Specialist  │ │    Agent     │ │    Reader    │
└──────────────┘ └──────────────┘ └──────────────┘
```

Подробности проектных решений — в [`docs/DESIGN.md`](./docs/DESIGN.md).

## Быстрый старт

> Требуется **Python 3.11+**. Рекомендуется пакетный менеджер [`uv`](https://docs.astral.sh/uv/); подойдёт и обычный `pip`.

```bash
# 1. Клонировать репозиторий
git clone git@github.com:Shugar86/methodist-agent.git
cd methodist-agent

# 2. Установить зависимости
uv sync                      # или: pip install -r requirements.txt

# 3. Указать ключ LLM-провайдера
cp .env.example .env
# Откройте .env и впишите ANTHROPIC_API_KEY (Claude — primary по умолчанию)

# 4. Инициализировать агента
uv run python -m src.main init
```

## Использование

```bash
# Интерактивный режим
uv run python -m src.main chat

# Создать рабочую программу
uv run python -m src.main create curriculum --subject "Математика" --hours 144

# Поиск методички
uv run python -m src.main search "рабочая программа математика ФГОС"

# Адаптировать документ под новый шаблон
uv run python -m src.main adapt "old.docx" --template "new_template.docx"

# Извлечь содержимое PDF
uv run python -m src.main pdf extract "document.pdf" --output "document.docx"

# Свернуть в системный трей (Windows)
uv run python -m src.main tray
```

> Без `uv` те же команды запускаются как `python -m src.main <команда>` внутри активированного виртуального окружения.

## Структура проекта

```
methodist-agent/
├── src/
│   ├── core/                  # Core Engine
│   │   ├── config.py          # Конфигурация и дефолты провайдеров
│   │   ├── model_router.py    # Маршрутизация LLM-запросов
│   │   ├── context_manager.py # Контекст и skills
│   │   └── orchestrator.py    # Диспетчер задач
│   ├── agents/                # Специализированные агенты
│   │   ├── document_specialist.py
│   │   ├── web_search.py
│   │   ├── pdf_reader.py
│   │   └── adaptation_agent.py
│   ├── windows/               # Windows-интеграция (tray)
│   └── main.py                # CLI-вход
├── skills/                    # Репозиторий навыков (docx/xlsx/pptx-creation)
├── templates/                 # Шаблоны документов
├── docs/                      # DESIGN, UX_GUIDE, API
├── pyproject.toml             # Зависимости и метаданные пакета
└── .env.example               # Шаблон переменных окружения
```

## Конфигурация

Ключи провайдеров берутся из `.env`, остальное — из `~/.methodist-agent/config.yaml`:

```yaml
agent:
  name: "methodist-agent"
  language: "ru"

models:
  # По умолчанию (src/core/config.py): primary — Anthropic (Claude), fallback — OpenAI.
  primary:
    provider: "anthropic"
    model: "claude-opus-4-8"
    api_key: "${ANTHROPIC_API_KEY}"
  fallback:
    provider: "openai"
    model: "gpt-4o"
    api_key: "${OPENAI_API_KEY}"

windows:
  tray_icon: true
  context_menu: true
  com_automation: true

documents:
  preferred_mode: "com"        # com или native
  output_path: "~/Documents/Методист-Агент"
```

## 📍 С чего начать чтение

Чтобы разобраться в проекте за ~15 минут, читай в таком порядке:

1. **`src/main.py`** — CLI: все команды (`chat`, `create`, `search`, `adapt`, `pdf`) и точка входа.
2. **`src/core/orchestrator.py`** — диспетчер: как запрос превращается в вызовы агентов; рядом `model_router.py` — выбор LLM-провайдера.
3. **`src/agents/`** — специализированные агенты: `document_specialist`, `web_search`, `pdf_reader`, `adaptation_agent`.

## Документация

- [`INSTALL.md`](./INSTALL.md) — подробная установка и настройка.
- [`docs/DESIGN.md`](./docs/DESIGN.md) — архитектура и проектные решения.
- [`docs/UX_GUIDE.md`](./docs/UX_GUIDE.md) — продуктовый вайб, тон и правила интерфейса.

## Лицензия

[MIT](./LICENSE) © 2026 Shugar86
