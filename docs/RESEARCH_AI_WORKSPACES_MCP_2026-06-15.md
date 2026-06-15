# Methodist Agent — Research: AI Workspaces, Office Automation, MCP, Skills v2

> Исследование open-source проектов и концепций по запросу: Kimi Work / Claude Cowork analogs, прямая работа с Office, среда документов, хуки, MCP, Skills v2, ContextScout, streaming.
> Дата: 2026-06-15.

---

## 1. AI Workspace / Desktop Agent аналоги

| Проект | Стек | Ключевые фичи | Чем полезно для нас |
|--------|------|---------------|---------------------|
| [AionUi](https://github.com/iOfficeAI/AionUi) | Electron + React + Rust backend | 21 ассистента, Office skill'ы, превью документов, multi-agent mode, MCP, cron | Office-ассистенты, превью файлов, параллельные агенты |
| [QwenPaw](https://github.com/agentscope-ai/QwenPaw) | Python + Tauri desktop beta | Skills, plugin market, tool/file guard, proactive memory, MCP | Security guardrails, proactive memory, plugin market |
| [Eigent](https://github.com/eigent-ai/eigent) | Electron + Python/FastAPI + CAMEL-AI | Multi-agent workforce, MCP tools, human-in-the-loop, HTML/PPT reports | Document worker, approval UX, parallel decomposition |
| [DeepChat](https://github.com/ThinkInAIXYZ/deepchat) | Electron + Vue | Multi-model chat, MCP, skills import/export, ACP, Office skills | MCP-first архитектура, мульти-сессии, импорт скиллов |
| [LobsterAI](https://github.com/netease-youdao/LobsterAI) | Electron + React + OpenClaw | 29 skills, bundled Python runtime, memory files, cron, IM remote | Windows Python bundle, memory files, permission gates |
| [Open Cowork](https://github.com/OpenCoworkAI/open-cowork) | Electron + React | VM sandbox (WSL2/Lima), MCP connectors, GUI automation | Sandbox model, trace panel, one-click installer |
| [Kuse Cowork](https://github.com/kuse-ai/kuse_cowork) | Rust + Tauri + SolidJS | ~10 MB, Docker sandbox, default Office skills | Лёгкий инсталлятор, Docker изоляция |

**Вывод:** все проекты делают ставку на **skills**, **MCP**, **in-app preview**, **permission gates**, **cron**. Methodist Agent отличается фокусом на Windows + Office + методиста; COM-интеграция остаётся нашей сильной стороной.

---

## 2. Автоматизация Office и документов

| Библиотека/проект | Назначение | Применение в Methodist Agent |
|-------------------|------------|------------------------------|
| `pywin32` / `win32com` | Полный COM-доступ к Word/Excel/PPT | Основной Windows-движок; `DispatchEx` для изоляции, `Visible=False`, чистка ссылок |
| `python-docx` / `openpyxl` / `python-pptx` | OOXML без Office | Native fallback для Linux/без Office; простые docx/xlsx/pptx |
| `xlwings` | Удобный API поверх COM для Excel | Интерактивная работа с Excel, DataFrame ↔ листы |
| `docx2pdf` | DOCX → PDF через Word | Финализация документов с точным рендерингом |
| `office_oxide` | Rust + Python, чтение/конвертация Office и legacy форматов | Быстрый native fallback для чтения старых `.doc`/`.xls` |
| `TagUI` | RPA с плагинами для Word/Excel | UI-автоматизация legacy-сценариев |
| `OpenRPA` | Windows-first RPA платформа | Если вырастаем до enterprise RPA |

**Ключевые best practices для COM:**
- `DispatchEx` вместо `Dispatch` для фоновой работы.
- `Visible=False`, `DisplayAlerts=False`.
- Явно закрывать документы и `Quit()`, удалять ссылки.
- `pythoncom.CoInitialize()` / `CoUninitialize()` в потоках.

---

## 3. MCP (Model Context Protocol)

**Что это:** открытый стандарт Anthropic/Agentic AI Foundation для подключения AI-приложений к инструментам и данным (JSON-RPC 2.0).

**Примитивы:** Tools, Resources, Prompts, Sampling, Roots.
**Транспорты:** stdio (для desktop), SSE/Streamable HTTP (для сети).

**Полезные MCP-сервера:**
- `@modelcontextprotocol/server-filesystem` — безопасный доступ к файлам.
- `awslabs.document-loader-mcp-server` — чтение PDF/DOCX/XLSX/PPTX.
- `mcp-ms-office-documents` — создание PPTX/DOCX/XLSX из Markdown.
- `pptx-xlsx-mcp` — COM-автоматизация Office.
- `mcp-libre` — LibreOffice headless.

**Рекомендация для Methodist Agent:**
1. Добавить `mcp[cli]` в зависимости.
2. Создать `methodist_mcp_server.py` с 3–5 инструментами: `list_documents`, `read_document`, `create_document_from_template`, `convert_to_pdf`, `review_document`.
3. Использовать stdio transport для desktop.
4. Добавить MCP client wrapper для вызова внешних серверов (filesystem, document loader).

---

## 4. Skills v2, ContextScout, Streaming

### Skills v2 / Agent Skills
- Стандарт `SKILL.md` с YAML frontmatter + Markdown body.
- Progressive disclosure: catalog → instructions → resources.
- Поля: `name`, `description`, `triggers`, `allowed-tools`, `metadata`.
- Уже есть в проекте базовый парсер frontmatter; нужно довести до стандарта.

### ContextScout / Context Discovery
- Поиск релевантного контекста перед ответом агента.
- Механизмы: keyword triggers, description matching, project-local context files.
- Принцип MVI (Minimal Viable Information): файлы < 200 строк, lazy loading.

### Streaming
- Потоковая выдача токенов LLM для снижения воспринимаемой задержки.
- Реализация: `stream=True` в OpenAI/Anthropic, SSE/WebSocket, queue в UI.
- UI: один assistant bubble, индикатор, Stop, сохранение в БД после завершения потока.

---

## 5. Перекрёстные рекомендации

1. **Document Environment** — центральная абстракция над COM/native. Приоритет COM → native → LibreOffice → ошибка с подсказкой.
2. **Hooks / Event Bus** — file watcher, `before_save`, `after_open`, `on_template_update`, cron.
3. **MCP Server** — экспозиция операций с документами как tools/resources/prompts.
4. **Skills v2** — привести `SKILL.md` к стандарту, добавить `allowed-tools`, `examples`, `validation`.
5. **ContextScout** — релевантный поиск skills/шаблонов перед планированием.
6. **Streaming** — перейти на потоковый вывод в chat.
7. **Security** — allowlist директорий, approval gates, destructive hints, OS keyring для секретов.

---

## 6. Ссылки

- AionUi: https://github.com/iOfficeAI/AionUi
- QwenPaw: https://github.com/agentscope-ai/QwenPaw
- Eigent: https://github.com/eigent-ai/eigent
- DeepChat: https://github.com/ThinkInAIXYZ/deepchat
- LobsterAI: https://github.com/netease-youdao/LobsterAI
- Open Cowork: https://github.com/OpenCoworkAI/open-cowork
- Kuse Cowork: https://github.com/kuse-ai/kuse_cowork
- pywin32: https://github.com/mhammond/pywin32
- python-docx: https://github.com/python-openxml/python-docx
- openpyxl: https://foss.heptapod.net/openpyxl/openpyxl
- python-pptx: https://github.com/scanny/python-pptx
- office_oxide: https://github.com/yfedoseev/office_oxide
- MCP docs: https://modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Agent Skills: https://docingest.com/docs/agentskills.io
- Claude Code Skills: https://code.claude.com/docs/en/skills
