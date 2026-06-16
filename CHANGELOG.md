# Changelog

Все значимые изменения в проекте фиксируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Changed
- LLM по умолчанию: primary — Anthropic (Claude `claude-opus-4-8`), fallback — OpenAI (`gpt-4o`). Раньше primary был OpenAI.

### Added
- Профессиональный README (вайб `calm professional`), `.env.example`, MIT LICENSE.
- `CONTRIBUTING.md` и этот `CHANGELOG.md`.

## [1.0.0] — 2026-06-15

### Added
- CLI-точка входа `python -m src.main` с командами `init`, `chat`, `create`, `search`, `adapt`, `pdf`, `tray`.
- Core Engine: `orchestrator` (диспетчер), `model_router` (OpenAI / Anthropic / Ollama), `context_manager` (контекст и skills), `config` на Pydantic.
- Специализированные агенты: `document_specialist`, `web_search`, `pdf_reader`, `adaptation_agent`.
- Репозиторий навыков (`skills/`): создание DOCX, XLSX, PPTX.
- Работа с документами: DOCX, XLSX, PPTX, PDF (чтение, извлечение текста/таблиц, OCR, конвертация).
- Windows-интеграция: системный трей, контекстное меню, COM-автоматизация Office.
- Конфигурация через `~/.methodist-agent/config.yaml` и `.env`.
- Набор unit-тестов (pytest + coverage).

[Unreleased]: https://github.com/Shugar86/methodist-agent/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Shugar86/methodist-agent/releases/tag/v1.0.0
