"""Unified Settings widget combining all configuration options."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QLineEdit, QCheckBox, QComboBox, QGroupBox, QFormLayout,
    QPushButton, QSpinBox, QFrame, QMessageBox, QFileDialog,
    QTextEdit, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .config import (
    Config, save_config, load_env_keys,
    GEMINI_MODELS, OPENAI_MODELS, MISTRAL_MODELS, OPENROUTER_MODELS,
)
from .formats_widget import FormatsWidget
from .mic_test_widget import MicTestWidget


class APIKeysWidget(QWidget):
    """API Keys configuration section."""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("API Keys")
        title.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "Configure API keys for transcription providers. "
            "OpenRouter is recommended as it provides access to multiple models through a single API key."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 12px;")
        layout.addWidget(desc)

        # API Keys form
        api_form = QFormLayout()
        api_form.setSpacing(12)
        api_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # OpenRouter
        self.openrouter_key = QLineEdit()
        self.openrouter_key.setText(self.config.openrouter_api_key)
        self.openrouter_key.setPlaceholderText("sk-or-v1-...")
        self.openrouter_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openrouter_key.textChanged.connect(lambda: self._save_key("openrouter_api_key", self.openrouter_key.text()))

        or_layout = QVBoxLayout()
        or_layout.addWidget(self.openrouter_key)
        or_help = QLabel("Recommended: Access Gemini, GPT-4o, and Voxtral models")
        or_help.setStyleSheet("color: #28a745; font-size: 10px; margin-left: 2px;")
        or_layout.addWidget(or_help)
        api_form.addRow("OpenRouter API Key:", or_layout)

        # Gemini
        self.gemini_key = QLineEdit()
        self.gemini_key.setText(self.config.gemini_api_key)
        self.gemini_key.setPlaceholderText("AI...")
        self.gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_key.textChanged.connect(lambda: self._save_key("gemini_api_key", self.gemini_key.text()))
        api_form.addRow("Gemini API Key:", self.gemini_key)

        # OpenAI
        self.openai_key = QLineEdit()
        self.openai_key.setText(self.config.openai_api_key)
        self.openai_key.setPlaceholderText("sk-...")
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.textChanged.connect(lambda: self._save_key("openai_api_key", self.openai_key.text()))
        api_form.addRow("OpenAI API Key:", self.openai_key)

        # Mistral
        self.mistral_key = QLineEdit()
        self.mistral_key.setText(self.config.mistral_api_key)
        self.mistral_key.setPlaceholderText("...")
        self.mistral_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.mistral_key.textChanged.connect(lambda: self._save_key("mistral_api_key", self.mistral_key.text()))
        api_form.addRow("Mistral API Key:", self.mistral_key)

        layout.addLayout(api_form)

        # Available models section
        models_group = QGroupBox("Available Models by Provider")
        models_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ced4da;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
        """)
        models_layout = QVBoxLayout(models_group)
        models_layout.setSpacing(8)

        # OpenRouter models
        or_models = [name for _, name in OPENROUTER_MODELS]
        or_label = QLabel("<b>OpenRouter:</b> " + ", ".join(or_models))
        or_label.setWordWrap(True)
        or_label.setStyleSheet("padding: 4px;")
        models_layout.addWidget(or_label)

        # Gemini models
        gem_models = [name for _, name in GEMINI_MODELS]
        gem_label = QLabel("<b>Gemini:</b> " + ", ".join(gem_models))
        gem_label.setWordWrap(True)
        gem_label.setStyleSheet("padding: 4px;")
        models_layout.addWidget(gem_label)

        # OpenAI models
        oai_models = [name for _, name in OPENAI_MODELS]
        oai_label = QLabel("<b>OpenAI:</b> " + ", ".join(oai_models))
        oai_label.setWordWrap(True)
        oai_label.setStyleSheet("padding: 4px;")
        models_layout.addWidget(oai_label)

        # Mistral models
        mis_models = [name for _, name in MISTRAL_MODELS]
        mis_label = QLabel("<b>Mistral:</b> " + ", ".join(mis_models))
        mis_label.setWordWrap(True)
        mis_label.setStyleSheet("padding: 4px;")
        models_layout.addWidget(mis_label)

        layout.addWidget(models_group)
        layout.addStretch()

    def _save_key(self, key_name: str, value: str):
        """Save API key to config."""
        setattr(self.config, key_name, value)
        save_config(self.config)


