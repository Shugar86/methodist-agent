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
