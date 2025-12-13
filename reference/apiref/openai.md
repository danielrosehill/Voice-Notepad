# OpenAI Audio API Reference

## Documentation Links

- Models overview: https://platform.openai.com/docs/models
- Audio guide: https://platform.openai.com/docs/guides/audio
- GPT-4o Audio: https://platform.openai.com/docs/models/gpt-4o-audio-preview
- GPT-4o Mini Audio: https://platform.openai.com/docs/models/gpt-audio-mini

## Models

### GPT-4o Audio Preview (Full Featured)
- **Model ID**: `gpt-4o-audio-preview`
- **Description**: Full-featured audio model with speech understanding and generation
- **Use case**: High quality transcription with context understanding

### GPT-4o Mini Audio Preview (Cost Effective)
- **Model ID**: `gpt-4o-mini-audio-preview`
- **Description**: Smaller, cost-effective audio model
- **Use case**: Budget-friendly transcription tasks

## API Endpoint

```
POST https://api.openai.com/v1/chat/completions
```

## Request Structure (Audio Input)

```python
from openai import OpenAI
import base64

client = OpenAI(api_key="your-api-key")

# Read and encode audio
with open("audio.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Transcribe this audio"},
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_b64,
                        "format": "wav"  # or "mp3", "opus", etc.
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

## Audio Input Formats Supported
- `wav`
- `mp3`
- `opus`
- `flac`
- `webm`

## Audio Output (Optional)

For generating audio responses:

```python
response = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    modalities=["text", "audio"],
    audio={
        "voice": "alloy",  # alloy, echo, fable, onyx, nova, shimmer
        "format": "wav"    # wav, pcm16, opus
    },
    messages=[...]
)
```

## Key Differences from Whisper API

| Feature | GPT-4o Audio | Whisper API |
|---------|--------------|-------------|
| Endpoint | `/v1/chat/completions` | `/v1/audio/transcriptions` |
| Context | Full conversation context | Single audio file |
| Cleanup | Via prompt instructions | Raw transcription |
| Output | Text (+ optional audio) | Text only |

## Pricing (Approximate)
- Transcription: ~$1.55/hour of audio
- Audio generation: ~$5.93/hour of audio output
