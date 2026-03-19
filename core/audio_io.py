import asyncio
import sounddevice as sd
import numpy as np
import sys
from core import config

class AudioInterface:
    def __init__(self):
        self.audio_queue = asyncio.Queue()
        self.is_listening = True
        self.is_speaking = False

    def _mic_callback(self, indata, frames, time, status):
        """
        Runs in a background C-thread. Pushes raw audio from the mic into the async queue.
        """
        if status:
            print(f"\n[Audio Error] {status}", file=sys.stderr)
            
        # Only capture audio if the agent isn't currently speaking (prevents echoing)
        if self.is_listening and not self.is_speaking:
            # Flatten the array and ensure it's float32 (Required by Silero VAD)
            chunk = indata.flatten().astype(np.float32)
            self.loop.call_soon_threadsafe(self.audio_queue.put_nowait, chunk)

    def start_listening(self):
        """Starts the non-blocking microphone stream."""
        self.loop = asyncio.get_running_loop()
        
        self.stream = sd.InputStream(
	    device=config.INPUT_DEVICE,
            samplerate=config.SAMPLE_RATE,
            channels=config.CHANNELS,
            dtype='float32',
            blocksize=config.CHUNK_SIZE,
            callback=self._mic_callback
        )
        self.stream.start()

    def stop_listening(self):
        """Stops the microphone stream."""
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
