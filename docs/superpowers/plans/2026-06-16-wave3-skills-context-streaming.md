# Methodist Agent v2 — Wave 3: Skills v2 + ContextScout + Streaming

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Улучшить систему навыков до стандарта Skills v2 (YAML frontmatter + Markdown), добавить ContextScout для релевантного поиска контекста, и реализовать streaming-вывод LLM-ответов в чат.

**Architecture:** `SkillRegistry` загружает skills с progressive disclosure (catalog → full skill). `ContextScout` ранжирует релевантные skills/шаблоны/контекст по triggers и keywords. `ModelRouter.chat(..., stream=True)` возвращает async iterator, который UI отображает в `ChatPanel`.

**Tech Stack:** Python 3.11+, pydantic, pytest, async OpenAI/Anthropic SDK.

---

## Task 1: Skills v2 dataclass and parser

**Files:**
- Create: `src/core/skill_registry.py`
- Test: `tests/test_skill_registry.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_skill_registry.py
from pathlib import Path
import tempfile
from core.skill_registry import SkillV2, parse_skill_frontmatter


def test_parse_skill_frontmatter():
    content = """---
name: create-rpd
description: Создаёт рабочую программу.
triggers:
  - рабочая программа
---

# Инструкции
1. Запроси дисциплину.
"""
    skill = parse_skill_frontmatter(Path("/tmp/create-rpd/SKILL.md"), content)
    assert skill.name == "create-rpd"
    assert skill.description == "Создаёт рабочую программу."
    assert skill.triggers == ["рабочая программа"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_skill_registry.py::test_parse_skill_frontmatter -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/skill_registry.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class SkillV2:
    name: str
    description: str
    path: Path
    triggers: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    allowed_tools: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    content: str = ""


def parse_skill_frontmatter(path: Path, content: str) -> SkillV2:
    metadata: Dict[str, Any] = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()

    return SkillV2(
        name=metadata.get("name", path.parent.name),
        description=metadata.get("description", ""),
        path=path,
        triggers=metadata.get("triggers", []),
        examples=metadata.get("examples", []),
        inputs=metadata.get("inputs", {}),
        outputs=metadata.get("outputs", {}),
        validation=metadata.get("validation", {}),
        allowed_tools=metadata.get("allowed-tools", []),
        metadata=metadata.get("metadata", {}),
        content=body,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_skill_registry.py::test_parse_skill_frontmatter -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/skill_registry.py tests/test_skill_registry.py
git commit -m "feat(skills): add SkillV2 dataclass and frontmatter parser"
```

---

## Task 2: SkillRegistry

**Files:**
- Modify: `src/core/skill_registry.py`
- Test: `tests/test_skill_registry.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_skill_registry.py — append
import tempfile
from pathlib import Path


def test_skill_registry_loads_skills():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "curriculum" / "create-rpd"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: create-rpd\ndescription: Создаёт РПД.\ntriggers:\n  - рабочая программа\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )
        registry = SkillRegistry(tmpdir)
        assert "curriculum/create-rpd" in registry.catalog
        assert registry.catalog["curriculum/create-rpd"].description == "Создаёт РПД."
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_skill_registry.py::test_skill_registry_loads_skills -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/skill_registry.py — append
class SkillRegistry:
    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir).expanduser()
        self.catalog: Dict[str, SkillV2] = {}
        self._load_all()

    def _load_all(self) -> None:
        if not self.skills_dir.exists():
            return
        for category_dir in sorted(self.skills_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            for skill_dir in sorted(category_dir.iterdir()):
                if not skill_dir.is_dir():
                    continue
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skill = parse_skill_frontmatter(skill_file, skill_file.read_text(encoding="utf-8"))
                    self.catalog[f"{category_dir.name}/{skill_dir.name}"] = skill

    def get(self, key: str) -> Optional[SkillV2]:
        return self.catalog.get(key)

    def find_by_trigger(self, query: str) -> List[SkillV2]:
        query_lower = query.lower()
        results = []
        for skill in self.catalog.values():
            for trigger in skill.triggers:
                if trigger.lower() in query_lower:
                    results.append(skill)
                    break
        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_skill_registry.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/skill_registry.py tests/test_skill_registry.py
git commit -m "feat(skills): add SkillRegistry with catalog loading"
```

