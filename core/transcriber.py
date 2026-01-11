"""
Speech-to-Text transcriber using Groq API (Whisper).
"""

import io
import warnings
from typing import Optional

# Suppress httpx deprecation warning (groq dependency issue)
warnings.filterwarnings("ignore", message="URL.raw is deprecated")

from groq import Groq


class Transcriber:
    """Transcribes audio to text using Groq's Whisper API."""

    # Prompts to guide punctuation style (in target language)
    PUNCTUATION_PROMPTS = {
        "it": "Ciao, come stai? Bene, grazie. Oggi il tempo è bello, ma domani pioverà.",
        "en": "Hello, how are you? Fine, thanks. Today the weather is nice, but tomorrow it will rain.",
        "es": "Hola, ¿cómo estás? Bien, gracias. Hoy el tiempo es bueno, pero mañana lloverá.",
        "fr": "Bonjour, comment allez-vous? Bien, merci. Aujourd'hui il fait beau, mais demain il pleuvra.",
        "de": "Hallo, wie geht es dir? Gut, danke. Heute ist das Wetter schön, aber morgen wird es regnen.",
    }

    def __init__(self, api_key: str, language: str = "it"):
        """
        Initialize transcriber.

        Args:
            api_key: Groq API key
            language: Language code (it, en, es, fr, de)
        """
        self.client = Groq(api_key=api_key)
        self.language = language
        self.model = "whisper-large-v3"

    def set_language(self, language: str) -> None:
        """Change transcription language."""
        self.language = language

    def _get_prompt(self) -> str:
        """Get punctuation prompt for current language."""
        return self.PUNCTUATION_PROMPTS.get(self.language, self.PUNCTUATION_PROMPTS["en"])

    def transcribe(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio bytes to text.

        Args:
            audio_data: WAV audio data as bytes

        Returns:
            Transcribed text or None if failed
        """
        if not audio_data:
            return None

        try:
            # Create a file-like object from bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "recording.wav"

            # Call Groq API with punctuation prompt
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.model,
                language=self.language,
                prompt=self._get_prompt(),
                response_format="text",
            )

            return transcription.strip() if transcription else None

        except Exception as e:
            print(f"Transcription error: {e}")
            return None

