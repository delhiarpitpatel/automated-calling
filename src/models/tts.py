"""
Text-to-Speech Module using Piper ONNX

This module synthesizes natural speech from text using the Piper TTS engine.
Piper is extremely lightweight (ONNX-based, no CUDA/GPU required) and outputs
22050 Hz mono audio, making it perfect for CPU-constrained environments.

Key Implementation Details:

1. Audio Format: Piper outputs 22050 Hz, 16-bit PCM mono audio
2. Upsampling: Some hardware (especially Bluetooth speakers) requires 44100 Hz
   To prevent audio drops, we use numpy.repeat() for 2x upsampling
3. Device Selection: Configurable output device via core.config
4. File I/O: We use temporary .wav files as the interface to Piper's API

Performance: Synthesis is real-time on CPU (sub-100ms for <10 second utterances)
"""

import asyncio
import logging
import os
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from piper import PiperVoice

from src.core import config

logger = logging.getLogger(__name__)


class TextToSpeech:
    """
    Text-to-Speech synthesizer using Piper ONNX models.

    Attributes:
        voice: The loaded Piper voice model
        model_path: Full path to the .onnx voice model file
        output_device: Audio output device ID (from config)
    """

    def __init__(self):
        """
        Load the Piper TTS model from disk.

        The model file should be in models/voices/ directory.
        Set VOICE_MODEL_NAME in .env to choose which voice to load.

        Raises:
            FileNotFoundError: If the model .onnx file doesn't exist
            RuntimeError: If Piper fails to load the model
        """
        logger.info("📢 Loading Piper TTS model (CPU optimized)...")

        try:
            # Construct the full model path
            model_path = (
                config.VOICE_MODEL_DIR / f"{config.VOICE_MODEL_NAME}.onnx"
            )

            if not model_path.exists():
                raise FileNotFoundError(
                    f"Voice model not found: {model_path}\n"
                    f"Download from: https://github.com/rhasspy/piper/releases\n"
                    f"Place .onnx and .json files in: {config.VOICE_MODEL_DIR}"
                )

            self.voice = PiperVoice.load(str(model_path))
            self.model_path = model_path
            self.output_device = config.OUTPUT_DEVICE

            logger.info(f"✅ TTS model loaded: {config.VOICE_MODEL_NAME}")

        except Exception as e:
            logger.critical(f"❌ Failed to load TTS model: {e}", exc_info=True)
            raise

    def speak(self, text: str):
        """
        Synthesize and play speech from text.

        Process:
        1. Create a temporary .wav file
        2. Feed the file handle to Piper (synchronous I/O)
        3. Read the synthesized audio back into memory
        4. Optionally upsample for Bluetooth compatibility
        5. Play through the configured audio device
        6. Clean up the temp file

        This is designed to be blocking (the agent waits for playback to finish)
        to prevent overlapping audio and maintain conversation flow.

        Args:
            text: The text to synthesize (plain English, no special chars)

        Raises:
            RuntimeError: If audio device is unavailable or playback fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS; skipping playback")
            return

        logger.debug(f"🔊 Synthesizing: '{text[:50]}...'")
        wav_path = Path(config.TTS_TEMP_FILE)

        try:
            # Step 1: Synthesize audio to a temporary WAV file
            with wave.open(str(wav_path), "wb") as wav_file:
                self.voice.synthesize_wav(text, wav_file)

            logger.debug(f"✅ Synthesized audio to {wav_path}")

            # Step 2: Read the synthesized audio from disk into memory
            with wave.open(str(wav_path), "rb") as wav_file:
                raw_data = wav_file.readframes(wav_file.getnframes())
                audio_array = np.frombuffer(raw_data, dtype=np.int16)

            logger.debug(
                f"Audio shape: {audio_array.shape}, "
                f"duration: {len(audio_array) / 22050:.2f}s"
            )

            # Step 3: Upsample if needed (Bluetooth fix)
            # ============================================
            # GLUE ENGINEERING: Bluetooth Audio Drop Fix
            #
            # Problem: Some Bluetooth speakers (especially boat rockers, gaming
            # headsets) expect 44100 Hz audio. Piper outputs 22050 Hz, causing
            # audio drops or stuttering when the device's buffer underruns.
            #
            # Solution: Use numpy.repeat() to 2x upsample before playback.
            # This is fast (<1ms) and preserves audio quality enough for TTS.
            #
            # Alternative: Could use scipy.signal.resample for higher quality,
            # but adds ~20ms latency which violates our sub-2s response target.
            # ============================================
            if config.UPSAMPLE_TTS_AUDIO:
                audio_array = np.repeat(audio_array, 2)
                output_sample_rate = config.TTS_OUTPUT_SAMPLE_RATE
                logger.debug(
                    f"Upsampled to {output_sample_rate}Hz "
                    f"(new shape: {audio_array.shape})"
                )
            else:
                output_sample_rate = 22050

            # Step 4: Play the audio
            logger.info(f"🔊 Playing audio (device={self.output_device})...")
            sd.play(
                audio_array,
                samplerate=output_sample_rate,
                device=self.output_device,
            )
            sd.wait()  # Block until playback finishes

            logger.info("✅ Audio playback complete")

        except (FileNotFoundError, OSError) as e:
            logger.error(f"❌ Audio device error: {e}", exc_info=True)
            raise RuntimeError(f"Audio playback failed: {e}") from e
        except Exception as e:
            logger.error(f"❌ TTS error: {e}", exc_info=True)
            raise
        finally:
            # Step 5: Clean up the temporary file
            if wav_path.exists():
                try:
                    wav_path.unlink()
                    logger.debug(f"🗑️  Cleaned up {wav_path}")
                except OSError as e:
                    logger.warning(f"⚠️  Failed to delete {wav_path}: {e}")