---

## Task 3: SkillValidator

**Files:**
- Create: `src/core/skill_validator.py`
- Test: `tests/test_skill_validator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_skill_validator.py
from pathlib import Path
import tempfile
from core.skill_validator import SkillValidator


def test_validator_rejects_missing_description():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "curriculum" / "bad-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: bad-skill\n---\n\nBody.\n", encoding="utf-8")
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert any("description" in err.lower() for err in errors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_skill_validator.py::test_validator_rejects_missing_description -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/skill_validator.py
import re
from pathlib import Path
from typing import List

from core.skill_registry import SkillRegistry


class SkillValidator:
    def __init__(self, skills_dir: Path):
        self.registry = SkillRegistry(skills_dir)

    def validate_all(self) -> List[str]:
        errors = []
        seen = set()
        for key, skill in self.registry.catalog.items():
            if not skill.name:
                errors.append(f"{key}: missing name")
            if not re.fullmatch(r"[a-z0-9-]+", skill.name):
                errors.append(f"{key}: invalid name '{skill.name}'")
            if not skill.description:
                errors.append(f"{key}: missing description")
            if len(skill.description) > 1024:
                errors.append(f"{key}: description too long")
            if skill.name in seen:
                errors.append(f"{key}: duplicate name '{skill.name}'")
            seen.add(skill.name)
        return errors
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_skill_validator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/skill_validator.py tests/test_skill_validator.py
git commit -m "feat(skills): add SkillValidator"
```

---

## Task 4: ContextScout

**Files:**
- Create: `src/core/context_scout.py`
- Test: `tests/test_context_scout.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_context_scout.py
from pathlib import Path
import tempfile
from core.context_scout import ContextScout
from core.skill_registry import SkillRegistry


def test_context_scout_finds_skill_by_trigger():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "curriculum" / "create-rpd"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: create-rpd\ndescription: Создаёт РПД.\ntriggers:\n  - рабочую программу\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )
        registry = SkillRegistry(tmpdir)
        scout = ContextScout(skill_registry=registry)
        results = scout.find_relevant("создай рабочую программу по математике")
        assert any(item.key == "curriculum/create-rpd" for item in results)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_context_scout.py::test_context_scout_finds_skill_by_trigger -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/context_scout.py
from dataclasses import dataclass
from typing import List, Optional

from core.skill_registry import SkillRegistry


@dataclass
class ContextItem:
    key: str
    source: str  # "skill", "template", "context_file", "session"
    content: str
    score: int


class ContextScout:
    def __init__(self, skill_registry: Optional[SkillRegistry] = None):
        self.skill_registry = skill_registry

    def find_relevant(self, query: str, top_k: int = 5) -> List[ContextItem]:
        query_lower = query.lower()
        scored: List[ContextItem] = []

        if self.skill_registry:
            for key, skill in self.skill_registry.catalog.items():
                score = 0
                for trigger in skill.triggers:
                    if trigger.lower() in query_lower:
                        score += 10
                if skill.description.lower() in query_lower:
                    score += 5
                if query_lower in skill.description.lower():
                    score += 3
                if score > 0:
                    scored.append(ContextItem(
                        key=key,
                        source="skill",
                        content=f"{skill.name}: {skill.description}",
                        score=score,
                    ))

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_context_scout.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/context_scout.py tests/test_context_scout.py
git commit -m "feat(context): add ContextScout for skill relevance ranking"
```

---

## Task 5: Streaming in ModelRouter

