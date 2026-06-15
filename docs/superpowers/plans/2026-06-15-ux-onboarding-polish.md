# UX/UI Polish & Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace technical and generic user-facing messages in Methodist Agent with calm-professional, human-friendly texts, and add a first-run onboarding + environment check.

**Architecture:** Centralize all user-facing Russian strings in `src/core/ui_text.py`, then refactor CLI, agents, and Tray to call this registry. Add `src/core/environment_check.py` to detect Office, Tesseract, and API keys with friendly reporting. Wire onboarding into `init` and `chat`.

**Tech Stack:** Python 3.11+, Typer, Rich, tkinter, pytest.

---

## File Map

| File | Responsibility |
|------|----------------|
| `src/core/ui_text.py` | Central registry of user-facing strings (success, progress, error, empty, onboarding). |
| `src/core/environment_check.py` | Detect Office COM, Tesseract OCR, API keys and return structured report. |
| `src/main.py` | CLI entry point; uses `ui_text` and runs onboarding/environment check. |
| `src/agents/document_specialist.py` | Uses `ui_text` for document creation/editing messages. |
| `src/agents/adaptation_agent.py` | Uses `ui_text` for adaptation messages. |
| `src/windows/tray_app.py` | Uses `ui_text` for notifications and dialogs. |
| `tests/test_ui_text.py` | Unit tests for `ui_text`. |
| `tests/test_environment_check.py` | Unit tests for `environment_check`. |
| `docs/UX_GUIDE.md` | Update with concrete examples. |
| `docs/DESIGN.md` | Update onboarding flow. |

---

## Task 1: Create `src/core/ui_text.py` message registry

**Files:**
- Create: `src/core/ui_text.py`
- Test: `tests/test_ui_text.py`

- [ ] **Step 1: Write the registry**

Create `src/core/ui_text.py`:

```python
"""Central registry of user-facing strings for Methodist Agent.

All Russian/English texts shown to users live here so we can keep the
calm-professional vibe consistent across CLI, Tray, and Chat.
"""

from pathlib import Path
from typing import Optional


# ------------------------------------------------------------------
# Progress
# ------------------------------------------------------------------

def progress_creating_document(template: str) -> str:
    return f"Создаю документ из шаблона: {template}"


def progress_adapting_document(path: str) -> str:
    return f"Адаптирую документ: {Path(path).name}"


def progress_searching(query: str) -> str:
    return f"🔍 Ищу методические материалы: {query}"


def progress_pdf(action: str, path: str) -> str:
    return f"📄 Обрабатываю PDF ({action}): {Path(path).name}"


# ------------------------------------------------------------------
# Success
# ------------------------------------------------------------------

def success_document_created(path: str) -> str:
    return f"✅ Документ готов: {Path(path).name}"


def success_document_adapted(path: str) -> str:
    return f"✅ Документ адаптирован и сохранён: {Path(path).name}"


def success_search_results(count: int) -> str:
    return f"✅ Найдено материалов: {count}"


def success_pdf_ready(path: str) -> str:
    return f"✅ PDF обработан: {Path(path).name}"


# ------------------------------------------------------------------
# Errors
# ------------------------------------------------------------------

def error_template_not_found(path: Path) -> str:
    return (
        f"❌ Шаблон не найден: {path}\n"
        "Проверьте, что инициализация выполнена (methodist-agent init), "
        "или укажите путь к своему шаблону."
    )


def error_template_folder_empty(path: Path) -> str:
    return (
        f"❌ В папке шаблона не найден файл template.*: {path}\n"
        "Убедитесь, что в папке есть template.docx, template.xlsx или template.pptx."
    )


def error_unsupported_format(fmt: str) -> str:
    return (
        f"❌ Неподдерживаемый формат: {fmt}\n"
        "Поддерживаются: docx, xlsx, pptx."
    )


def error_no_office_fallback() -> str:
    return (
        "⚠️ Microsoft Office не найден. "
        "Переключаюсь на встроенный режим — документ всё равно будет готов."
    )


def error_api_key_missing(provider: str = "языковой модели") -> str:
    return (
        f"❌ Не удалось подключиться к {provider}.\n"
        "Проверьте API-ключ в настройках (~/.methodist-agent/config.yaml) "
        "или выберите локальную модель Ollama."
    )


def error_file_not_found(path: str) -> str:
    return f"❌ Файл не найден: {path}. Проверьте путь и попробуйте снова."


def error_write_failed(path: str, reason: Optional[str] = None) -> str:
    msg = f"❌ Не удалось сохранить файл: {path}."
    if reason:
        msg += f" Причина: {reason}"
    return msg + " Проверьте права на запись в папку."


def error_generic(action: str, reason: str) -> str:
    return f"❌ Не удалось {action}. {reason}"


# ------------------------------------------------------------------
# Empty / Info
# ------------------------------------------------------------------

def info_no_sessions() -> str:
    return (
        "Пока нет сохранённых диалогов. "
        'Начните с команды «создай рабочую программу».'
    )


def info_no_skills() -> str:
    return (
        "Skills не загружены. "
        "Запустите инициализацию: methodist-agent init."
    )


def info_no_search_results() -> str:
    return (
        "По запросу ничего не найдено. "
        "Попробуйте уточнить тему или тип материала."
    )


# ------------------------------------------------------------------
# Onboarding
# ------------------------------------------------------------------

def onboarding_welcome() -> str:
    return (
        "👋 Добро пожаловать в Методист-Агент!\n"
        "Я помогаю готовить рабочие программы, ведомости, презентации и отчёты. "
        "Все документы сохраняются в папку «Методист-Агент»."
    )


def onboarding_first_step() -> str:
    return (
        "Начнём с создания первого документа? "
        'Например: «создай рабочую программу по Базам данных, 144 часа».'
    )


def onboarding_env_report(report: str) -> str:
    return (
        "📋 Проверка окружения:\n"
        f"{report}\n"
        "Если что-то не найдено, агент всё равно будет работать во встроенном режиме."
    )


# ------------------------------------------------------------------
# Approval
# ------------------------------------------------------------------

def approval_prompt() -> str:
    return "\nПодтвердить выполнение? (y/n): "


def approval_rejected() -> str:
    return "❌ План отклонён."
```

