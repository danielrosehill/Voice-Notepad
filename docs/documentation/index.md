# Voice Notepad Documentation

Voice Notepad is a desktop application that uses a dual-pipeline architecture for voice transcription: local preprocessing (VAD + AGC) combined with cloud-based multimodal AI transcription. See the [README](../README.md) for an overview and quick start guide.

## User Manual

- **[User Manual v3 (PDF)](manuals/Voice-Notepad-User-Manual-v3.pdf)** - Complete guide (v1.9.11) covering the dual-pipeline architecture

## Getting Started

- [Installation](installation.md) - Two-stage setup (system dependencies + application)
- [Configuration](configuration.md) - API keys and settings
- [Hotkey Setup](hotkey-setup.md) - Global hotkeys for hands-free operation
- [Text Injection Setup](text-injection.md) - Auto-paste on Wayland (ydotool)

## Reference

- [Shortcuts](shortcuts.md) - Keyboard shortcuts and global hotkeys
- [Models](models.md) - Available AI models by provider
- [Cost Tracking](cost-tracking.md) - Monitoring API spend
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## Technical

- [Audio Pipeline](audio-pipeline.md) - Local preprocessing (VAD, AGC, compression)
- [Prompt Concatenation](prompt-concatenation.md) - How cleanup instructions are built
- [Technology Stack](stack.md) - Libraries and dependencies
- [Multimodal vs ASR](multimodal-vs-asr.md) - Why this approach differs from traditional speech-to-text

## Archive

Previous documentation versions:

- [User Manual v2 (PDF)](manuals/Voice-Notepad-User-Manual-v2.pdf) - v1.8.0
- [User Manual v2 (Markdown)](manuals/user-manual-v2.md) - v1.8.0
- [User Manual v1 (PDF)](manuals/archive/Voice-Notepad-User-Manual-v1.pdf) - v1.3.0

## Screenshots

- [Screenshots](screenshots.md) - Application screenshots (v1.3.0, may be outdated)
