"""
Configuration loader for Voice Agent.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Base directory
BASE_DIR = Path(__file__).parent


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1


@dataclass
class Config:
    """Main configuration class."""

    groq_api_key: str = ""
    hotkey: str = "ctrl+m"
    language: str = "it"
    audio: AudioConfig = field(default_factory=AudioConfig)
    text_corrections: list = field(default_factory=list)

    def toggle_language(self) -> str:
        """Toggle between Italian and English."""
        self.language = "en" if self.language == "it" else "it"
        return self.language


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file and environment variables."""

    if config_path is None:
        config_path = BASE_DIR / "config.yaml"

    config = Config()

    # Load from YAML if exists
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f) or {}

        config.hotkey = yaml_config.get("hotkey", config.hotkey)
        config.language = yaml_config.get("language", config.language)
        config.text_corrections = yaml_config.get("text_corrections", [])

        audio_cfg = yaml_config.get("audio", {})
        config.audio = AudioConfig(
            sample_rate=audio_cfg.get("sample_rate", 16000),
            channels=audio_cfg.get("channels", 1),
        )

    # Load API key from environment (overrides everything)
    config.groq_api_key = os.getenv("GROQ_API_KEY", "")

    # Try loading from .env file if not in environment
    if not config.groq_api_key:
        env_path = BASE_DIR / ".env"
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GROQ_API_KEY="):
                        config.groq_api_key = line.split("=", 1)[1].strip()
                        break

    return config


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


