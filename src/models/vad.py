"""Voice Activity Detection (VAD) using Silero VAD.

This module detects when the user is speaking vs. silence using the Silero
VAD model. Silero is fast and well-suited for local inference. On modern
hardware we rely on PyTorch's normal logging; older FD-level hacks have been
removed for clarity and maintainability.

Key Features:
 - Real-time inference: typically a few milliseconds per 32ms audio chunk
 - Confidence scores (0.0-1.0) for tunable sensitivity
 - Supports running on CUDA if available (model moved to device)
"""

import logging
import warnings

import numpy as np
import torch

from src.core import config

logger = logging.getLogger(__name__)


# Note: We intentionally avoid OS-level FD manipulation. PyTorch warnings
# are handled by the runtime environment; developers can set appropriate
# environment flags if they need to suppress driver-level messages.


class VADetector:
    """
    Voice Activity Detection using Silero VAD.

    The Silero VAD model returns confidence scores (0.0 to 1.0) indicating
    the likelihood that the current audio chunk contains speech.

    Attributes:
        model: The loaded Silero VAD PyTorch model
        threshold: Confidence threshold for speech detection (configurable)
    """

    def __init__(self):
        """
        Load the Silero VAD model from torch.hub.

        This downloads the model from GitHub on first run (~30MB)
        and caches it locally (~/.cache/torch/...).

        Initialization Steps:
        1. Suppress Python warnings (filterwarnings)
        2. Suppress C++ warnings (FD2 hijacking) during model load
        3. Load the model from snakers4/silero-vad GitHub repo
        4. Set the detection threshold from config

        Raises:
            RuntimeError: If torch.hub can't download or the model is corrupted
        """
        logger.info("🧠 Loading Silero VAD model...")

        try:
            # Suppress Python-level warnings (scipy, sklearn, etc.)
            warnings.filterwarnings("ignore")

            # Load model via torch hub; keep it simple and move to device if CUDA
            self.model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                trust_repo=True,
            )

            # Determine device from config (prefer GPU if available)
            try:
                device_name = config.GPU_MODE if hasattr(config, "GPU_MODE") else (
                    "cuda" if torch.cuda.is_available() else "cpu"
                )
            except Exception:
                device_name = "cpu"

            self.device = torch.device(device_name)
            # Some hub models support .to(); attempt to move model to device
            try:
                self.model = self.model.to(self.device)
            except Exception:
                # Not all model objects have .to(); continue on CPU
                logger.debug("VAD model: unable to move to device, continuing on default")

            self.threshold = config.VAD_THRESHOLD
            logger.info(f"✅ VAD model loaded (threshold={self.threshold}) on {self.device}")

        except Exception as e:
            logger.critical(f"❌ Failed to load VAD model: {e}", exc_info=True)
            raise

    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Determine if an audio chunk contains speech.

        Args:
            audio_chunk: Numpy array of float32 audio samples at 16 kHz.
                        Typically 512 samples (32ms of audio).

        Returns:
            bool: True if confidence > threshold, False otherwise.

        Performance: ~5-10ms per chunk on CPU (parallelizable on multi-core)
        """
        # Ensure the audio is float32 and flat (1D array)
        audio_chunk = audio_chunk.flatten().astype(np.float32)

        try:
            # Convert numpy array to PyTorch tensor
            tensor_chunk = torch.from_numpy(audio_chunk).to(self.device)

            # Run inference through the VAD model; model expects 16k audio
            confidence = self.model(tensor_chunk, config.SAMPLE_RATE).item()

            is_speech = confidence > self.threshold

            if config.DEBUG_AUDIO_INPUT:
                logger.debug(f"VAD confidence: {confidence:.3f} → {is_speech}")

            return is_speech

        except Exception as e:
            logger.error(f"⚠️  VAD inference error: {e}")
            # Fail-safe: assume no speech to prevent infinite loops
            return False
