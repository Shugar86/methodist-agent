# Methodist Agent v2 — Design Specification

> Дата: 2026-06-15.  
> Статус: draft, awaiting approval.  
> Цель: превратить CLI/Tray-агента в минимальное рабочее пространство методиста с кнопками, абстракцией над Office, MCP-интеграцией и улучшенной системой навыков.

---

## 1. Goal

Создать Windows-first desktop-агента для методистов с:
- **tkinter workspace UI** — кнопки быстрых действий, чат, панель файлов, approval gates.
- **Document Environment** — единой абстракцией для работы с Office (COM → native → LibreOffice fallback).
- **MCP server** — экспозицией операций с документами через Model Context Protocol.
- **Skills v2** — стандартизированными Markdown-навыками с frontmatter.
- **ContextScout** — умным поиском релевантного контекста перед планированием.
- **Streaming** — потоковым выводом LLM-ответов в чат.

Интерфейс остаётся минимальным и не перегруженным: CLI остаётся для отладки, System Tray — точкой входа, встроенный чат — основным интерфейсом.

---

## 2. Current Context

Проект уже содержит:
- `src/main.py` — Typer CLI с командами `init`, `create`, `adapt`, `search`, `pdf`, `chat`, `tray`.
- `src/core/orchestrator.py` — правиловый планировщик + LLM refinement.
- `src/core/context_manager.py` — SQLite-сессии, базовая загрузка skills, ContextScout-заглушка.
- `src/core/model_router.py` — OpenAI/Anthropic/Ollama клиент, без streaming.
- `src/agents/document_specialist.py` — COM/native fallback для DOCX/XLSX/PPTX.
- `src/windows/tray_app.py` — System Tray на pystray + tkinter диалоги.
- `src/core/ui_text.py` — центральный реестр строк.

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  tkinter Workspace UI                                       │
│  (chat, quick actions, file panel, approval buttons)        │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│ Orchestrator │ │ ContextScout│ │  EventBus    │
└──────┬───────┘ └──────┬──────┘ └──────┬───────┘
       │                │               │
       └────────────────┼───────────────┘
                        ▼
            ┌─────────────────────┐
            │  DocumentRequest    │
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │ DocumentEnvironment │
            │  (COM → Native →    │
            │   LibreOffice)      │
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │  MCP Server (stdio) │
            │  tools/resources/   │
            │  prompts            │
            └─────────────────────┘