- [ ] **Step 2: Add a failing test**

Create `tests/test_ui_text.py`:

```python
import pytest
from core.ui_text import (
    progress_creating_document,
    success_document_created,
    error_template_not_found,
    error_no_office_fallback,
    onboarding_welcome,
)


def test_progress_creating_document():
    assert progress_creating_document("curriculum") == "Создаю документ из шаблона: curriculum"


def test_success_document_created():
    assert "Документ готов" in success_document_created("/tmp/foo.docx")


def test_error_template_not_found():
    from pathlib import Path
    msg = error_template_not_found(Path("/tmp/missing"))
    assert "Шаблон не найден" in msg
    assert "init" in msg


def test_error_no_office_fallback():
    msg = error_no_office_fallback()
    assert "Office не найден" in msg
    assert "встроенный режим" in msg


def test_onboarding_welcome():
    assert "Добро пожаловать" in onboarding_welcome()
```

- [ ] **Step 3: Run the test to verify it fails**

```bash
cd /home/shugar/dev/Workspaces/auto/methodist-agent
./venv/bin/python -m pytest tests/test_ui_text.py -v
```

Expected: `ModuleNotFoundError: No module named 'core'` or import error.

- [ ] **Step 4: Add PYTHONPATH handling**

Tests already have `tests/conftest.py` that inserts `src` into `sys.path`. If it does not exist, create it:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

- [ ] **Step 5: Run the test to verify it passes**

```bash
./venv/bin/python -m pytest tests/test_ui_text.py -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/core/ui_text.py tests/test_ui_text.py
git commit -m "feat(ui): add centralized user-facing message registry"
```

---

## Task 2: Refactor `src/main.py` to use `ui_text`

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Replace create command messages**

In `src/main.py`, find the `create` command (around line 243) and replace:

```python
console.print(f"[bold blue]Создаю документ из шаблона: {template}[/bold blue]")
```

with:

```python
from core.ui_text import progress_creating_document, success_document_created, error_generic
console.print(f"[bold blue]{progress_creating_document(template)}[/bold blue]")
```

Then replace the success/error prints:

```python
console.print(f"[green]{success_document_created(result['path'])}[/green]")
```

and:

```python
console.print(f"[red]{error_generic('создать документ', str(e))}[/red]")
```

- [ ] **Step 2: Replace adapt command messages**

Use `progress_adapting_document`, `success_document_adapted`, `error_generic`.

- [ ] **Step 3: Replace search and pdf messages**

Use `progress_searching`, `success_search_results`, `progress_pdf`, `success_pdf_ready`, `error_generic`.

- [ ] **Step 4: Replace init welcome and chat welcome/error**

In `init`, after successful initialization, print:

```python
from core.ui_text import onboarding_welcome, onboarding_first_step
console.print(onboarding_welcome())
console.print(onboarding_first_step())
```

