"""
Audio recorder module.
Captures audio from microphone using sounddevice.
"""

import io
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from typing import Optional
from threading import Thread, Event


class AudioRecorder:
    """Records audio from the microphone."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device_id: Optional[int] = None,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.device_id = device_id

        self._recording = False
        self._audio_data: list = []
        self._stop_event = Event()
        self._thread: Optional[Thread] = None

    def check_microphone(self) -> tuple[bool, str]:
        """
        Check if microphone is available by actually trying to open a stream.
        Returns: (is_available, error_message)
        """
        try:
            # Force refresh of audio devices
            sd._terminate()
            sd._initialize()

            # Actually try to open the stream briefly
            with sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
            ):
                pass  # If we get here, mic works

            return True, ""

        except sd.PortAudioError as e:
            error_str = str(e).lower()
            if "invalid" in error_str or "device" in error_str:
                return False, "No microphone found. Please connect one and try again."
            return False, f"Microphone error: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording

    def start(self) -> None:
        """Start recording audio."""
        if self._recording:
            return

        self._recording = True
        self._audio_data = []
        self._stop_event.clear()

        self._thread = Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop(self) -> bytes:
        """Stop recording and return WAV audio data as bytes."""
        if not self._recording:
            return b""

        self._recording = False
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

        return self._get_wav_bytes()

    def toggle(self) -> tuple[bool, Optional[bytes]]:
        """
        Toggle recording state.
        Returns: (is_now_recording, audio_data_if_stopped)
        """
        if self._recording:
            audio_data = self.stop()
            return False, audio_data
        else:
            self.start()
            return True, None

    def _record_loop(self) -> None:
        """Main recording loop."""
        try:
            with sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                blocksize=1024,
                callback=self._audio_callback,
            ):
                while not self._stop_event.is_set():
                    self._stop_event.wait(0.1)
        except Exception as e:
            print(f"Recording error: {e}")
            self._recording = False

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time_info, status
    ) -> None:
        """Callback for audio stream."""
        if status:
            print(f"Audio status: {status}")
        if self._recording:
            self._audio_data.append(indata.copy())

    def _get_wav_bytes(self) -> bytes:
        """Convert recorded audio to WAV bytes."""
        if not self._audio_data:
            return b""

        # Concatenate all audio chunks
        audio = np.concatenate(self._audio_data, axis=0)

        # Write to WAV bytes
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio)
        buffer.seek(0)
        return buffer.read()
