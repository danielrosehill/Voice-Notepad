"""Configuration management for Voice Notepad V3."""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional


CONFIG_DIR = Path.home() / ".config" / "voice-notepad-v3"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Config:
    """Application configuration."""

    # API Keys
    gemini_api_key: str = ""
    openai_api_key: str = ""
    mistral_api_key: str = ""

    # Selected model provider: "gemini", "openai", "mistral"
    selected_provider: str = "gemini"

    # Model names per provider
    gemini_model: str = "gemini-2.0-flash-lite"
    openai_model: str = "gpt-4o-audio-preview"
    mistral_model: str = "mistral-small-latest"

    # Audio settings
    selected_microphone: str = ""
    sample_rate: int = 48000

    # UI settings
    window_width: int = 500
    window_height: int = 600
    start_minimized: bool = False

    # Cleanup prompt
    cleanup_prompt: str = """Your task is to provide a cleaned transcription of the audio recorded by the user.
- Remove filler words (um, uh, like, you know, etc.)
- Add proper punctuation and sentence structure
- Add natural paragraph spacing
- If the user makes any verbal instructions during the recording (such as "don't include this" or "new paragraph"), follow those instructions
- Add markdown subheadings (## Heading) if it's a lengthy transcription with distinct sections
- Use markdown formatting where appropriate (bold, lists, etc.)
- Output ONLY the cleaned transcription in markdown format, no commentary or preamble"""


def load_config() -> Config:
    """Load configuration from disk, or create default."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            return Config(**data)
        except (json.JSONDecodeError, TypeError):
            pass

    # Return default config
    return Config()


def save_config(config: Config) -> None:
    """Save configuration to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump(asdict(config), f, indent=2)


def load_env_keys(config: Config) -> Config:
    """Load API keys from environment variables if not already set."""
    if not config.gemini_api_key:
        config.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    if not config.openai_api_key:
        config.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    if not config.mistral_api_key:
        config.mistral_api_key = os.environ.get("MISTRAL_API_KEY", "")
    return config