**Files:**
- Modify: `src/core/model_router.py`
- Test: `tests/test_model_router.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_model_router.py
from unittest.mock import MagicMock, patch
import pytest
from core.model_router import ModelRouter
from core.config import Config


def test_model_router_stream_returns_chunks():
    config = Config()
    router = ModelRouter(config)
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock(delta=MagicMock(content="Hello"))]

    with patch.object(router, "_get_client", return_value=MagicMock()) as mock_client_get:
        mock_client = mock_client_get.return_value
        mock_client.chat.completions.create.return_value = iter([mock_chunk])

        with patch.object(router, "_chat_openai", return_value=mock_client.chat.completions.create.return_value):
            chunks = list(router.chat([MagicMock(role="user", content="Hi")], stream=True))
            assert any("Hello" in chunk for chunk in chunks)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_model_router.py::test_model_router_stream_returns_chunks -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Modify `src/core/model_router.py`:
- `chat(..., stream=True)` should return the raw stream iterator from `_chat_openai`/`_chat_anthropic`.
- Consumers will iterate over chunks.

```python
# In ModelRouter.chat
if stream:
    kwargs["stream"] = True
    return client.chat.completions.create(**kwargs)
```

Actually, the existing implementation already has `stream` parameter but returns `ChatResponse`. We need to change so that when `stream=True`, it returns the iterator. Update `_chat_openai` and `_chat_anthropic` to respect `stream` and return the stream object.

For OpenAI:
```python
if stream:
    kwargs["stream"] = True
    return client.chat.completions.create(**kwargs)
```

For Anthropic:
```python
if stream:
    kwargs["stream"] = True
    return client.messages.create(**kwargs)
```

Also update `chat()`:
```python
if stream:
    return self._chat_openai(...)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_model_router.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/model_router.py tests/test_model_router.py
git commit -m "feat(llm): add streaming support to ModelRouter"
```

---

## Task 6: Streaming in ChatPanel

**Files:**
- Modify: `src/windows/chat_panel.py`
- Test: `tests/test_chat_panel.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_chat_panel.py — append
import queue


def test_chat_panel_stream_message(root):
    panel = ChatPanel(root)
    panel.start_stream()
    panel.append_stream_chunk("Привет")
    panel.append_stream_chunk(" мир")
    panel.finish_stream()
    text = panel.get_text()
    assert "Привет мир" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_chat_panel.py::test_chat_panel_stream_message -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/windows/chat_panel.py — add methods
    def start_stream(self) -> None:
        self.history.configure(state="normal")
        self.history.insert("end", "assistant: ")
        self.history.configure(state="disabled")
        self._stream_buffer = ""

    def append_stream_chunk(self, text: str) -> None:
        if not text:
            return
        self._stream_buffer += text
        self.history.configure(state="normal")
        self.history.insert("end", text)
        self.history.configure(state="disabled")
        self.history.see("end")

    def finish_stream(self) -> None:
        self.history.configure(state="normal")
        self.history.insert("end", "\n\n")
        self.history.configure(state="disabled")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_chat_panel.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/windows/chat_panel.py tests/test_chat_panel.py
git commit -m "feat(ui): add streaming display methods to ChatPanel"
```

---

## Task 7: Integrate ContextScout into Orchestrator

**Files:**
- Modify: `src/core/orchestrator.py`
- Test: `tests/test_orchestrator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_orchestrator.py
from unittest.mock import MagicMock
from core.orchestrator import Orchestrator
from core.context_scout import ContextScout


def test_orchestrator_uses_context_scout():
    config = MagicMock()
    config.approval.enabled = False
    model_router = MagicMock()
    model_router.chat.return_value.content = "[]"
    context_manager = MagicMock()
    context_manager._current_session = None
    scout = MagicMock()
    scout.find_relevant.return_value = []

    orch = Orchestrator(config, model_router, context_manager, context_scout=scout)
    orch.create_plan("создай рабочую программу")
    scout.find_relevant.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_orchestrator.py::test_orchestrator_uses_context_scout -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Modify `src/core/orchestrator.py`:
- Add optional `context_scout` parameter to `Orchestrator.__init__`.
- In `create_plan`, call `self.context_scout.find_relevant(user_input)` and include relevant context in the system prompt or as a user message.

```python
# In __init__
def __init__(self, config, model_router, context_manager, context_scout=None):
    ...
    self.context_scout = context_scout

# In create_plan
context_items = []
if self.context_scout:
    context_items = self.context_scout.find_relevant(user_input)
context_text = "\n".join(f"- {item.content}" for item in context_items)
```

