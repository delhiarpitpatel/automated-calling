"""Automated Calling - Local AI Voice Agent"""

__version__ = "1.0.0"
__author__ = "Arpit Patel"

from src.core.audio_io import AudioInterface
from src.core.config import *
from src.core.state_manager import StateManager
from .models.vad import VADetector
from .models.stt import SpeechToText
from .models.llm import LocalLLM
from .models.tts import TextToSpeech

__all__ = [
    "AudioInterface",
    "StateManager",
    "VADetector",
    "SpeechToText",
    "LocalLLM",
    "TextToSpeech",
]