```

---

## 4. UI Design

### 4.1 tkinter Workspace

Окно `MethodistWorkspace` (стартовый размер 900×700, resizable).

Layout:
- **Левая боковая панель (200 px):**
  - Раздел «Быстрые действия» с кнопками:
    - Рабочая программа
    - Ведомость
    - Презентация
    - Отчёт
    - Адаптировать документ
  - Раздел «Сессии» — список недавних чатов.
- **Центральная область:**
  - Чат-история (scrollable).
  - План действий с approval-кнопками (Подтвердить / Отменить).
  - Поле ввода + кнопка «Отправить».
  - Индикатор streaming (точки / «печатает…»).
- **Правая боковая панель (250 px):**
  - Дерево файлов `~/Documents/Методист-Агент`.
  - Превью последнего документа: имя, путь, тип, статус.

### 4.2 Вход из System Tray

Левый клик по иконке в трее открывает/поднимает workspace окно.
Правый клик — прежнее меню + пункт «Открыть рабочее пространство».

### 4.3 Vibe

- calm professional.
- Нейтральные статусы, без восклицаний.
- Эмодзи по `UX_GUIDE.md`.
- Нет splash screen, нет onboarding wizard при каждом запуске.

---

## 5. Document Environment

### 5.1 Responsibilities

- Открывать, создавать, редактировать, сохранять, экспортировать документы.
- Выбирать драйвер по приоритету: COM → Native → LibreOffice.
- Поддерживать hooks и event bus.
- Работать в песочнице: `~/Documents/Методист-Агент`.
- Делать backup-копию перед редактированием.

### 5.2 Components

- `DocumentEnvironment` — facade, принимает `DocumentRequest`, маршрутизирует на драйвер.
- `DocumentRequest` — dataclass: `action`, `doc_type`, `input_path`, `output_path`, `parameters`, `options`.
- `DocumentResult` — dataclass: `success`, `output_path`, `message`, `metadata`, `events`.
- `BaseDocumentDriver` — интерфейс драйвера.
- `COMDriver` — `pywin32`, `DispatchEx`, headless.
- `NativeDriver` — `python-docx`, `openpyxl`, `python-pptx`.
- `LibreOfficeDriver` — `soffice --headless` (опционально).

### 5.3 Driver Priority

1. Если Windows + Office доступен → `COMDriver`.
2. Иначе если задача поддерживается native → `NativeDriver`.
3. Иначе если установлен LibreOffice → `LibreOfficeDriver`.
4. Иначе — понятная ошибка с предложением установить Office или LibreOffice.

### 5.4 Hooks

Хуки вызываются через `EventBus`:
- `before_open`
- `after_open`
- `before_save`
- `after_save`
- `before_export`
- `after_export`
- `on_format_conflict`
- `on_error`

Подписчики:
- UI обновляет статус документа.
- Logger пишет в SQLite.
- Sandbox делает backup перед `before_save`.

### 5.5 Sandbox

- Все операции по умолчанию в `~/Documents/Методист-Агент`.
- Пути нормализуются, запрещены `..` и symlink за пределами песочницы.
- Перед редактированием существующего файла создаётся `.backup/{timestamp}/{filename}`.
- Rollback: восстановление из последнего backup.

---

## 6. MCP Server

### 6.1 Purpose

Экспонировать операции Methodist Agent как MCP server, чтобы:
- Внешние MCP host'ы (Claude Desktop, Cursor, и т.д.) могли работать с документами.
- Сам агент мог вызывать внешние MCP servers (filesystem, document-loader).

### 6.2 Implementation

- Файл: `src/mcp_server/methodist_mcp_server.py`.
- Библиотека: `mcp[cli]` (FastMCP).
- Transport: stdio по умолчанию; streamable-http под флагом.

### 6.3 Tools

| Tool | Описание |
|------|----------|
| `list_documents` | Список документов в проектной папке |
| `read_document` | Извлечь текст/метаданные из DOCX/XLSX/PPTX/PDF |
| `create_document` | Создать документ из шаблона и параметров |
| `edit_document` | Применить набор операций к документу |
| `adapt_document` | Адаптировать документ под новый шаблон/ФГОС |
| `convert_to_pdf` | Конвертировать документ в PDF |

### 6.4 Resources

- `doc://{relative_path}` — read-only доступ к документу.

### 6.5 Prompts

- `generate_curriculum` — шаблон для генерации рабочей программы.
- `adapt_to_fgos` — шаблон для адаптации под ФГОС.

### 6.6 Security

- Allowlist директорий через MCP Roots.
- Подтверждение destructive операций (write/delete) перед выполнением.
- API keys — в OS keyring, не в коде.

---

## 7. Skills v2

### 7.1 Format

```
skills/
├── curriculum/
│   └── create-rpd/
│       ├── SKILL.md
│       ├── references/
│       │   └── fgos-3-plus-plus.md
│       └── scripts/
│           └── validate.py
```

`SKILL.md`:
```markdown
---
name: create-rpd
description: Создаёт рабочую программу дисциплины.
triggers:
  - рабочая программа
  - РПД
  - учебная программа
examples:
  - input: "Создай рабочую программу по Базам данных, 144 часа"
    output: "docx-файл рабочей программы"
allowed-tools:
  - create_document
  - search_web
metadata:
  author: methodist-agent
  version: "2.0"
---

# Создание рабочей программы

1. Запроси дисциплину и часы, если не указаны.
2. Найди актуальный шаблон в templates/curriculum/.
3. ...
```

### 7.2 Registry & Loader

- `SkillRegistry` сканирует `skills/` при старте.
- В каталоге хранятся только `name`, `description`, `triggers`.
- Полная загрузка `SKILL.md` происходит при активации.
- `SkillValidator` проверяет `name`, `description`, уникальность, существование references/scripts.

### 7.3 Activation

- Автоматическая активация по `triggers` из запроса пользователя.
- Ручная активация через UI/CLI.
- Активированные skills добавляются в system prompt.

---

## 8. ContextScout

### 8.1 Purpose

Находить релевантный контекст перед планированием и перед LLM-вызовом, чтобы не грузить все skills и шаблоны в prompt.