Add context_text to the system prompt.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_orchestrator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/orchestrator.py tests/test_orchestrator.py
git commit -m "feat(orchestrator): integrate ContextScout into planning"
```

---

## Task 8: Integrate Skills v2 into ContextManager

**Files:**
- Modify: `src/core/context_manager.py`
- Test: `tests/test_context_manager.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_context_manager.py
from unittest.mock import MagicMock
from pathlib import Path
import tempfile
from core.context_manager import ContextManager


def test_context_manager_uses_skill_registry(tmp_path):
    config = MagicMock()
    config.skills.repository = str(tmp_path)
    config.skills.auto_load = True
    cm = ContextManager(config)
    assert hasattr(cm, "skill_registry")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_context_manager.py::test_context_manager_uses_skill_registry -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Modify `src/core/context_manager.py`:
- Replace `_loaded_skills` dict with `SkillRegistry`.
- Keep `find_skills` and `get_skill` methods for backward compatibility, delegating to `SkillRegistry`.
- Optionally keep old skill loading as fallback.

```python
from core.skill_registry import SkillRegistry

# In __init__
self.skill_registry = SkillRegistry(self.skills_dir)
self._context_scout = ContextScout(skill_registry=self.skill_registry)

# find_skills / get_skill delegate to skill_registry
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_context_manager.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/context_manager.py tests/test_context_manager.py
git commit -m "feat(context): integrate SkillRegistry into ContextManager"
```

---

## Task 9: Update sample skills to v2 format

**Files:**
- Modify: existing `skills/**/SKILL.md` files.

- [ ] **Step 1: Find existing skills**

Run: `find skills -name "SKILL.md"`

- [ ] **Step 2: Update each SKILL.md**

Ensure each has YAML frontmatter:
```yaml
---
name: <matches-directory-name>
description: <concise description>
triggers:
  - <keyword>
---
```

Keep the body content unchanged.

- [ ] **Step 3: Run SkillValidator**

Add or run a test:
```python
# tests/test_skill_validator.py — append
def test_sample_skills_pass_validation():
    from core.config import Config
    from core.skill_validator import SkillValidator
    config = Config()
    validator = SkillValidator(config.skills.repository)
    errors = validator.validate_all()
    assert errors == [], f"Skill validation errors: {errors}"
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_skill_validator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/ tests/test_skill_validator.py
git commit -m "feat(skills): update sample skills to v2 format"
```

---

## Task 10: Final lint/test/commit

**Files:**
- All Wave 3 files.

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: all pass

- [ ] **Step 2: Run ruff on Wave 3 files**

Run: `ruff check src/core/skill_registry.py src/core/skill_validator.py src/core/context_scout.py src/core/model_router.py src/core/orchestrator.py src/core/context_manager.py src/windows/chat_panel.py tests/test_skill_registry.py tests/test_skill_validator.py tests/test_context_scout.py tests/test_model_router.py tests/test_chat_panel.py tests/test_orchestrator.py tests/test_context_manager.py`
Expected: clean

- [ ] **Step 3: Run ruff format --check**

Run: `ruff format --check src/core/skill_registry.py src/core/skill_validator.py src/core/context_scout.py src/core/model_router.py src/core/orchestrator.py src/core/context_manager.py src/windows/chat_panel.py tests/test_skill_registry.py tests/test_skill_validator.py tests/test_context_scout.py tests/test_model_router.py tests/test_chat_panel.py tests/test_orchestrator.py tests/test_context_manager.py`
Expected: all formatted

- [ ] **Step 4: Commit final wave**

```bash
git add .
git commit -m "feat(skills): complete Wave 3 Skills v2 + ContextScout + streaming"
```

---

## Self-review checklist

- [ ] SkillV2 dataclass and parser tested.
- [ ] SkillRegistry loads catalog.
- [ ] SkillValidator validates name/description/uniqueness.
- [ ] ContextScout ranks skills by trigger/description.
- [ ] ModelRouter supports streaming.
- [ ] ChatPanel displays streaming chunks.
- [ ] Orchestrator uses ContextScout.
- [ ] ContextManager uses SkillRegistry.
- [ ] Sample skills updated to v2 format.
- [ ] Full suite passes, lint/format clean.
