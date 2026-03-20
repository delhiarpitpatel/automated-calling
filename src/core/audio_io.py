"""
Audio Input/Output Interface using sounddevice

This module handles real-time audio acquisition from the microphone and
playback to speakers using the sounddevice library (Python wrapper for
libsounddevice, which uses ALSA/PulseAudio on Linux).

Architecture:
- Non-blocking stream: Audio runs in a background C thread
- Async queue: Chunks are pushed to an asyncio queue from the callback
- Thread-safe: Uses loop.call_soon_threadsafe for thread-safe queueing
- Echo prevention: is_listening flag prevents recording while speaking

Key Challenge on Linux:
- Audio device IDs vary across distributions and hardware
- Run `python -m sounddevice` to discover your device IDs
- Set INPUT_DEVICE and OUTPUT_DEVICE in .env for portability

Callback Design:
- Runs in C thread (not the async event loop)
- Must be fast (<1ms) to avoid audio buffer underruns
- Uses call_soon_threadsafe to push to asyncio queue
- Ignores status errors gracefully (logs instead of crash)
"""

import asyncio
import logging
import sys
from typing import Optional

import numpy as np
import sounddevice as sd

from . import config

logger = logging.getLogger(__name__)


class AudioInterface:
    """
    Manages real-time audio input from microphone to asyncio queue.

    This uses sounddevice.InputStream with a callback to push audio chunks
    into an asyncio queue, bridging the gap between C-thread audio and
    Python's async event loop.

    Attributes:
        audio_queue: asyncio.Queue where audio chunks are pushed
        is_listening: Flag to enable/disable recording (prevents echo)
        is_speaking: Flag indicating if TTS is currently playing
        stream: The sounddevice InputStream (started in start_listening)
        loop: Reference to the asyncio event loop
    """

    def __init__(self):
        """Initialize the audio interface (doesn't start the stream yet)."""
        self.audio_queue: asyncio.Queue = asyncio.Queue()
        self.is_listening = True
        self.is_speaking = False
        self.stream: Optional[sd.InputStream] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def _mic_callback(
        self, indata: np.ndarray, frames: int, time, status: sd.CallbackFlags
    ):
        """
        Audio callback: Runs in background C thread.

        This is called by sounddevice every CHUNK_SIZE frames (~32ms).
        It must be extremely fast and non-blocking.

        Args:
            indata: Numpy array of raw audio samples (shape: (frames, channels))
            frames: Number of frames in the buffer
            time: Timing information (ignored for now)
            status: sounddevice.CallbackFlags (0 = OK, non-zero = error)

        Design Notes:
        - Flattens multi-channel audio to 1D (required by VAD)
        - Converts to float32 (required by Silero VAD)
        - Checks is_listening flag to prevent echo during playback
        - Uses call_soon_threadsafe to queue data safely from C thread
        """
        # Check for audio device errors (underruns, overruns, etc.)
        if status:
            logger.warning(f"Audio callback status: {status}", file=sys.stderr)

        # Only capture if listening AND not currently speaking
        # (prevents recording our own TTS output)
        if self.is_listening and not self.is_speaking:
            # Flatten from (frames, channels) to 1D array
            chunk = indata.flatten().astype(np.float32)

            # Push to asyncio queue from C thread (thread-safe)
            # call_soon_threadsafe is the only safe way to cross thread boundary
            try:
                self.loop.call_soon_threadsafe(
                    self.audio_queue.put_nowait, chunk
                )
            except RuntimeError as e:
                logger.error(f"Failed to queue audio chunk: {e}")

    def start_listening(self):
        """
        Start the microphone stream (non-blocking).

        This creates and starts a sounddevice.InputStream that continuously
        calls _mic_callback in a background thread. The callback pushes audio
        chunks into the asyncio queue for processing by the main loop.

        Device Selection:
        - If INPUT_DEVICE is None, sounddevice auto-selects the default device
        - To see available devices, run: python -m sounddevice

        Raises:
            RuntimeError: If the audio device is unavailable or init fails
        """
        try:
            # Store reference to the running event loop (needed in callback)
            self.loop = asyncio.get_running_loop()

            logger.info(
                f"Starting audio stream (device={config.INPUT_DEVICE}, "
                f"sample_rate={config.SAMPLE_RATE}Hz, "
                f"chunk_size={config.CHUNK_SIZE})"
            )

            self.stream = sd.InputStream(
                device=config.INPUT_DEVICE,
                samplerate=config.SAMPLE_RATE,
                channels=config.CHANNELS,
                dtype="float32",
                blocksize=config.CHUNK_SIZE,
                callback=self._mic_callback,
            )
            self.stream.start()
            logger.info("✅ Audio stream started")

        except (OSError, ValueError) as e:
            logger.critical(f"❌ Audio device error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize audio device: {e}") from e

    def stop_listening(self):
        """
        Stop the microphone stream and clean up resources.

        Safe to call multiple times; checks if stream exists before closing.
        """
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
                logger.info("✅ Audio stream stopped")
            except Exception as e:
                logger.error(f"Error closing audio stream: {e}")
            finally:
                self.stream = None
