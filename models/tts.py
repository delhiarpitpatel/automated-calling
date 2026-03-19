import wave
import sounddevice as sd
import numpy as np
import os
from piper import PiperVoice

class TextToSpeech:
    def __init__(self):
        print("📢 Loading Piper TTS model (CPU optimized)...")
        model_path = "models/voices/en_US-lessac-medium.onnx"
        self.voice = PiperVoice.load(model_path)
        
    def speak(self, text: str):
        wav_path = "temp_output.wav"
        
        # 1. Open the wave file object FIRST
        with wave.open(wav_path, 'wb') as wav_file:
            # 2. Hand the OPEN object to Piper so it can set the headers and write
            self.voice.synthesize_wav(text, wav_file)
            
        # 3. Read the beautifully formatted physical file back into memory
        with wave.open(wav_path, 'rb') as wav_file:
            raw_data = wav_file.readframes(wav_file.getnframes())
            audio_array = np.frombuffer(raw_data, dtype=np.int16)
            
        # 4. Upsample 22050 Hz to 44100 Hz for your boAt Rockerz
        audio_array_44k = np.repeat(audio_array, 2)
        
        # 5. Play through Device 5 (PulseAudio)
        sd.play(audio_array_44k, samplerate=44100, device=5)
        sd.wait() 
        
        # 6. Clean up the temp file
        if os.path.exists(wav_path):
            os.remove(wav_path)
