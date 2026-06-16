"""
Context Manager - manages sessions, skills loading, and context.
Inspired by OpenCode's ContextScout concept.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from core.config import Config, get_data_dir
from core.context_scout import ContextScout
from core.skill_registry import SkillRegistry, SkillV2


@dataclass
class Session:
    """A user session."""

    id: str
    name: str
    created_at: str
    updated_at: str
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class Skill:
    """A loaded skill."""

    name: str
    category: str
    path: Path
    triggers: List[str]
    content: str
    metadata: Dict[str, Any]


class ContextManager:
    """Manages sessions, skills, and context for the agent."""

    def __init__(self, config: Config):
        self.config = config
        self.data_dir = get_data_dir(config)
        self.db_path = self.data_dir / "sessions.db"
        self.skills_dir = Path(config.skills.repository).expanduser()
        self.skill_registry: Optional[SkillRegistry] = None
        self._context_scout: Optional[ContextScout] = None
        if config.skills.auto_load:
            self.skill_registry = SkillRegistry(self.skills_dir)
            self._context_scout = ContextScout(skill_registry=self.skill_registry)
        self._current_session: Optional[Session] = None

        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            conn.commit()

    def create_session(self, name: str = "New Session") -> Session:
        """Create a new session."""
        session_id = f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.now().isoformat()
        session = Session(
            id=session_id, name=name, created_at=now, updated_at=now, messages=[], metadata={}
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO sessions (id, name, created_at, updated_at, messages, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session.id,
                    session.name,
                    session.created_at,
                    session.updated_at,
                    json.dumps(session.messages),
                    json.dumps(session.metadata),
                ),
            )
            conn.commit()

        self._current_session = session
        return session

    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, name, created_at, updated_at, messages, metadata FROM sessions WHERE id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            if row:
                session = Session(
                    id=row[0],
                    name=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                    messages=json.loads(row[4]),
                    metadata=json.loads(row[5]),
                )
                self._current_session = session
                return session
        return None

    def save_session(self, session: Optional[Session] = None) -> None:
        """Save session to database."""
        session = session or self._current_session
        if not session:
            return

        session.updated_at = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE sessions SET name = ?, updated_at = ?, messages = ?, metadata = ? WHERE id = ?",
                (
                    session.name,
                    session.updated_at,
                    json.dumps(session.messages),
                    json.dumps(session.metadata),
                    session.id,
                ),
            )
            conn.commit()

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to current session."""
        if not self._current_session:
            self.create_session()

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self._current_session.messages.append(message)
        self.save_session()

    def get_session_history(self, limit: int = 50) -> List[Dict]:
        """Get recent messages from current session."""
        if not self._current_session:
            return []
        return self._current_session.messages[-limit:]

    def list_sessions(self) -> List[Dict]:
        """List all sessions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, name, created_at, updated_at FROM sessions ORDER BY updated_at DESC"
            )
            return [
                {"id": row[0], "name": row[1], "created_at": row[2], "updated_at": row[3]}
                for row in cursor.fetchall()
            ]

    def _to_skill(self, key: str, skill_v2: SkillV2) -> Skill:
        """Convert a SkillV2 from the registry to the public Skill dataclass."""
        category, name = key.split("/", 1)
        return Skill(
            name=name,
            category=category,
            path=skill_v2.path.parent,
            triggers=skill_v2.triggers,
            content=skill_v2.path.read_text(encoding="utf-8"),
            metadata=skill_v2.metadata,
        )

    def find_skills(self, query: str) -> List[Skill]:
        """Find skills matching query via the ContextScout."""
        if self._context_scout is None or self.skill_registry is None:
            return []
        items = self._context_scout.find_relevant(query, top_k=len(self.skill_registry.catalog))
        results: List[Skill] = []
        for item in items:
            skill_v2 = self.skill_registry.get(item.key)
            if skill_v2:
                results.append(self._to_skill(item.key, skill_v2))
        return results

    def get_skill(self, category: str, name: str) -> Optional[Skill]:
        """Get a specific skill by category and name."""
        if self.skill_registry is None:
            return None
        skill_v2 = self.skill_registry.get(f"{category}/{name}")
        if skill_v2 is None:
            return None
        return self._to_skill(f"{category}/{name}", skill_v2)

    def get_all_skills(self) -> Dict[str, Skill]:
        """Get all loaded skills."""
        if self.skill_registry is None:
            return {}
        return {
            key: self._to_skill(key, skill_v2)
            for key, skill_v2 in self.skill_registry.catalog.items()
        }

    def log_action(self, action: str, details: Optional[str] = None) -> None:
        """Log an action to context history."""
        if not self._current_session:
            return

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO context_history (session_id, timestamp, action, details) VALUES (?, ?, ?, ?)",
                (self._current_session.id, datetime.now().isoformat(), action, details),
            )
            conn.commit()
