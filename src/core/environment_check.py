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
    return EnvironmentReport(items=[
        check_com_office(),
        check_tesseract(),
        check_api_keys(),
    ])
