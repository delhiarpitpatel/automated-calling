"""
Speech-to-Text (STT) Module using Faster-Whisper

This module converts audio to text using OpenAI's Whisper model,
optimized via the faster-whisper library for CPU inference.

Performance Tuning for Low-End Hardware:
- Model: tiny.en (39M parameters) for fastest inference
- Quantization: int8 (32-bit → 8-bit) for 4x memory savings
- Beam Size: 1 (greedy decoding, no second-guessing)
- Language: Hard-coded to English (skips 500ms language detection)
- VAD: Disabled (we already did VAD with Silero)
- Threads: Pinned to physical core count for optimal cache behavior

Target Hardware: AMD APU (4 cores @ 2GHz)
Expected Latency: 300-500ms for 5-10 second audio clips
Memory Usage: ~200MB (int8) vs ~800MB (fp32)
"""

import logging

import numpy as np
from faster_whisper import WhisperModel

from src.core import config

logger = logging.getLogger(__name__)


class SpeechToText:
    """
    Speech-to-Text transcriber using Faster-Whisper (int8 quantized).

    Attributes:
        model: The loaded Whisper model instance
    """

    def __init__(self):
        """
        Load the Faster-Whisper STT model with CPU optimizations.

        Configuration:
        - device="cpu": Force CPU inference (no GPU/CUDA required)
        - compute_type="int8": 8-bit quantization for memory efficiency
        - cpu_threads: Pinned to physical core count (prevents oversubscription)
        - num_workers=1: Disable parallelization (prevents RAM bloat)

        The first load takes ~2-3 seconds and caches the model locally.
        Subsequent loads are instant.

        Raises:
            RuntimeError: If model download fails or device is unavailable
        """
        # Determine device to use for STT: prefer explicit STT_DEVICE if set
        # otherwise fall back to the repo-wide GPU_MODE (auto-detected)
        try:
            explicit_device = getattr(config, "STT_DEVICE", None)
            if explicit_device:
                device_to_use = explicit_device
            else:
                device_to_use = getattr(config, "GPU_MODE", "cpu")

            compute_type = getattr(config, "STT_COMPUTE_TYPE", "int8")

            logger.info(
                f"📝 Loading Faster-Whisper STT model: {config.STT_MODEL}"
                f" on device={device_to_use} compute_type={compute_type}"
            )

            self.model = WhisperModel(
                model_size_or_path=config.STT_MODEL,
                device=device_to_use,
                compute_type=compute_type,
                cpu_threads=config.STT_CPU_THREADS,
                num_workers=config.STT_NUM_WORKERS,
            )

            logger.info(f"✅ STT model loaded: {config.STT_MODEL} ({compute_type})")

        except Exception as e:
            logger.critical(f"❌ Failed to load STT model: {e}", exc_info=True)
            raise

    def transcribe(self, audio_array: np.ndarray) -> str:
        """
        Transcribe audio to text using greedy decoding.

        Args:
            audio_array: Numpy array of float32 audio samples at 16 kHz.
                        Typically the concatenated audio buffer from VAD.

        Returns:
            str: Transcribed text (trimmed and lowercased for consistency).

        Performance Tuning Explained:
        ============================
        - beam_size=1: Greedy decoding. Whisper explores only the most
          likely token at each step (instead of keeping top-K candidates).
          Massive speedup (~3x) with minimal accuracy loss for STT.

        - language="en": Hard-code to English, skip auto-detection.
          Language detection uses the full model on a sub-sample, adding
          500ms+ latency. Since we're a phone agent, we assume English.

        - condition_on_previous_text=False: Whisper sometimes hallucinates
          by trying to continue previous sentences. Disable this to prevent
          "So anyway, as I was saying..." artifacts.

        - vad_filter=False: We already ran Silero VAD upstream.
          Double-filtering is wasteful and may cause subtle artifacts.

        Raises:
            RuntimeError: If inference fails or audio is invalid
        """
        try:
            logger.debug(
                f"Transcribing {len(audio_array) / config.SAMPLE_RATE:.2f}s "
                f"of audio..."
            )

            segments, info = self.model.transcribe(
                audio_array,
                beam_size=1,
                language="en",
                condition_on_previous_text=False,
                vad_filter=False,
            )

            # Collect all segments into a single string
            text = " ".join([segment.text for segment in segments])
            text = text.strip()

            logger.info(f"✅ Transcription: '{text}'")

            return text

        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}", exc_info=True)
            raise
