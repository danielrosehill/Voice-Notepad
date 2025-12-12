# Mistral Voxtral Audio API Reference

## Documentation Links

- Mistral Audio Guide: https://docs.mistral.ai/capabilities/audio/
- Voxtral Announcement: https://mistral.ai/news/voxtral
- Python SDK: https://github.com/mistralai/client-python

## Models

### Voxtral Small (Full Featured)
- **Model ID**: `voxtral-small-latest`
- **Description**: 24B parameter model for production-scale, enterprise use
- **Context**: 32k tokens (~30 min audio for transcription, ~40 min for understanding)
- **Use case**: High quality transcription with context understanding

### Voxtral Mini (Cost Effective)
- **Model ID**: `voxtral-mini-latest`
- **Description**: 3B parameter model optimized for edge devices
- **Context**: 32k tokens
- **Use case**: Budget-friendly transcription, local deployment

## API Endpoints

### Chat Completions with Audio (Used for cleanup prompts)

```
POST https://api.mistral.ai/v1/chat/completions
```

### Dedicated Transcription

```
POST https://api.mistral.ai/v1/audio/transcriptions
```

## Request Structure (Audio via Chat Completions)

```python
import base64
from mistralai import Mistral

client = Mistral(api_key="your-api-key")

# Read and encode audio as base64 (NOT a data URL)
with open("audio.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.complete(
    model="voxtral-mini-latest",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": audio_b64  # Raw base64 string
                },
                {
                    "type": "text",
                    "text": "Transcribe this audio"
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

## Request Structure (Dedicated Transcription)

```python
from mistralai import Mistral

client = Mistral(api_key="your-api-key")

with open("audio.mp3", "rb") as f:
    transcription = client.audio.transcriptions.complete(
        model="voxtral-mini-latest",
        file={
            "content": f,
            "file_name": "audio.mp3",
        },
        language="en",  # Optional, improves accuracy
        timestamp_granularities=["segment"]  # Optional
    )

print(transcription.text)
```

## Audio Input Formats Supported
- `wav`
- `mp3`
- `flac`
- `ogg`
- `webm`

## Key Differences from Chat vs Transcription API

| Feature | Chat Completions | Transcription API |
|---------|-----------------|-------------------|
| Endpoint | `/v1/chat/completions` | `/v1/audio/transcriptions` |
| Input Format | base64 in message | File upload |
| Custom Prompts | Yes | No |
| Timestamps | No | Yes (segment-level) |
| Use Case | Cleanup/processing | Raw transcription |

## Important Notes

1. **Audio format**: Pass raw base64 string to `input_audio`, NOT a data URL
2. **Order matters**: Put `input_audio` before `text` in the content array
3. **Model selection**: Use `voxtral-*` models for audio, not `mistral-small-latest`

## Pricing (Approximate)

- Voxtral Mini: $0.001/minute
- Voxtral Small: Higher tier pricing (check console)

## Sources

- [Mistral Audio & Transcription Docs](https://docs.mistral.ai/capabilities/audio/)
- [Voxtral Announcement](https://mistral.ai/news/voxtral)
- [Mistral Python SDK](https://github.com/mistralai/client-python)
