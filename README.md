# Voice Notepad V3

A PyQt6 desktop application for voice recording with AI-powered transcription and cleanup. Uses multimodal AI models (Gemini, OpenAI GPT-4o, Mistral Voxtral) to transcribe audio AND clean it up in a single pass.

## Features

- **One-shot transcription + cleanup**: Audio is sent with a cleanup prompt to multimodal models, eliminating the need for separate ASR and LLM passes
- **Multiple AI providers**: Gemini, OpenAI, and Mistral (Voxtral)
- **Audio compression**: Automatic downsampling to 16kHz mono before upload (reduces file size, matches Gemini's internal format)
- **Markdown rendering**: Transcriptions display with rendered markdown formatting (toggle to view/edit source)
- **System tray integration**: Minimizes to tray for quick access
- **Microphone selection**: Choose your preferred input device
- **Recording controls**: Record, pause, resume, stop, delete
- **Save & copy**: Save to markdown files or copy to clipboard
- **Word count**: Live word and character count
- **Keyboard shortcuts**: Full keyboard control for efficient workflow
- **Local configuration**: Settings stored in `~/.config/voice-notepad-v3/`

## Installation

```bash
# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Configuration

### API Keys

Set your API keys either:

1. **Environment variables** (or `.env` file):
   ```
   GEMINI_API_KEY=your_key
   OPENAI_API_KEY=your_key
   MISTRAL_API_KEY=your_key
   ```

2. **Settings dialog**: Click "Settings" in the app to configure API keys

### Models

Default models:
- **Gemini**: `gemini-2.0-flash-lite`
- **OpenAI**: `gpt-4o-audio-preview`
- **Mistral**: `mistral-small-latest`

These can be changed in Settings > Models.

## Usage

```bash
./run.sh
# or
source .venv/bin/activate
python -m src.main
```

1. Select your microphone and AI provider
2. Click **Record** to start recording (or press `Ctrl+R`)
3. Click **Stop & Transcribe** when done (or press `Ctrl+Return`)
4. The cleaned transcription appears with markdown formatting
5. Click **Save** to export or **Copy** to clipboard

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Start recording |
| `Ctrl+Space` | Pause/Resume recording |
| `Ctrl+Return` | Stop and transcribe |
| `Ctrl+S` | Save to file |
| `Ctrl+Shift+C` | Copy to clipboard |
| `Ctrl+N` | New note |

### System Tray

- Closing the window minimizes to system tray
- Click the tray icon to show/hide the window
- Right-click for quick actions (Show, Start Recording, Quit)

## Cleanup Prompt

The default cleanup prompt instructs the AI to:
- Remove filler words (um, uh, like, etc.)
- Add proper punctuation and sentences
- Add natural paragraph spacing
- Follow verbal instructions in the recording
- Add subheadings for lengthy transcriptions
- Return output as markdown

Customize the prompt in Settings > Prompt.

## Project Structure

```
Voice-Notepad-V3/
├── src/                    # Source code
│   ├── main.py            # Main application
│   ├── audio_recorder.py  # Audio recording
│   ├── audio_processor.py # Audio compression
│   ├── transcription.py   # API clients
│   ├── markdown_widget.py # Markdown display
│   └── config.py          # Configuration
├── docs/                   # Documentation
│   ├── apiref/            # API reference docs
│   ├── idea-notes/        # Planning notes
│   └── screenshots/       # Screenshots
├── requirements.txt
├── run.sh
└── README.md
```

## Requirements

- Python 3.10+
- PyQt6
- PyAudio (requires system audio libraries)
- ffmpeg (for audio processing via pydub)
- API keys for your chosen provider(s)

## License

MIT
