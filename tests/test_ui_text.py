from pathlib import Path

from core.ui_text import (
    approval_prompt,
    approval_rejected,
    chat_goodbye,
    chat_hint_exit,
    error_agent_not_implemented,
    error_generic,
    error_no_office_fallback,
    error_pdf_processing,
    error_task_execution,
    error_template_not_found,
    info_data_dir,
    info_output_dir,
    info_skills_dir,
    info_templates_dir,
    onboarding_welcome,
    progress_creating_document,
    search_header_description,
    search_header_index,
    search_header_title,
    search_header_url,
    search_results_title,
    status_analyzing_request,
    status_executing_plan,
    success_document_created,
    task_success,
    task_warning,
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


def test_info_data_dir():
    assert info_data_dir("/tmp/data") == "📁 Данные: /tmp/data"


def test_info_templates_dir():
    assert info_templates_dir(Path("/tmp/templates")) == "📁 Шаблоны: /tmp/templates"


def test_info_skills_dir():
    assert "📁 Skills" in info_skills_dir("/tmp/skills")


def test_info_output_dir():
    assert "Выходные файлы" in info_output_dir("/tmp/out")


def test_status_analyzing_request():
    assert status_analyzing_request() == "Анализирую запрос…"


def test_status_executing_plan():
    assert "▶ Выполняю план" in status_executing_plan()


def test_chat_hint_exit():
    msg = chat_hint_exit()
    assert "Интерактивный режим" in msg
    assert "exit" in msg


def test_chat_goodbye():
    assert "До свидания" in chat_goodbye()


def test_approval_prompt():
    assert "Подтвердить выполнение" in approval_prompt()


def test_approval_rejected():
    assert "План отклонён" in approval_rejected()


def test_error_agent_not_implemented():
    msg = error_agent_not_implemented("foo_agent")
    assert "foo_agent" in msg
    assert "еще не реализован" in msg or "ещё не реализован" in msg


def test_error_task_execution():
    assert error_task_execution("boom") == "Ошибка выполнения: boom"


def test_error_generic():
    assert "Не удалось" in error_generic("сделать", "бум")


def test_search_results_title():
    assert search_results_title() == "Результаты поиска"


def test_search_header_index():
    assert search_header_index() == "#"


def test_search_header_title():
    assert search_header_title() == "Заголовок"


def test_search_header_url():
    assert search_header_url() == "URL"


def test_search_header_description():
    assert search_header_description() == "Описание"


def test_task_success():
    assert task_success("Сделано") == "  ✅ Сделано"


def test_task_warning():
    assert task_warning("Внимание") == "  ⚠️ Внимание — требуется внимание"


def test_error_pdf_processing():
    msg = error_pdf_processing("файл повреждён")
    assert "Не удалось обработать PDF" in msg
    assert "файл повреждён" in msg


def test_workspace_strings_exist():
    from core import ui_text

    assert callable(getattr(ui_text, "workspace_title", None))
    assert callable(getattr(ui_text, "workspace_quick_actions", None))
    assert callable(getattr(ui_text, "workspace_approved", None))
    assert callable(getattr(ui_text, "workspace_cancelled", None))
    assert callable(getattr(ui_text, "workspace_file_panel", None))