### 8.2 Sources

1. **Skills catalog** — `triggers` и `description`.
2. **Project context files** — `.methodist/context/*.md`.
3. **Templates index** — имена и описания шаблонов.
4. **Session summary** — последние N сообщений + summary.

### 8.3 Ranking

| Сигнал | Вес |
|--------|-----|
| Точное совпадение trigger | 10 |
| Ключевое слово в description | 5 |
| Ключевое слово в project context | 4 |
| Категория skill | 2 |
| Description similarity | 1 |

Возвращаются top-K элементов (K=5 по умолчанию).

### 8.4 MVI

- Файлы контекста < 200 строк.
- Ленивая загрузка больших reference-файлов.
- Local-first: project context override global.

---

## 9. Streaming

### 9.1 Model Router

- `ModelRouter.chat(..., stream=True)` возвращает async iterator.
- Поддержка OpenAI, Anthropic, Ollama.
- Если streaming не поддерживается провайдером — fallback на обычный ответ.

### 9.2 UI

- `ChatPanel` слушает `asyncio.Queue`.
- Токены дописываются в текущее сообщение ассистента.
- Кнопка «Стоп» прерывает генерацию через `asyncio.Event`.
- После завершения потока сообщение сохраняется в SQLite.

### 9.3 Error Handling

- Ошибки mid-stream отображаются как сообщение об ошибке.
- Частичный ответ сохраняется, если он не пустой.

---

## 10. Data Flow

1. Пользователь взаимодействует с tkinter workspace (кнопка или чат).
2. UI передаёт запрос в `Orchestrator`.
3. `ContextScout` находит релевантные skills и шаблоны.
4. `Orchestrator` формирует `ExecutionPlan`.
5. UI показывает план и кнопки Подтвердить/Отменить.
6. После approval `Orchestrator` выполняет задачи через `DocumentEnvironment` и агентов.
7. `DocumentEnvironment` публикует события в `EventBus`.
8. UI обновляет статус, отображает результат.
9. LLM-ответы streaming'ом выводятся в чат.
10. `MCP Server` доступен параллельно для внешних интеграций.

---

## 11. Error Handling & Security

### 11.1 Errors

- Все ошибки пользователю через `ui_text.py`.
- Traceback только в лог.
- Fallback-цепочка для документов: COM → native → LibreOffice → ошибка с подсказкой.

### 11.2 Security

- Песочница: только `~/Documents/Методист-Агент` и явно разрешённые пути.
- Approval gates для write/delete/network.
- OS keyring для API keys.
- MCP tools помечаются `readOnlyHint` / `destructiveHint`.

---

## 12. Testing

- Unit tests:
  - `DocumentEnvironment` driver selection and fallback.
  - `COMDriver` / `NativeDriver` with mocked Office/libs.
  - `SkillRegistry` loading and validation.
  - `ContextScout` ranking.
  - Streaming queue behavior.
- Integration tests:
  - MCP server stdio client round-trip.
  - UI smoke test (окно открывается, кнопки существуют).
- Manual checks:
  - Создание документа через UI.
  - Approval gate flow.
  - COM fallback to native.

---

## 13. Implementation Waves

### Wave 1: tkinter Workspace UI
- `src/windows/workspace.py` — основное окно.
- Интеграция с `tray_app.py`.
- Chat panel с историей и вводом.
- Quick actions panel.
- File panel (простое дерево).
- Approval gate UI.

### Wave 2: Document Environment + MCP Server
- `src/core/document_environment.py` и драйверы.
- `src/core/event_bus.py`.
- `src/mcp_server/methodist_mcp_server.py`.
- Hooks и sandbox.
- UI отображает статус документов.

### Wave 3: Skills v2 + ContextScout + Streaming
- Рефакторинг skills под формат v2.
- `SkillRegistry`, `SkillValidator`.
- `ContextScout` implementation.
- Streaming в `ModelRouter` и UI.

---

## 14. Open Questions

1. Нужен ли LibreOffice driver в MVP или ограничиться COM + native?
2. Нужна ли индексация шаблонов через embeddings или достаточно keyword matching?
3. Нужен ли встроенный просмотрщик содержимого DOCX/PDF в UI или достаточно имени/пути/статуса?
