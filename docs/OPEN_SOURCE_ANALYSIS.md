# Methodist Agent — Open Source Analysis

> Анализ похожих open-source проектов: что заимствуем, что адаптируем, что отбрасываем.

## Критерии отбора

Мы ищем решения, которые:
1. Работают с агентами, планированием и approval gates.
2. Умеют интегрироваться с IDE/рабочим столом.
3. Имеют опыт работы с документами, RAG или мульти-агентной оркестрацией.
4. Подходят для Windows-first desktop-продукта (не только cloud/SaaS).

---

## 1. OpenCode / OpenAgentsControl / PAI-OpenCode

**Что это:** open-source AI coding assistant с архитектурой агентов, skills и контекста. OpenAgentsControl и PAI-OpenCode — надстройки с production-фокусом.

**Ключевые фичи:**
- **Skills** как Markdown-файлы с YAML-frontmatter (`name`, `triggers`, `agent`, инструкции).
- **ContextScout** — умный поиск релевантного контекста перед выполнением задачи.
- **Approval gates** — агент всегда запрашивает одобрение перед write/bash/delegate.
- **Editable agents** — поведение агентов описано в Markdown, можно править без кода.
- **MVI principle** — контекстные файлы <200 строк, lazy loading.
- **ExternalScout** — live-документация по внешним библиотекам.

**Что заимствуем:**
- ✅ Формат Skills (уже есть, но расширить: `examples`, `inputs`, `outputs`, `validation`).
- ✅ Approval gates с показом плана действий.
- ✅ Context discovery: подгружать только релевантные skills и шаблоны.
- ✅ Markdown-first конфигурация агентов (для методистов — не программистов).

**Что не заимствуем:**
- ❌ Coding-специфичные инструменты (bash-разрешения, diff-патчи, git-операции) — не наша аудитория.
- ❌ Контекст разработки ПО — методист работает с документами, не с кодом.

---

## 2. Continue.dev

**Что это:** open-source IDE-расширение (VS Code / JetBrains) для AI-ассистента программиста. Bring your own LLM.

**Ключевые фичи:**
- **Chat UI** боковой панели с историей.
- **Streaming** ответов.
- **Codebase context**: `@codebase`, `@file`, `@docs` — агент видит нужный контекст.
- **Indexing engine** — embeddings для семантического поиска по проекту.
- **Model switching** — лёгкое переключение между OpenAI, Anthropic, Ollama.

**Что заимствуем:**
- ✅ Streaming-ответы в chat (улучшает восприятие скорости).
- ✅ Контекстные ссылки: «работаю с файлом X, шаблоном Y».
- ✅ Индексация шаблонов и методичек для быстрого поиска.
- ✅ UI-паттерн «chat + план + результат».

**Что не заимствуем:**
- ❌ IDE-интеграция — мы не в редакторе кода, мы в Windows-трее.
- ❌ Autocomplete/ghost text — неприменимо к документам.

---

## 3. OpenHands (ex-OpenDevin)

**Что это:** автономный AI-агент для разработки ПО с sandbox-выполнением.

**Ключевые фичи:**
- **Docker sandbox** для безопасного выполнения команд.
- **Plan-Execute-Verify loop**.
- **Event-sourced state** — воспроизводимость и отказоустойчивость.
- **Tool calling** — shell, browser, editor.
- **Observability** — логи, трейсы, cost tracking.

**Что заимствуем:**
- ✅ Подход «план → одобрение → выполнение → проверка».
- ✅ Event sourcing для сессий и истории действий.
- ✅ Observability: токены, latency, стоимость, ошибки.
- ✅ Идея sandbox для опасных операций (в перспективе).

**Что не заимствуем:**
- ❌ Docker-зависимость — методист не разворачивает контейнеры.
- ❌ Git workflow, PR, коммиты — не наша предметная область.
- ❌ Автономность без контроля — нам нужен calm professional с approval gates.

---

## 4. Dify

**Что это:** open-source LLM application platform: visual workflow builder, RAG, agent runtime, observability.

**Ключевые фичи:**
- **Visual workflow orchestration** — drag-and-drop узлы LLM, условий, retrieval, human-in-the-loop.
- **RAG pipeline** — ingestion, chunking, embedding, vector search.
- **Prompt management UI** — версионирование, A/B-тесты.
- **Multi-model management** — 100+ провайдеров.
- **Observability** — traces, costs, latency, analytics.

**Что заимствуем:**
- ✅ Prompt versioning для system prompts и skills.
- ✅ RAG для методических материалов и шаблонов.
- ✅ Observability dashboard (lightweight).
- ✅ Workflow orchestration для сложных многошаговых сценариев.

**Что не заимствуем:**
- ❌ Visual builder — не вписывается в Windows Tray/CLI концепт.
- ❌ Cloud/SaaS-фокус — наш продукт desktop-first.
- ❌ Chatbot-only подход — нам нужна интеграция с Office.

---

## 5. AutoGen / CrewAI

**Что это:** фреймворки для мульти-агентных диалогов и ролевых агентов.

**Ключевые фичи:**
- **Role-based agents** — агенты с ролями и задачами.
- **Multi-agent conversations** — делегирование между агентами.
- **Tool calling** и workflow patterns.

**Что заимствуем:**
- ✅ Ролевые агенты: `document_specialist`, `web_researcher`, `fgos_expert`, `data_analyst`.
- ✅ Делегирование задач между специалистами.

**Что не заимствуем:**
- ❌ Сложные group chats — методисту нужен один понятный собеседник.
- ❌ Глубокая интеграция с кодом — неприменимо.

---

## Сводная таблица заимствований

| Фича | Источник | Как применим в Methodist Agent |
|------|----------|-------------------------------|
| Skills как Markdown + frontmatter | OpenCode | Уже есть, расширить метаданными |
| Approval gates | OpenCode, OpenHands | Показ плана перед записью файлов |
| Context discovery | OpenCode ContextScout | Поиск релевантных skills/шаблонов |
| Streaming в chat | Continue.dev | Потоковый вывод ответов LLM |
| Document indexing | Continue.dev, Dify | RAG по шаблонам и методичкам |
| Plan-Execute-Verify | OpenHands | План → одобрение → выполнение |
| Event-sourced sessions | OpenHands | Надёжная история действий |
| Observability | Dify, OpenHands | Токены, latency, ошибки |
| Prompt versioning | Dify | Версии system prompts и skills |
| Role-based agents | AutoGen / CrewAI | Чёткие роли специалистов |

---

## Рекомендации по приоритетам

### Ближайший план (недели 1–2)
1. Расширить формат Skills: `examples`, `inputs`, `outputs`, `validation`.
2. Улучшить approval gates: показывать diff файлов, кнопки в UI.
3. Добавить streaming в chat и Tray-уведомления.
4. Переписать тексты ошибок по `UX_GUIDE.md`.

### Средний план (недели 3–6)
5. Context discovery: релевантный поиск skills/шаблонов.
6. Индексация шаблонов и методичек (RAG light).
7. Prompt versioning и observability (token usage, latency).
8. Улучшенный onboarding и первичная настройка.

### Долгосрочный план
9. Windows Context Menu интеграция.
10. Встроенный chat-UI (tkinter/PyQt).
11. Plugin system для skills и агентов.
12. Sandbox для выполнения внешних команд (опционально).
