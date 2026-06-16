"""
Configuration module for Methodist Agent.
Uses Pydantic for validation and supports YAML config files.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class ModelConfig(BaseModel):
    """Configuration for a single LLM provider."""
    provider: str = "anthropic"
    model: str = "claude-opus-4-8"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


class WindowsConfig(BaseModel):
    """Windows-specific configuration."""
    tray_icon: bool = True
    context_menu: bool = True
    file_association: bool = True
    com_automation: bool = True
    default_office_path: Optional[str] = None


class SkillsConfig(BaseModel):
    """Skills system configuration."""
    auto_load: bool = True
    repository: str = "~/.methodist-agent/skills"
    lazy_load: bool = True


class SearchConfig(BaseModel):
    """Web search configuration."""
    engine: str = "duckduckgo"  # duckduckgo, serpapi, google
    serpapi_key: Optional[str] = None
    google_api_key: Optional[str] = None
    google_cx: Optional[str] = None
    max_results: int = 10


class DocumentsConfig(BaseModel):
    """Document processing configuration."""
    default_template_path: str = "~/.methodist-agent/templates"
    output_path: str = "~/Documents/Методист-Агент"
    preferred_mode: str = "com"  # com, native, auto
    auto_save: bool = True


class ApprovalConfig(BaseModel):
    """Approval gates configuration."""
    enabled: bool = True
    auto_approve_simple: bool = False
    auto_approve_read_only: bool = True
    require_approval_for: List[str] = Field(default_factory=lambda: [
        "file_write", "shell_exec", "web_download", "email_send"
    ])


class AgentConfig(BaseModel):
    """Main agent configuration."""
    name: str = "methodist-agent"
    version: str = "1.0.0"
    language: str = "ru"
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = "~/.methodist-agent"


class Config(BaseModel):
    """Root configuration model."""
    agent: AgentConfig = Field(default_factory=AgentConfig)
    models: Dict[str, ModelConfig] = Field(default_factory=lambda: {
        "primary": ModelConfig(provider="anthropic", model="claude-opus-4-8"),
        "fallback": ModelConfig(provider="openai", model="gpt-4o"),
    })
    windows: WindowsConfig = Field(default_factory=WindowsConfig)
    skills: SkillsConfig = Field(default_factory=SkillsConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    documents: DocumentsConfig = Field(default_factory=DocumentsConfig)
    approval: ApprovalConfig = Field(default_factory=ApprovalConfig)

    @field_validator('models', mode='before')
    @classmethod
    def validate_models(cls, v):
        if isinstance(v, dict):
            return {k: ModelConfig(**v[k]) if isinstance(v[k], dict) else v[k] for k in v}
        return v


def get_default_config_path() -> Path:
    """Get the default configuration file path."""
    return Path.home() / ".methodist-agent" / "config.yaml"


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML file or create default."""
    if config_path is None:
        config_path = get_default_config_path()
    else:
        config_path = Path(config_path)
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load from file if exists
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return Config(**data) if data else Config()
    
    # Create default config
    config = Config()
    save_config(config, str(config_path))
    return config


def save_config(config: Config, config_path: Optional[str] = None) -> None:
    """Save configuration to YAML file."""
    if config_path is None:
        config_path = get_default_config_path()
    else:
        config_path = Path(config_path)
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config.model_dump(), f, allow_unicode=True, sort_keys=False)


def get_data_dir(config: Config) -> Path:
    """Get the data directory path."""
    path = Path(config.agent.data_dir).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_templates_dir(config: Config) -> Path:
    """Get the templates directory path."""
    path = Path(config.documents.default_template_path).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_dir(config: Config) -> Path:
    """Get the output directory path."""
    path = Path(config.documents.output_path).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_skills_dir(config: Config) -> Path:
    """Get the skills directory path."""
    path = Path(config.skills.repository).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path
