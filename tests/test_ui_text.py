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
