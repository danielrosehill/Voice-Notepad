"""Models tab widget showing available AI models by provider."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QScrollArea,
    QFrame,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .config import GEMINI_MODELS, OPENAI_MODELS, MISTRAL_MODELS, OPENROUTER_MODELS


# Model metadata with additional notes
MODEL_INFO = {
    # Gemini models
    "gemini-flash-latest": {
        "note": "Dynamic endpoint - always points to the latest Flash model",
        "audio_support": True,
        "tier": "standard",
    },
    "gemini-2.5-flash": {
        "note": "Latest generation Flash model with improved capabilities",
        "audio_support": True,
        "tier": "standard",
    },
    "gemini-2.5-flash-lite": {
        "note": "Lighter version optimized for cost efficiency",
        "audio_support": True,
        "tier": "budget",
    },
    "gemini-2.5-pro": {
        "note": "Most capable Gemini model for complex tasks",
        "audio_support": True,
        "tier": "premium",
    },
    # OpenAI models
    "gpt-4o-audio-preview": {
        "note": "GPT-4o with native audio understanding",
        "audio_support": True,
        "tier": "standard",
    },
    "gpt-4o-mini-audio-preview": {
        "note": "Smaller, faster, more cost-effective version",
        "audio_support": True,
        "tier": "budget",
    },
    "gpt-audio": {
        "note": "Dedicated audio model",
        "audio_support": True,
        "tier": "standard",
    },
    "gpt-audio-mini": {
        "note": "Budget-friendly audio model",
        "audio_support": True,
        "tier": "budget",
    },
    # Mistral models
    "voxtral-small-latest": {
        "note": "Mistral's latest small audio model",
        "audio_support": True,
        "tier": "standard",
    },
    "voxtral-mini-latest": {
        "note": "Compact model optimized for efficiency",
        "audio_support": True,
        "tier": "budget",
    },
    # OpenRouter models
    "google/gemini-2.5-flash": {
        "note": "Latest Gemini Flash via OpenRouter",
        "audio_support": True,
        "tier": "standard",
    },
    "google/gemini-2.5-flash-lite": {
        "note": "Budget-friendly Gemini 2.5 Flash Lite",
        "audio_support": True,
        "tier": "budget",
    },
    "google/gemini-2.0-flash-001": {
        "note": "Gemini 2.0 Flash via OpenRouter",
        "audio_support": True,
        "tier": "standard",
    },
    "google/gemini-2.0-flash-lite-001": {
        "note": "Budget-friendly Gemini 2.0 Flash Lite",
        "audio_support": True,
        "tier": "budget",
    },
    "openai/gpt-4o-audio-preview": {
        "note": "GPT-4o with audio via OpenRouter",
        "audio_support": True,
        "tier": "premium",
    },
    "mistralai/voxtral-small-24b-2507": {
        "note": "Voxtral Small 24B via OpenRouter",
        "audio_support": True,
        "tier": "standard",
    },
}


class ModelsWidget(QWidget):
    """Widget showing available models grouped by provider."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        title = QLabel("Available Models")
        title.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        intro = QLabel(
            "Voice Notepad supports multimodal AI models that can process audio directly. "
            "Select your preferred provider and model in the Record tab."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 10px;")
        layout.addWidget(intro)

        # OpenRouter models (default provider)
        openrouter_group = self._create_provider_group(
            "OpenRouter (Recommended)",
            OPENROUTER_MODELS,
            "https://openrouter.ai/models?fmt=cards&input_modalities=audio",
            "Unified API for multiple providers. Access Gemini, GPT-4o, and Voxtral "
            "through a single API key. Flexible model switching without changing providers."
        )
        layout.addWidget(openrouter_group)

        # Gemini models
        gemini_group = self._create_provider_group(
            "Google Gemini",
            GEMINI_MODELS,
            "https://ai.google.dev/gemini-api/docs/models",
            "Multimodal models with native audio support. 'gemini-flash-latest' is a dynamic "
            "endpoint that always points to Google's latest Flash model."
        )
        layout.addWidget(gemini_group)

        # OpenAI models
        openai_group = self._create_provider_group(
            "OpenAI",
            OPENAI_MODELS,
            "https://platform.openai.com/docs/models",
            "GPT models with audio understanding capabilities via the Chat Completions API."
        )
        layout.addWidget(openai_group)

        # Mistral models
        mistral_group = self._create_provider_group(
            "Mistral AI",
            MISTRAL_MODELS,
            "https://docs.mistral.ai/capabilities/audio/",
            "Voxtral models designed for audio transcription and understanding."
        )
        layout.addWidget(mistral_group)

        # Tier legend
        legend_group = QGroupBox("Model Tiers")
        legend_layout = QVBoxLayout(legend_group)

        tiers = [
            ("Budget", "#28a745", "Lower cost, suitable for most transcription tasks"),
            ("Standard", "#007bff", "Balanced performance and cost"),
            ("Premium", "#6f42c1", "Highest capability, best for complex content"),
        ]

        for tier_name, color, description in tiers:
            tier_row = QHBoxLayout()
            tier_label = QLabel(f"<span style='color: {color}; font-weight: bold;'>{tier_name}</span>")
            tier_label.setFixedWidth(70)
            tier_row.addWidget(tier_label)
            tier_desc = QLabel(description)
            tier_desc.setStyleSheet("color: #666; font-size: 11px;")
            tier_row.addWidget(tier_desc)
            tier_row.addStretch()
            legend_layout.addLayout(tier_row)

        layout.addWidget(legend_group)

        # Note about dynamic endpoints
        note = QLabel(
            "<b>Note:</b> Dynamic endpoints (like 'gemini-flash-latest') automatically use "
            "the newest model version. This means capabilities and pricing may change over time."
        )
        note.setWordWrap(True)
        note.setStyleSheet(
            "background-color: #fff3cd; border: 1px solid #ffc107; "
            "border-radius: 4px; padding: 8px; font-size: 11px; margin-top: 10px;"
        )
        layout.addWidget(note)

        # Spacer
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_provider_group(
        self,
        provider_name: str,
        models: list,
        docs_url: str,
        description: str
    ) -> QGroupBox:
        """Create a group box for a provider's models."""
        group = QGroupBox(provider_name)
        group_layout = QVBoxLayout(group)

        # Provider description and docs link
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 11px;")
        group_layout.addWidget(desc_label)

        docs_link = QLabel(f'<a href="{docs_url}">Documentation</a>')
        docs_link.setOpenExternalLinks(True)
        docs_link.setStyleSheet("font-size: 10px; margin-bottom: 8px;")
        group_layout.addWidget(docs_link)

        # Models list
        for model_id, display_name in models:
            model_widget = self._create_model_entry(model_id, display_name)
            group_layout.addWidget(model_widget)

        return group

    def _create_model_entry(self, model_id: str, display_name: str) -> QWidget:
        """Create a widget for a single model entry."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        # Model name row
        name_row = QHBoxLayout()
        name_row.setSpacing(8)

        # Tier indicator
        info = MODEL_INFO.get(model_id, {})
        tier = info.get("tier", "standard")
        tier_colors = {
            "budget": "#28a745",
            "standard": "#007bff",
            "premium": "#6f42c1",
        }
        color = tier_colors.get(tier, "#007bff")

        tier_dot = QLabel("\u25cf")  # Unicode filled circle
        tier_dot.setStyleSheet(f"color: {color}; font-size: 10px;")
        tier_dot.setFixedWidth(12)
        name_row.addWidget(tier_dot)

        # Display name
        name_label = QLabel(f"<b>{display_name}</b>")
        name_row.addWidget(name_label)
        name_row.addStretch()

        layout.addLayout(name_row)

        # Model ID
        id_label = QLabel(f"<code style='color: #666;'>{model_id}</code>")
        id_label.setStyleSheet("font-size: 10px; margin-left: 20px;")
        layout.addWidget(id_label)

        # Note if available
        note = info.get("note", "")
        if note:
            note_label = QLabel(note)
            note_label.setStyleSheet("color: #888; font-size: 10px; margin-left: 20px;")
            note_label.setWordWrap(True)
            layout.addWidget(note_label)

        return widget