In `chat`, update the welcome banner text to match `onboarding_welcome()` tone (keep the banner itself; just align copy).

Replace the generic `except Exception as e:` handler in `_process_message` with:

```python
console.print(f"[red]{error_generic('обработать сообщение', str(e))}[/red]")
```

- [ ] **Step 5: Run smoke tests**

```bash
./venv/bin/python -m src.main --help
./venv/bin/python -m src.main init
./venv/bin/python -m src.main create curriculum --subject "Базы данных" --hours 144
```

Expected: commands work, messages are human-friendly.

- [ ] **Step 6: Commit**

```bash
git add src/main.py
git commit -m "refactor(cli): use centralized ui_text messages"
```

---

## Task 3: Refactor `src/agents/document_specialist.py` to use `ui_text`

**Files:**
- Modify: `src/agents/document_specialist.py`

- [ ] **Step 1: Import ui_text helpers**

At the top of the file, add:

```python
from core.ui_text import (
    error_template_not_found,
    error_template_folder_empty,
    error_unsupported_format,
    error_no_office_fallback,
    error_write_failed,
)
```

- [ ] **Step 2: Replace template error messages**

In `create_from_template`, replace:

```python
return {"success": False, "error": f"Шаблон не найден: {template_path}"}
```

with:

```python
return {"success": False, "error": error_template_not_found(template_path)}
```

Replace:

```python
return {"success": False, "error": f"В папке шаблона не найден template.*: {template_path}"}
```

with `error_template_folder_empty(template_path)`.

Replace:

```python
return {"success": False, "error": f"Неподдерживаемый формат: {output_format}"}
```

with `error_unsupported_format(output_format)`.

- [ ] **Step 3: Replace COM fallback messages**

In `create_docx` and other methods, find:

```python
logger.warning(f"COM create_docx не удался: {exc}. Fallback на native.")
```

Keep the logger line for debugging, but ensure the user-facing path returns/uses `error_no_office_fallback()` if native also fails. Currently native fallback happens silently; keep it silent unless it fails. If native fails:

```python
return {"success": False, "error": error_no_office_fallback() + " " + error_write_failed(str(output_path), str(exc))}
```

Actually simpler: keep fallback silent; only on final failure show a friendly message. Replace final native failure:

```python
return {"success": False, "error": "Ни COM, ни native библиотеки недоступны"}
```

with:

```python
return {"success": False, "error": error_no_office_fallback()}
```

- [ ] **Step 4: Run tests**

```bash
./venv/bin/python -m pytest tests/test_document_specialist.py -v
./venv/bin/python -m src.main create curriculum --subject "Тест" --hours 100
```

Expected: tests pass, document created, errors friendly if template missing.

- [ ] **Step 5: Commit**

```bash
git add src/agents/document_specialist.py
git commit -m "refactor(documents): use ui_text for user-facing messages"
```

---

## Task 4: Refactor `src/agents/adaptation_agent.py` to use `ui_text`

**Files:**
- Modify: `src/agents/adaptation_agent.py`

- [ ] **Step 1: Import ui_text helpers**

```python
from core.ui_text import error_no_office_fallback, error_file_not_found, error_generic
```

- [ ] **Step 2: Replace pywin32 debug and mode messages**

Find:

```python
logger.debug("pywin32 не установлен — COM-автоматизация недоступна")
```

Keep as logger debug (no user-facing change).

Find:

```python
logger.warning("Запрошен COM-режим, но pywin32 не установлен. Переключаюсь на native.")
```

Change to:

```python
logger.warning(error_no_office_fallback())
```

- [ ] **Step 3: Replace file not found and generic errors**

Replace:

```python
raise AdaptationError(f"Файл не найден: {input_file}")
```

with:

```python
raise AdaptationError(error_file_not_found(input_file))
```

Replace top-level exception in `execute` to wrap with `error_generic` if not already friendly.

- [ ] **Step 4: Run tests**

```bash
./venv/bin/python -m src.main adapt /path/that/does/not/exist.docx --output /tmp/out.docx
```

Expected: friendly "Файл не найден" message.

- [ ] **Step 5: Commit**

```bash
git add src/agents/adaptation_agent.py
git commit -m "refactor(adaptation): use ui_text for user-facing messages"
```

---

## Task 5: Refactor `src/windows/tray_app.py` to use `ui_text`

**Files:**
- Modify: `src/windows/tray_app.py`

- [ ] **Step 1: Import ui_text helpers**

