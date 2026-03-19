# --- AUDIO SETTINGS ---
# Run `python -m sounddevice` in terminal to find your mic's ID number.
# Change this from None to the integer of your active mic (e.g., 2)
INPUT_DEVICE = 6

# --- AUDIO SETTINGS ---
# 16000 Hz is the standard for Silero VAD and Whisper. Do not change this.
SAMPLE_RATE = 16000 
CHANNELS = 1

# 512 frames per chunk = 32ms of audio per loop. Perfect for low latency.
CHUNK_SIZE = 512      

# --- VAD SETTINGS ---
# Confidence threshold for speech detection (0.0 to 1.0)
# Lower = more sensitive to noise, Higher = might miss quiet speech
VAD_THRESHOLD = 0.8

# How many consecutive silent chunks before we assume the user is done speaking?
# 30 chunks * 32ms = ~1 second of silence to trigger the AI response
SILENCE_LIMIT_CHUNKS = 30
