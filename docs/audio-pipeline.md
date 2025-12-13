# Audio Pipeline

Voice Notepad processes audio through several stages before sending it to AI models for transcription. This page documents the complete audio processing pipeline.

## Pipeline Overview

```mermaid
flowchart TD
    subgraph Recording
        A[🎤 Microphone Input] --> B[PyAudio Capture]
        B --> C[Raw WAV Buffer]
    end

    subgraph Processing
        C --> D{VAD Enabled?}
        D -->|Yes| E[Silero VAD]
        E --> F[Speech Segments Only]
        D -->|No| G[Full Audio]
        F --> H[Compression]
        G --> H
        H --> I[16kHz Mono WAV]
    end

    subgraph API
        I --> J[Base64 Encode]
        J --> K[Cleanup Prompt + Audio]
        K --> L[AI Model API]
        L --> M[Cleaned Transcript]
    end

    subgraph Storage
        C --> N{Archive Enabled?}
        N -->|Yes| O[Opus Encoder]
        O --> P[Audio Archive]
        M --> Q[SQLite Database]
    end
```

## Stage 1: Recording

Audio is captured using **PyAudio**, which provides cross-platform access to the system's audio input devices.

```mermaid
flowchart LR
    A[USB/Built-in Mic] --> B[PipeWire/PulseAudio]
    B --> C[PyAudio Stream]
    C --> D[WAV Buffer]

    style A fill:#e1f5fe
    style D fill:#c8e6c9
```

**Configuration:**
- Sample rate: System default (typically 44.1kHz or 48kHz)
- Channels: Mono or Stereo (depends on device)
- Format: 16-bit PCM

## Stage 2: Voice Activity Detection (VAD)

When enabled, **Silero VAD** detects speech segments and removes silence.

```mermaid
flowchart TD
    A[Raw Audio] --> B[Convert to 16kHz Mono]
    B --> C[Split into 32ms Windows]
    C --> D[ONNX Inference]
    D --> E{Speech Probability > 0.5?}
    E -->|Yes| F[Mark as Speech]
    E -->|No| G[Mark as Silence]
    F --> H[Collect Speech Segments]
    G --> H
    H --> I[Concatenate Speech Only]
    I --> J[Processed Audio]

    style D fill:#fff3e0
    style J fill:#c8e6c9
```

**VAD Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Sample Rate | 16kHz | Silero VAD requirement |
| Window Size | 512 samples (~32ms) | Analysis chunk size |
| Threshold | 0.5 | Speech probability cutoff |
| Min Speech | 250ms | Minimum segment duration |
| Min Silence | 100ms | Silence gap to remove |
| Padding | 30ms | Buffer around speech |

**Benefits:**
- Reduces audio file size (often 30-50% smaller)
- Lowers API costs (fewer audio tokens)
- Faster upload times

## Stage 3: Compression

Audio is compressed to **16kHz mono** before API submission.

```mermaid
flowchart LR
    A[Input Audio] --> B{Sample Rate?}
    B -->|>16kHz| C[Downsample to 16kHz]
    B -->|16kHz| D[Pass Through]
    C --> E{Channels?}
    D --> E
    E -->|Stereo| F[Convert to Mono]
    E -->|Mono| G[Pass Through]
    F --> H[16kHz Mono WAV]
    G --> H

    style H fill:#c8e6c9
```

**Why 16kHz Mono?**

- Gemini internally downsamples to 16kHz mono
- Reduces file size by ~66% compared to 48kHz stereo
- No quality loss for speech transcription
- Consistent results regardless of input format

**Size Comparison:**

| Format | Size per Minute |
|--------|-----------------|
| 48kHz Stereo | ~11 MB |
| 16kHz Mono | ~1.9 MB |
| With VAD (~50% speech) | ~1 MB |

## Stage 4: API Submission

The processed audio is sent to AI models with a cleanup prompt.

```mermaid
flowchart TD
    subgraph Request
        A[16kHz Mono WAV] --> B[Base64 Encode]
        C[Cleanup Prompt] --> D[Combine]
        B --> D
    end

    subgraph API Call
        D --> E{Provider}
        E -->|OpenRouter| F[OpenRouter API]
        E -->|Gemini| G[Google AI API]
        E -->|OpenAI| H[OpenAI API]
        E -->|Mistral| I[Mistral API]
    end

    subgraph Response
        F --> J[Cleaned Transcript]
        G --> J
        H --> J
        I --> J
        J --> K[Token Usage]
        J --> L[Cost Data]
    end
```

**What Gets Sent:**

1. **Audio Data**: Base64-encoded 16kHz mono WAV
2. **Cleanup Prompt**: Instructions for transcription and formatting

**What Comes Back:**

1. **Transcript**: Cleaned, formatted text (markdown)
2. **Token Counts**: Input/output tokens for cost tracking
3. **Cost** (OpenRouter): Actual cost for the request

## Stage 5: Storage

Transcripts are saved to a local SQLite database, with optional audio archival.

```mermaid
flowchart TD
    subgraph Transcript Storage
        A[Transcript Text] --> B[SQLite Database]
        C[Token Usage] --> B
        D[Cost Data] --> B
        E[Metadata] --> B
    end

    subgraph Audio Archive
        F[Original Audio] --> G{Archive Enabled?}
        G -->|Yes| H[Convert to Opus]
        H --> I[~24kbps VoIP]
        I --> J[Audio Archive Folder]
        G -->|No| K[Discard]
    end

    style B fill:#e3f2fd
    style J fill:#fff3e0
```

**Database Fields:**
- Timestamp
- Provider and model
- Transcript text
- Audio duration (original and post-VAD)
- Token counts
- Estimated/actual cost
- Archive file path (if enabled)

**Audio Archive Format:**
- Codec: Opus
- Bitrate: ~24kbps
- Mode: VoIP (speech-optimized)
- Size: ~180KB per minute

## Complete Pipeline Timing

```mermaid
gantt
    title Audio Processing Timeline (30-second recording)
    dateFormat X
    axisFormat %Ls

    section Recording
    Capture Audio :a1, 0, 30000

    section Processing
    VAD Analysis :a2, 30000, 31000
    Compression :a3, 31000, 31500

    section API
    Base64 Encode :a4, 31500, 31600
    API Request :a5, 31600, 33500

    section Storage
    Database Write :a6, 33500, 33600
    Archive (optional) :a7, 33500, 34000
```

**Typical Latency:**

| Stage | Duration |
|-------|----------|
| VAD Processing | ~500-1000ms |
| Compression | ~100-500ms |
| API Round-trip | ~1500-3000ms |
| Total | ~2-4 seconds |

## Configuration Options

All pipeline options are configurable in **Settings > Behavior**:

| Option | Default | Description |
|--------|---------|-------------|
| Enable VAD | On | Remove silence before upload |
| Archive Audio | Off | Save Opus copy of recordings |

See [Configuration](configuration.md) for details.
