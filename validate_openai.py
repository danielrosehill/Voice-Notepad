#!/usr/bin/env python3
"""Validate OpenAI audio backend connectivity and transcription."""

import os
import sys
import base64
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load .env file manually
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def create_test_audio() -> bytes:
    """Create a short test WAV audio with a tone."""
    import wave
    import struct
    import math
    import io

    sample_rate = 16000
    duration = 1.0  # 1 second
    frequency = 440  # A4 note

    num_samples = int(sample_rate * duration)

    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        for i in range(num_samples):
            value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            wav.writeframes(struct.pack('<h', value))

    buffer.seek(0)
    return buffer.read()


def validate_openai_backend():
    """Test OpenAI audio API connectivity."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment")
        return False

    print(f"API key found: {api_key[:20]}...")

    try:
        from openai import OpenAI
        print("OpenAI SDK imported successfully")
    except ImportError as e:
        print(f"ERROR: Failed to import OpenAI SDK: {e}")
        return False

    client = OpenAI(api_key=api_key)
    print("OpenAI client initialized")

    # Test 1: Simple API connectivity with a text request
    print("\n--- Test 1: API connectivity (text completion) ---")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API connection successful' and nothing else."}],
            max_tokens=20
        )
        print(f"Response: {response.choices[0].message.content}")
        print("Text API: OK")
    except Exception as e:
        print(f"ERROR: Text API failed: {e}")
        return False

    # Test 2: Audio model availability
    print("\n--- Test 2: Audio model test (gpt-4o-audio-preview) ---")
    try:
        # Create a short test audio
        audio_data = create_test_audio()
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o-audio-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe what you hear in this audio. If it's just a tone, say 'I hear a tone'."},
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_b64,
                                "format": "wav"
                            }
                        }
                    ]
                }
            ]
        )
        print(f"Response: {response.choices[0].message.content}")
        print("Audio model (gpt-4o-audio-preview): OK")
    except Exception as e:
        print(f"ERROR: Audio model failed: {e}")
        print("This could be a model availability issue or API permissions")
        return False

    # Test 3: Test with real audio file if available
    print("\n--- Test 3: Real audio file test ---")
    test_audio_path = Path(__file__).parent / "planning" / "idea-notes" / "idea.mp3"

    if test_audio_path.exists():
        print(f"Found test file: {test_audio_path}")
        try:
            # Read first 30 seconds worth (approx) to avoid large requests
            with open(test_audio_path, "rb") as f:
                # Read first ~500KB of the MP3
                audio_data = f.read(500_000)

            audio_b64 = base64.b64encode(audio_data).decode("utf-8")

            response = client.chat.completions.create(
                model="gpt-4o-audio-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Transcribe the first few sentences of this audio."},
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": audio_b64,
                                    "format": "mp3"
                                }
                            }
                        ]
                    }
                ]
            )
            transcript = response.choices[0].message.content
            print(f"Transcription preview: {transcript[:200]}...")
            print("Real audio transcription: OK")
        except Exception as e:
            print(f"WARNING: Real audio test failed: {e}")
            print("(This is non-critical if Test 2 passed)")
    else:
        print(f"Test audio not found at {test_audio_path}, skipping")

    print("\n" + "=" * 50)
    print("OpenAI backend validation: PASSED")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = validate_openai_backend()
    sys.exit(0 if success else 1)
