"""
Context Manager - manages sessions, skills loading, and context.
Inspired by OpenCode's ContextScout concept.
"""

import os
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from core.config import Config, get_data_dir


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
        self._current_session: Optional[Session] = None
        self._loaded_skills: Dict[str, Skill] = {}
        
        self._init_db()
        if config.skills.auto_load:
            self._load_all_skills()
    
    def _init_db(self):
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
            id=session_id,
            name=name,
            created_at=now,
            updated_at=now,
            messages=[],
            metadata={}
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO sessions (id, name, created_at, updated_at, messages, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (session.id, session.name, session.created_at, session.updated_at,
                 json.dumps(session.messages), json.dumps(session.metadata))
            )
            conn.commit()
        
        self._current_session = session
        return session
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, name, created_at, updated_at, messages, metadata FROM sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                session = Session(
                    id=row[0],
                    name=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                    messages=json.loads(row[4]),
                    metadata=json.loads(row[5])
                )
                self._current_session = session
                return session
        return None
    
    def save_session(self, session: Optional[Session] = None):
        """Save session to database."""
        session = session or self._current_session
        if not session:
            return
        
        session.updated_at = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE sessions SET name = ?, updated_at = ?, messages = ?, metadata = ? WHERE id = ?",
                (session.name, session.updated_at, json.dumps(session.messages),
                 json.dumps(session.metadata), session.id)
            )
            conn.commit()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to current session."""
        if not self._current_session:
            self.create_session()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
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
    
    def _load_all_skills(self):
        """Load all skills from skills directory."""
        if not self.skills_dir.exists():
            return
        
        for category_dir in self.skills_dir.iterdir():
            if category_dir.is_dir():
                for skill_dir in category_dir.iterdir():
                    if skill_dir.is_dir():
                        self._load_skill(skill_dir, category_dir.name)
    
    def _load_skill(self, skill_dir: Path, category: str):
        """Load a single skill."""
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            return
        
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            metadata = self._parse_skill_frontmatter(content)
            
            skill = Skill(
                name=skill_dir.name,
                category=category,
                path=skill_dir,
                triggers=metadata.get("triggers", []),
                content=content,
                metadata=metadata
            )
            
            self._loaded_skills[f"{category}/{skill_dir.name}"] = skill
        except Exception as e:
            print(f"Error loading skill {skill_dir}: {e}")
    
    def _parse_skill_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from skill markdown."""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    return yaml.safe_load(parts[1]) or {}
                except ImportError:
                    pass
        return {}
    
    def find_skills(self, query: str) -> List[Skill]:
        """Find skills matching query (ContextScout)."""
        query_lower = query.lower()
        results = []
        
        for skill in self._loaded_skills.values():
            score = 0
            
            # Check triggers
            for trigger in skill.triggers:
                if trigger.lower() in query_lower:
                    score += 10
            
            # Check content
            if query_lower in skill.content.lower():
                score += 5
            
            # Check category
            if query_lower in skill.category.lower():
                score += 2
            
            if score > 0:
                results.append((score, skill))
        
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [skill for _, skill in results]
    
    def get_skill(self, category: str, name: str) -> Optional[Skill]:
        """Get a specific skill by category and name."""
        return self._loaded_skills.get(f"{category}/{name}")
    
    def get_all_skills(self) -> Dict[str, Skill]:
        """Get all loaded skills."""
        return self._loaded_skills.copy()
    
    def log_action(self, action: str, details: Optional[str] = None):
        """Log an action to context history."""
        if not self._current_session:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO context_history (session_id, timestamp, action, details) VALUES (?, ?, ?, ?)",
                (self._current_session.id, datetime.now().isoformat(), action, details)
            )
            conn.commit()