class AudioMicWidget(QWidget):
    """Audio device and microphone testing section."""

    def __init__(self, config: Config, recorder, parent=None):
        super().__init__(parent)
        self.config = config
        self.recorder = recorder
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("Audio & Microphone")
        title.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Audio device selection
        device_group = QGroupBox("Input Device")
        device_layout = QFormLayout(device_group)
        device_layout.setSpacing(12)

        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        self._populate_devices()

        device_row = QHBoxLayout()
        device_row.addWidget(self.device_combo, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self._populate_devices)
        device_row.addWidget(refresh_btn)

        device_layout.addRow("Microphone:", device_row)
        layout.addWidget(device_group)

        # Integrated Mic Test
        mic_test_title = QLabel("Microphone Test")
        mic_test_title.setFont(QFont("Sans", 13, QFont.Weight.Bold))
        mic_test_title.setStyleSheet("margin-top: 12px;")
        layout.addWidget(mic_test_title)

        self.mic_test_widget = MicTestWidget()
        layout.addWidget(self.mic_test_widget)

        layout.addStretch()

    def _populate_devices(self):
        """Populate device dropdown."""
        self.device_combo.clear()
        self.device_combo.addItem("Default", None)

        devices = self.recorder.get_input_devices()
        for idx, name in devices:
            self.device_combo.addItem(name, idx)
            if idx == self.config.audio_device_index:
                self.device_combo.setCurrentIndex(self.device_combo.count() - 1)

    def _on_device_changed(self):
        """Handle device selection change."""
        self.config.audio_device_index = self.device_combo.currentData()
        save_config(self.config)
        if self.config.audio_device_index is not None:
            self.recorder.set_device(self.config.audio_device_index)


class BehaviorWidget(QWidget):
    """Behavior settings section."""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("Behavior Settings")
        title.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Form layout for settings
        form = QFormLayout()
        form.setSpacing(12)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # VAD
        self.vad_enabled = QCheckBox()
        self.vad_enabled.setChecked(self.config.vad_enabled)
        self.vad_enabled.toggled.connect(lambda v: self._save_bool("vad_enabled", v))
        vad_layout = QVBoxLayout()
        vad_layout.addWidget(self.vad_enabled)
        vad_help = QLabel("Removes silence before transcription (reduces cost)")
        vad_help.setStyleSheet("color: #666; font-size: 10px;")
        vad_layout.addWidget(vad_help)
        form.addRow("Enable VAD:", vad_layout)

        # AGC info (always enabled, not configurable)
        agc_info = QLabel("✓ Automatic Gain Control (AGC) is always enabled to normalize audio levels")
        agc_info.setWordWrap(True)
        agc_info.setStyleSheet("color: #28a745; font-size: 11px; margin: 8px 0;")
        form.addRow("", agc_info)

        # Audio archival
        self.store_audio = QCheckBox()
        self.store_audio.setChecked(self.config.store_audio)
        self.store_audio.toggled.connect(lambda v: self._save_bool("store_audio", v))
        archive_layout = QVBoxLayout()
        archive_layout.addWidget(self.store_audio)
        archive_help = QLabel("Save audio recordings in Opus format (~24kbps)")
        archive_help.setStyleSheet("color: #666; font-size: 10px;")
        archive_layout.addWidget(archive_help)
        form.addRow("Archive Audio:", archive_layout)

        # Beep on recording
        self.beep_on_record = QCheckBox()
        self.beep_on_record.setChecked(self.config.beep_on_record)
        self.beep_on_record.toggled.connect(lambda v: self._save_bool("beep_on_record", v))
        form.addRow("Beep on recording start/stop:", self.beep_on_record)

        # Beep on clipboard
        self.beep_on_clipboard = QCheckBox()
        self.beep_on_clipboard.setChecked(self.config.beep_on_clipboard)
        self.beep_on_clipboard.toggled.connect(lambda v: self._save_bool("beep_on_clipboard", v))
        form.addRow("Beep on clipboard copy:", self.beep_on_clipboard)

        layout.addLayout(form)
        layout.addStretch()

    def _save_bool(self, key: str, value: bool):
        """Save boolean config value."""
        setattr(self.config, key, value)
        save_config(self.config)


class PersonalizationWidget(QWidget):
    """Personalization settings section."""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("Personalization")
        title.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel("Customize how the AI addresses you in transcriptions.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 12px;")
        layout.addWidget(desc)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.config.user_name)
        self.name_edit.setPlaceholderText("Your name")
        self.name_edit.textChanged.connect(lambda: self._save_str("user_name", self.name_edit.text()))
        form.addRow("Name:", self.name_edit)

        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setText(self.config.user_email)
        self.email_edit.setPlaceholderText("your.email@example.com")
        self.email_edit.textChanged.connect(lambda: self._save_str("user_email", self.email_edit.text()))
        form.addRow("Email:", self.email_edit)

        # Sign-off
        self.signoff_edit = QLineEdit()
        self.signoff_edit.setText(self.config.email_signature)
        self.signoff_edit.setPlaceholderText("Best regards")
        self.signoff_edit.textChanged.connect(lambda: self._save_str("email_signature", self.signoff_edit.text()))
        form.addRow("Email Sign-off:", self.signoff_edit)

        layout.addLayout(form)
        layout.addStretch()

    def _save_str(self, key: str, value: str):
        """Save string config value."""
        setattr(self.config, key, value)
        save_config(self.config)