```python
from core.ui_text import (
    progress_creating_document,
    success_document_created,
    error_generic,
    progress_searching,
    success_search_results,
    info_no_search_results,
)
```

- [ ] **Step 2: Replace create notification flow**

In `_create_document_dialog`, before creating document show a transient notification (optional) and after:

```python
if result.get("success"):
    self._show_notification("✅ Готово", success_document_created(result["path"]))
else:
    self._show_notification("❌ Ошибка", error_generic("создать документ", result.get("error", "")))
```

- [ ] **Step 3: Replace search notification flow**

Similarly use `progress_searching`, `success_search_results`, `info_no_search_results`.

- [ ] **Step 4: Replace error notifications**

Find all `self._show_notification("❌ Ошибка", str(e))` and wrap with `error_generic` if appropriate.

- [ ] **Step 5: Syntax check**

```bash
./venv/bin/python -m py_compile src/windows/tray_app.py
```

Expected: no output (success).

- [ ] **Step 6: Commit**

```bash
git add src/windows/tray_app.py
git commit -m "refactor(tray): use ui_text for notifications and dialogs"
```

---

## Task 6: Create `src/core/environment_check.py`

**Files:**
- Create: `src/core/environment_check.py`
- Test: `tests/test_environment_check.py`

- [ ] **Step 1: Implement environment checker**

Create `src/core/environment_check.py`:

```python
"""Environment checks for Methodist Agent.

Detects optional dependencies and reports findings in a human-friendly way.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class CheckItem:
    name: str
    available: bool
    message: str
    recommendation: str = ""


@dataclass
class EnvironmentReport:
    items: List[CheckItem] = field(default_factory=list)

    @property
    def all_good(self) -> bool:
        return all(item.available for item in self.items)

    def to_user_string(self) -> str:
        lines = []
        for item in self.items:
            icon = "✅" if item.available else "⚠️"
            lines.append(f"{icon} {item.name}: {item.message}")
            if item.recommendation:
                lines.append(f"   → {item.recommendation}")
        return "\n".join(lines)


def check_com_office() -> CheckItem:
    """Check if Windows COM automation for Office is available."""
    try:
        import win32com.client  # noqa: F401
        return CheckItem(
            name="Microsoft Office (COM)",
            available=True,
            message="Office обнаружен — доступен полный режим работы с документами.",
        )
    except ImportError:
        return CheckItem(
            name="Microsoft Office (COM)",
            available=False,
            message="Office/COM не обнаружен.",
            recommendation="Для расширенных возможностей установите Microsoft Office и pywin32. "
                           "Агент будет работать во встроенном режиме.",
        )


def check_tesseract() -> CheckItem:
    """Check if Tesseract OCR is available."""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return CheckItem(
            name="Tesseract OCR",
            available=True,
            message="Tesseract обнаружен — доступно распознавание сканов.",
        )
    except Exception:
        return CheckItem(
            name="Tesseract OCR",
            available=False,
            message="Tesseract не обнаружен.",
            recommendation="Для OCR установите Tesseract и добавьте его в PATH. "
                           "Агент будет извлекать текст из цифровых PDF.",
        )


def check_api_keys() -> CheckItem:
    """Check if at least one LLM provider is configured."""
    openai = os.getenv("OPENAI_API_KEY")
    anthropic = os.getenv("ANTHROPIC_API_KEY")
    if openai or anthropic:
        return CheckItem(
            name="API-ключ LLM",
            available=True,
            message="Найден API-ключ для облачной модели.",
        )
    return CheckItem(
        name="API-ключ LLM",
        available=False,
        message="API-ключи OpenAI/Anthropic не найдены.",
        recommendation="Добавьте ключ в ~/.methodist-agent/config.yaml или выберите локальную модель Ollama.",
    )


def run_environment_check() -> EnvironmentReport:
    """Run all environment checks and return a report."""
    return EnvironmentReport(items=[
        check_com_office(),
        check_tesseract(),
        check_api_keys(),
    ])
```

- [ ] **Step 2: Add tests**

Create `tests/test_environment_check.py`:

```python
from core.environment_check import run_environment_check, CheckItem


def test_run_environment_check():
    report = run_environment_check()
    assert len(report.items) == 3
    assert report.items[0].name == "Microsoft Office (COM)"
    assert isinstance(report.items[0].available, bool)


def test_environment_report_string():
    report = run_environment_check()
    text = report.to_user_string()
    assert "Microsoft Office" in text
    assert "Tesseract" in text
```

- [ ] **Step 3: Run tests**

