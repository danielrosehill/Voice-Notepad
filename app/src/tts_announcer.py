"""TTS accessibility announcements for Voice Notepad V3.

Plays pre-generated voice announcements for status changes.
Uses British English male voice (en-GB-RyanNeural) via Edge TTS.
"""

import os
import threading
from pathlib import Path
from typing import Optional

# Try to use simpleaudio for playback (non-blocking, can load WAV files)
try:
    import simpleaudio as sa
    HAS_SIMPLEAUDIO = True
except ImportError:
    HAS_SIMPLEAUDIO = False

# Fallback to PyAudio if available
try:
    import pyaudio
    import wave
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False


def _get_assets_dir() -> Path:
    """Get the path to TTS assets directory.

    Handles both development (running from source) and installed scenarios.
    """
    # First, check relative to this source file (development)
    src_dir = Path(__file__).parent
    dev_assets = src_dir.parent / "assets" / "tts"
    if dev_assets.exists():
        return dev_assets

    # Check in installed location (alongside src)
    installed_assets = src_dir / "assets" / "tts"
    if installed_assets.exists():
        return installed_assets

    # Check in system-wide location
    system_assets = Path("/opt/voice-notepad/assets/tts")
    if system_assets.exists():
        return system_assets

    # Fallback to development path (may not exist)
    return dev_assets


class TTSAnnouncer:
    """Manages TTS accessibility announcements."""

    def __init__(self):
        self._enabled = False
        self._assets_dir = _get_assets_dir()
        self._audio_cache: dict[str, Optional[bytes]] = {}
        self._sample_rate = 16000  # WAV files are 16kHz

        # Pre-load all audio files
        self._preload_audio()

    def _preload_audio(self) -> None:
        """Pre-load all TTS audio files into memory."""
        announcements = [
            "recording", "stopped", "transcribing", "complete",
            "copied", "injected", "cleared", "cached", "error"
        ]

        for name in announcements:
            wav_path = self._assets_dir / f"{name}.wav"
            if wav_path.exists():
                try:
                    if HAS_SIMPLEAUDIO:
                        # Load as WaveObject for simpleaudio
                        self._audio_cache[name] = sa.WaveObject.from_wave_file(str(wav_path))
                    elif HAS_PYAUDIO:
                        # Read raw audio data for PyAudio
                        with wave.open(str(wav_path), 'rb') as wf:
                            self._audio_cache[name] = wf.readframes(wf.getnframes())
                    else:
                        self._audio_cache[name] = None
                except Exception:
                    self._audio_cache[name] = None
            else:
                self._audio_cache[name] = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    def _play_async(self, name: str) -> None:
        """Play an announcement in a background thread."""
        if not self._enabled:
            return

        audio = self._audio_cache.get(name)
        if audio is None:
            return

        thread = threading.Thread(target=self._play_audio, args=(name, audio), daemon=True)
        thread.start()

    def _play_audio(self, name: str, audio) -> None:
        """Play audio data."""
        if HAS_SIMPLEAUDIO and isinstance(audio, sa.WaveObject):
            try:
                play_obj = audio.play()
                play_obj.wait_done()
                return
            except Exception:
                pass

        if HAS_PYAUDIO and isinstance(audio, bytes):
            try:
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self._sample_rate,
                    output=True
                )
                stream.write(audio)
                stream.stop_stream()
                stream.close()
                p.terminate()
                return
            except Exception:
                pass

        # If no audio backend available, silently fail

    def announce_recording(self) -> None:
        """Announce: Recording started."""
        self._play_async("recording")

    def announce_stopped(self) -> None:
        """Announce: Recording stopped."""
        self._play_async("stopped")

    def announce_transcribing(self) -> None:
        """Announce: Transcription in progress."""
        self._play_async("transcribing")

    def announce_complete(self) -> None:
        """Announce: Transcription complete."""
        self._play_async("complete")

    def announce_copied(self) -> None:
        """Announce: Text copied to clipboard."""
        self._play_async("copied")

    def announce_injected(self) -> None:
        """Announce: Text injected at cursor."""
        self._play_async("injected")

    def announce_cleared(self) -> None:
        """Announce: Recording cleared/discarded."""
        self._play_async("cleared")

    def announce_cached(self) -> None:
        """Announce: Audio cached for append mode."""
        self._play_async("cached")

    def announce_error(self) -> None:
        """Announce: Error occurred."""
        self._play_async("error")


# Global singleton instance
_announcer: Optional[TTSAnnouncer] = None
_announcer_lock = threading.Lock()


def get_announcer() -> TTSAnnouncer:
    """Get the global TTSAnnouncer instance (thread-safe)."""
    global _announcer
    if _announcer is None:
        with _announcer_lock:
            # Double-check pattern for thread safety
            if _announcer is None:
                _announcer = TTSAnnouncer()
    return _announcer