class HotkeysWidget(QWidget):
    """Hotkeys configuration section."""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("Global Hotkeys")
        title.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "Global hotkeys are currently fixed to F15-F19. "
            "Customizable hotkeys will be available in a future release."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 12px;")
        layout.addWidget(desc)

        # Hotkey reference
        ref_group = QGroupBox("Fixed Hotkey Mapping")
        ref_layout = QFormLayout(ref_group)
        ref_layout.setSpacing(8)

        hotkeys = [
            ("F15", "Toggle Recording"),
            ("F16", "Tap (same as F15)"),
            ("F17", "Transcribe Only"),
            ("F18", "Clear/Delete"),
            ("F19", "Append"),
        ]

        for key, action in hotkeys:
            key_label = QLabel(f"<b>{key}</b>")
            action_label = QLabel(action)
            action_label.setStyleSheet("color: #666;")
            ref_layout.addRow(key_label, action_label)

        layout.addWidget(ref_group)
        layout.addStretch()


class DatabaseWidget(QWidget):
    """Database management section."""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("Database Management")
        title.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel("Manage your transcription history and local data.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 12px;")
        layout.addWidget(desc)

        # Database info
        info_group = QGroupBox("Database Location")
        info_layout = QVBoxLayout(info_group)

        from pathlib import Path
        config_dir = Path.home() / ".config" / "voice-notepad-v3"

        path_label = QLabel(str(config_dir / "mongita"))
        path_label.setStyleSheet("font-family: monospace; color: #495057; padding: 8px;")
        path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addWidget(path_label)

        layout.addWidget(info_group)

        # Management actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(8)

        # Export button
        export_btn = QPushButton("Export Database")
        export_btn.setToolTip("Export all transcriptions to JSON")
        export_btn.clicked.connect(self._export_database)
        actions_layout.addWidget(export_btn)

        # Clear history button
        clear_btn = QPushButton("Clear All History")
        clear_btn.setToolTip("Delete all transcription history")
        clear_btn.setStyleSheet("background-color: #dc3545; color: white;")
        clear_btn.clicked.connect(self._clear_history)
        actions_layout.addWidget(clear_btn)

        layout.addWidget(actions_group)
        layout.addStretch()

    def _export_database(self):
        """Export database to JSON."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Database",
            "voice-notepad-export.json",
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                from .database_mongo import get_db
                import json

                db = get_db()
                transcriptions = list(db["transcriptions"].find({}))

                # Convert ObjectId to string
                for t in transcriptions:
                    if "_id" in t:
                        t["_id"] = str(t["_id"])

                with open(file_path, "w") as f:
                    json.dump(transcriptions, f, indent=2, default=str)

                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Exported {len(transcriptions)} transcriptions to {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Error: {e}")

    def _clear_history(self):
        """Clear all transcription history."""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to delete all transcription history? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                from .database_mongo import get_db
                db = get_db()
                result = db["transcriptions"].delete_many({})
                QMessageBox.information(
                    self,
                    "History Cleared",
                    f"Deleted {result.deleted_count} transcriptions."
                )
            except Exception as e:
                QMessageBox.critical(self, "Clear Failed", f"Error: {e}")


class SettingsWidget(QWidget):
    """Unified settings widget with tabbed sections."""

    def __init__(self, config: Config, recorder, parent=None):
        super().__init__(parent)
        self.config = config
        self.recorder = recorder
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create tab widget for settings sections
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Add sections as tabs
        self.tabs.addTab(APIKeysWidget(self.config), "API Keys")
        self.tabs.addTab(AudioMicWidget(self.config, self.recorder), "Audio & Mic")
        self.tabs.addTab(FormatsWidget(self.config), "Output Formats")
        self.tabs.addTab(BehaviorWidget(self.config), "Behavior")
        self.tabs.addTab(PersonalizationWidget(self.config), "Personalization")
        self.tabs.addTab(HotkeysWidget(self.config), "Hotkeys")
        self.tabs.addTab(DatabaseWidget(self.config), "Database")

        layout.addWidget(self.tabs)

    def refresh(self):
        """Refresh all sub-widgets."""
        # Refresh formats widget specifically
        formats_widget = self.tabs.widget(2)  # Output Formats tab
        if hasattr(formats_widget, 'refresh'):
            formats_widget.refresh()
