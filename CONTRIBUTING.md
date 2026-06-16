# Участие в Methodist Agent

Спасибо, что заглянул! Methodist Agent — open-source проект для автоматизации документной рутины методистов. PR приветствуются, но если планируешь большое изменение — сначала обсуди его в issue, чтобы не делать двойную работу.

---

## Быстрый старт для контрибьютора

1. Сделай форк репозитория.
2. Создай ветку с понятным именем:

   ```bash
   git checkout -b feature/short-description
   ```

3. Установи зависимости (рекомендуется [`uv`](https://docs.astral.sh/uv/)):

   ```bash
   uv sync                      # или: pip install -e ".[dev]"
   ```

4. Внеси изменения. Придерживайся минимального diff и KISS.
5. Запусти проверки:

   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run pytest
   ```

6. Убедись, что `.env`, ключи и токены не попали в индекс:

   ```bash
   git status
   ```

7. Обнови `README.md`, `INSTALL.md` и `CHANGELOG.md`, если менялась архитектура, конфигурация или команды.
8. Открой Pull Request с кратким описанием:
   - Что изменилось.
   - Зачем.
   - Как проверял.

---

## Стиль кода

- Python 3.11+, type hints, Google-style docstrings для публичных API.
- Максимальная длина строки: 100 символов (`ruff`).
- Импорты сортируются автоматически через `ruff`.
- Только конкретные `except SomeError`, никогда голый `except`.
- Новый агент-специалист живёт в `src/agents/`, новый навык — в `skills/`.
- LLM-вызовы идут через `src/core/model_router.py`, а не напрямую из агентов.

---

## Коммиты

Рекомендуется [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add XLSX gradebook generator
test: cover orchestrator routing
docs: update INSTALL with uv notes
fix: handle missing template path
```

---

## Definition of Done для PR

- `ruff check`, `ruff format --check` и `pytest` проходят без ошибок.
- Новая логика покрыта тестами или обоснованно исключена.
- Документация отражает изменения.
- Коммит-сообщения понятные.
- В PR нет секретов, API-ключей и личных конфигураций.

---

## Поведение

- Будь вежливым и конструктивным.
- Не коммить секреты, API-ключи и личные конфигурации.