```bash
./venv/bin/python -m pytest tests/test_environment_check.py -v
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add src/core/environment_check.py tests/test_environment_check.py
git commit -m "feat(env): add human-friendly environment checker"
```

---

## Task 7: Integrate onboarding and environment check into CLI

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Add `--check` flag to init and run environment check**

Modify `init` command signature:

```python
@app.command()
def init(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    check: bool = typer.Option(False, "--check", help="Run environment check only"),
):
```

At the start of `init`, if `check` is True:

```python
from core.environment_check import run_environment_check
from core.ui_text import onboarding_env_report
report = run_environment_check()
console.print(onboarding_env_report(report.to_user_string()))
return
```

- [ ] **Step 2: Show onboarding after normal init**

After creating directories and copying assets, print:

```python
from core.environment_check import run_environment_check
from core.ui_text import onboarding_welcome, onboarding_first_step, onboarding_env_report

console.print(onboarding_welcome())
console.print("")
report = run_environment_check()
console.print(onboarding_env_report(report.to_user_string()))
console.print("")
console.print(onboarding_first_step())
```

- [ ] **Step 3: Show welcome on first chat session**

In `chat`, before entering the loop, check if this is a new session and print `onboarding_welcome()` + `onboarding_first_step()`.

- [ ] **Step 4: Run smoke tests**

```bash
./venv/bin/python -m src.main init --check
./venv/bin/python -m src.main init
./venv/bin/python -m src.main chat --no-approval "создай рабочую программу по Базам данных"
```

Expected: onboarding prints, environment report prints, chat runs.

- [ ] **Step 5: Commit**

```bash
git add src/main.py
git commit -m "feat(cli): integrate onboarding and environment check"
```

---

## Task 8: Update documentation

**Files:**
- Modify: `docs/UX_GUIDE.md`
- Modify: `docs/DESIGN.md`

- [ ] **Step 1: Add concrete examples to UX_GUIDE**

Append a section `## Concrete examples in code` with snippets from `ui_text.py`:

```markdown
## Concrete examples in code

All user-facing strings live in `src/core/ui_text.py`. Examples:

- `error_no_office_fallback()` → "⚠️ Microsoft Office не найден. Переключаюсь на встроенный режим — документ всё равно будет готов."
- `error_api_key_missing()` → "❌ Не удалось подключиться к языковой модели..."
- `onboarding_welcome()` → "👋 Добро пожаловать в Методист-Агент..."
```

- [ ] **Step 2: Update DESIGN onboarding flow**

In `docs/DESIGN.md`, replace the onboarding section with:

```markdown
### Onboarding

1. **Приветствие** — `onboarding_welcome()`.
2. **Проверка окружения** — `run_environment_check()` через `init --check`.
3. **Создание первого документа** — `onboarding_first_step()`.
4. **Справка по команде `init --check`** — повторная проверка в любой момент.
```

- [ ] **Step 3: Commit**

```bash
git add docs/UX_GUIDE.md docs/DESIGN.md
git commit -m "docs: update UX/DESIGN with onboarding and ui_text examples"
```

---

## Task 9: Final verification

- [ ] **Step 1: Run full test suite**

```bash
./venv/bin/python -m pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Run lint on changed files**

```bash
./venv/bin/ruff check src/core/ui_text.py src/core/environment_check.py src/main.py src/agents/document_specialist.py src/agents/adaptation_agent.py src/windows/tray_app.py tests/test_ui_text.py tests/test_environment_check.py
```

Expected: minimal/no issues. Ignore pre-existing warnings in unrelated files.

- [ ] **Step 3: Manual smoke test**

```bash
./venv/bin/python -m src.main init --check
./venv/bin/python -m src.main init
./venv/bin/python -m src.main create curriculum --subject "Тест" --hours 100
```

Expected: friendly messages, document created.

- [ ] **Step 4: Commit if any fixes**

```bash
git add -A
git commit -m "chore: final fixes after UX/UI polish wave"
```

---

## Spec Coverage Check

| Requirement | Task |
|-------------|------|
| Centralized user-facing strings | Task 1 |
| Replace technical messages in CLI | Task 2 |
| Replace technical messages in DocumentSpecialist | Task 3 |
| Replace technical messages in AdaptationAgent | Task 4 |
| Replace technical messages in Tray | Task 5 |
| Human-friendly environment check | Task 6 |
| Onboarding flow | Task 7 |
| Documentation updated | Task 8 |
| Tests + lint pass | Task 9 |

No placeholders found. All file paths exact.
