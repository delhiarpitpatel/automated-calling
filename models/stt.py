from faster_whisper import WhisperModel
import numpy as np

class SpeechToText:
    def __init__(self):
        print("📝 Loading Faster-Whisper STT model (Hyper-Optimized CPU mode)...")
        # cpu_threads=4 forces it to perfectly map to your E2-7110's 4 physical cores
        # num_workers=1 prevents it from creating RAM-heavy parallel queues
        self.model = WhisperModel(
            "tiny.en", 
            device="cpu", 
            compute_type="int8",
            cpu_threads=4,
            num_workers=1
        )

    def transcribe(self, audio_array: np.ndarray) -> str:
        # beam_size=1: "Greedy decoding" (Massive speedup, stops second-guessing)
        # language="en": Skips the 500ms language detection phase
        # condition_on_previous_text=False: Stops it from analyzing past sentences
        segments, _ = self.model.transcribe(
            audio_array, 
            beam_size=1, 
            language="en",
            condition_on_previous_text=False,
            vad_filter=False # We already did VAD with Silero!
        )
        
        text = " ".join([segment.text for segment in segments])
        return text.strip()
