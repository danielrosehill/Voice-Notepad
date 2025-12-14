# Voice Notepad

[![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://github.com/danielrosehill/Voice-Notepad/releases)
[![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://github.com/danielrosehill/Voice-Notepad/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

**Download:** [AppImage](https://github.com/danielrosehill/Voice-Notepad/releases) • [Windows EXE](https://github.com/danielrosehill/Voice-Notepad/releases) • [Debian .deb](https://github.com/danielrosehill/Voice-Notepad/releases) • [Tarball](https://github.com/danielrosehill/Voice-Notepad/releases)

---

![Voice Notepad](screenshots/1_3_0/composite-1.png)

## Why Voice Notepad?

Most voice-to-text apps use a two-step process: first transcribe with ASR, then clean up with an LLM. Voice Notepad takes a different approach—it sends your audio directly to **multimodal AI models** that can hear and transcribe in a single pass.

**Why does this matter?**

- **Context-aware cleanup**: The AI "hears" your tone, pauses, and emphasis—not just raw text
- **Verbal editing works**: Say "scratch that" or "new paragraph" and the model understands
- **Faster turnaround**: One API call instead of two
- **Lower cost**: No separate ASR charges

This is a focused tool for the growing category of audio-capable multimodal models. If you want complex prompt engineering or traditional ASR pipelines, look elsewhere. If you want clean transcripts from your voice with minimal friction, this is it.

## Supported Providers & Models

| Provider | Models | Notes |
|----------|--------|-------|
| **OpenRouter** *(recommended)* | `google/gemini-2.5-flash`, `google/gemini-2.5-flash-lite`, `google/gemini-2.0-flash-001`, `openai/gpt-4o-audio-preview`, `mistralai/voxtral-small-24b-2507` | Single API key for all models, accurate cost tracking |
| **Google Gemini** | `gemini-flash-latest`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.5-pro` | Direct API access |
| **OpenAI** | `gpt-4o-audio-preview`, `gpt-4o-mini-audio-preview` | GPT-4o with native audio |
| **Mistral** | `voxtral-small-latest`, `voxtral-mini-latest` | Voxtral speech models |

OpenRouter is recommended because it gives you access to multiple providers through one API key, plus accurate per-key cost tracking.

## Features

- **One-shot transcription + cleanup**: Audio goes directly to multimodal models—no separate ASR step
- **Global hotkeys**: Record from anywhere, even when minimized (F14-F20 recommended for macro keys)
- **Voice Activity Detection**: Strips silence before upload to reduce costs
- **Automatic Gain Control**: Normalizes audio levels for consistent results
- **Cost tracking**: Monitor daily/weekly/monthly API spend (most accurate with OpenRouter)
- **Transcript history**: SQLite database stores all transcriptions with searchable metadata
- **Markdown output**: Clean, formatted text with optional source editing
- **Audio archival**: Optional Opus archival of recordings for reference

## Screenshots

![Record and History](screenshots/1_3_0/composite-1.png)
*Record tab and History tab*

![Cost and Analysis](screenshots/1_3_0/composite-2.png)
*Cost tracking and Analysis tabs*

## Installation

### Pre-built Packages

Download from [Releases](https://github.com/danielrosehill/Voice-Notepad/releases):
- **Linux**: AppImage (universal), .deb (Debian/Ubuntu), tarball
- **Windows**: Portable .exe

### From Source

```bash
git clone https://github.com/danielrosehill/Voice-Notepad.git
cd Voice-Notepad
./run.sh
```

The script creates a virtual environment and installs dependencies automatically.

## Configuration

Add your API key(s) via **Settings** in the app, or set environment variables:

```bash
OPENROUTER_API_KEY=your_key  # Recommended
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
MISTRAL_API_KEY=your_key
```

## Quick Start

1. Select your microphone and AI provider
2. Press **Record** (or `Ctrl+R`, or your global hotkey)
3. Speak naturally—say "new paragraph" or "scratch that" as needed
4. Press **Stop & Transcribe** (`Ctrl+Return`)
5. Copy or save your cleaned transcript

## Documentation

📖 **[User Manual (PDF)](docs/manuals/Voice-Notepad-User-Manual-v1.pdf)** — Full documentation including hotkey configuration, cost tracking details, and advanced settings.

## Related Resources

- [Audio-Multimodal-AI-Resources](https://github.com/danielrosehill/Audio-Multimodal-AI-Resources) — Curated list of audio-capable multimodal AI models
- [Audio-Understanding-Test-Prompts](https://github.com/danielrosehill/Audio-Understanding-Test-Prompts) — Test prompts for evaluating audio understanding

## License

MIT
