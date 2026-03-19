import os
import sys
import torch
import numpy as np
from contextlib import contextmanager
from core import config

@contextmanager
def suppress_c_stderr():
    """
    Temporarily redirects C-level stderr (File Descriptor 2) to /dev/null
    to silence hardcoded PyTorch/C++ backend warnings.
    """
    # Open /dev/null
    devnull = os.open(os.devnull, os.O_WRONLY)
    # Save the original stderr
    old_stderr = os.dup(2)
    # Point stderr to /dev/null
    os.dup2(devnull, 2)
    try:
        yield
    finally:
        # Restore the original stderr and clean up
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stderr)

class VADetector:
    def __init__(self):
        print("🧠 Loading Silero VAD model (CPU)...")
        import warnings
        warnings.filterwarnings("ignore")
        
        # Suppress warnings during the initial model load
        with suppress_c_stderr():
            self.model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                trust_repo=True
            )
        self.threshold = config.VAD_THRESHOLD

    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        audio_chunk = audio_chunk.flatten().astype(np.float32)
        tensor_chunk = torch.from_numpy(audio_chunk)
        
        # Suppress warnings during inference (this stops the continuous spam)
        with suppress_c_stderr():
            confidence = self.model(tensor_chunk, config.SAMPLE_RATE).item()
        
        return confidence > self.threshold
