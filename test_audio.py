import sounddevice as sd
import numpy as np
import time

def generate_beep(duration=0.25, frequency=440, samplerate=44100):
    """Generates a soft sine wave beep (A4 note)."""
    t = np.linspace(0, duration, int(samplerate * duration), False)
    audio = np.sin(frequency * t * 2 * np.pi) * 0.1 
    return audio

def test_all_outputs():
    print("🔍 Scanning all audio devices for Output capabilities...\n")
    
    devices = sd.query_devices()
    samplerate = 44100
    beep = generate_beep(duration=0.25, samplerate=samplerate)
    
    passed = []
    failed = []

    for device_id, device_info in enumerate(devices):
        if device_info['max_output_channels'] > 0:
            name = device_info['name']
            print(f"Testing Device [{device_id}]: {name[:40]:<40} ...", end=" ")
            
            try:
                sd.play(beep, samplerate=samplerate, device=device_id)
                sd.wait() 
                print("✅ PASS")
                passed.append(device_id)
                time.sleep(0.1) 
            except Exception as e:
                error_msg = str(e).split('\n')[0] 
                print(f"❌ FAIL ({error_msg})")
                failed.append(device_id)
    return passed

def test_tts_on_device():
    print("\n" + "="*50)
    print("📢 TESTING PIPER TTS ON BLUETOOTH (DEVICE 6)")
    print("="*50)
    
    try:
        # Import your actual TTS class
        from models.tts import TextToSpeech
        tts = TextToSpeech()
        
        test_phrase = "Hello Arpit, this is your local AI speaking directly into your headphones."
        print(f"\n🗣️ Generating audio for: '{test_phrase}'")
        
        # This will use the device=6 hardcode we just put in your tts.py
        tts.speak(test_phrase)
        
        print("\n✅ TTS Generation and Playback Executed Successfully!")
    except Exception as e:
        print(f"\n❌ TTS Test Failed: {e}")

if __name__ == "__main__":
    # 1. Run the beep test
    test_all_outputs()
    
    # 2. Run the TTS voice test
    test_tts_on_device()
