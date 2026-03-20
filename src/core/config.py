"""
Configuration module for the automated-calling voice agent.

This module loads environment variables and provides sensible defaults for:
- Audio input/output device management
- Sample rate and chunk size for low-latency processing
- VAD sensitivity thresholds
- LLM and TTS model paths
- n8n webhook integration parameters

All hardcoded paths and device IDs are replaced with environment variables
for maximum portability across different Linux distributions and hardware.

Usage:
    Run `python -m sounddevice` to discover device IDs on your system.
    Set INPUT_DEVICE and OUTPUT_DEVICE in your .env file, or leave as None
    for automatic device selection.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    logging.warning(f".env file not found at {ENV_FILE}. Using defaults.")

# ==================== AUDIO SETTINGS ====================
# Run `python -m sounddevice` in terminal to find your mic's ID number.
# Set INPUT_DEVICE in .env to the integer of your active mic (e.g., INPUT_DEVICE=6)
# If None, sounddevice will auto-select the default device.
INPUT_DEVICE = os.getenv("INPUT_DEVICE", None)
if INPUT_DEVICE is not None:
    INPUT_DEVICE = int(INPUT_DEVICE)

OUTPUT_DEVICE = os.getenv("OUTPUT_DEVICE", None)
if OUTPUT_DEVICE is not None:
    OUTPUT_DEVICE = int(OUTPUT_DEVICE)

# 16000 Hz is the standard for Silero VAD and Faster-Whisper.
# Do not change unless you understand the implications for all downstream models.
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 16000))
CHANNELS = int(os.getenv("CHANNELS", 1))

# 512 frames per chunk = 32ms of audio per loop. Perfect for low latency.
# Decrease for faster response (more CPU), increase for stability.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))

# ==================== VAD SETTINGS ====================
# Confidence threshold for speech detection (0.0 to 1.0)
# Lower = more sensitive to noise, Higher = might miss quiet speech
# Recommended: 0.5 (very sensitive) to 0.85 (balanced)
VAD_THRESHOLD = float(os.getenv("VAD_THRESHOLD", 0.8))

# How many consecutive silent chunks before we assume the user is done speaking?
# 30 chunks * 32ms = ~1 second of silence. Decrease for faster responses.
SILENCE_LIMIT_CHUNKS = int(os.getenv("SILENCE_LIMIT_CHUNKS", 30))

# ==================== STT (SPEECH-TO-TEXT) SETTINGS ====================
# Model: "tiny.en" (fastest), "base.en" (balanced), "small.en" (better accuracy)
# For AMD APU / 8GB RAM, stick with "tiny.en" to maintain <500ms transcription time.
STT_MODEL = os.getenv("STT_MODEL", "tiny.en")
STT_DEVICE = os.getenv("STT_DEVICE", "cpu")
STT_COMPUTE_TYPE = os.getenv("STT_COMPUTE_TYPE", "int8")  # int8 for low VRAM
STT_CPU_THREADS = int(os.getenv("STT_CPU_THREADS", 4))
STT_NUM_WORKERS = int(os.getenv("STT_NUM_WORKERS", 1))

# ==================== LLM (LARGE LANGUAGE MODEL) SETTINGS ====================
# Ollama must be running on the system: `ollama serve`
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_REQUEST_TIMEOUT = float(os.getenv("OLLAMA_REQUEST_TIMEOUT", 30.0))

LLM_SYSTEM_PROMPT = (
    "You are a helpful, conversational AI phone agent. "
    "Keep your answers extremely concise, natural, and friendly. "
    "Never use emojis, formatting, or lists. Speak exactly as a human would on the phone."
)

# ==================== TTS (TEXT-TO-SPEECH) SETTINGS ====================
# Path to the Piper ONNX voice model. Place .onnx and .json files in models/voices/
VOICE_MODEL_DIR = Path(os.getenv("VOICE_MODEL_DIR", "models/voices"))
VOICE_MODEL_NAME = os.getenv("VOICE_MODEL_NAME", "en_US-lessac-medium")

# Piper outputs at 22050 Hz. Some hardware (e.g., Bluetooth) needs upsampling.
# Set to True to upsample to 44100 Hz (doubles audio array size).
UPSAMPLE_TTS_AUDIO = os.getenv("UPSAMPLE_TTS_AUDIO", "true").lower() == "true"
TTS_OUTPUT_SAMPLE_RATE = 44100 if UPSAMPLE_TTS_AUDIO else 22050

# Temporary file for TTS synthesis (will be deleted after playback)
TTS_TEMP_FILE = os.getenv("TTS_TEMP_FILE", "temp_output.wav")

# ==================== N8N WEBHOOK INTEGRATION ====================
# Leave blank to disable n8n integration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")
N8N_REQUEST_TIMEOUT = float(os.getenv("N8N_REQUEST_TIMEOUT", 10.0))
N8N_RETRY_ATTEMPTS = int(os.getenv("N8N_RETRY_ATTEMPTS", 2))

# ==================== LOGGING & DEBUG ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG_AUDIO_INPUT = os.getenv("DEBUG_AUDIO_INPUT", "false").lower() == "true"

# ==================== GPU / CUDA DETECTION ====================
# Auto-detect CUDA availability and expose simple flags for the rest of the
# codebase. Honor environment override via GPU_ENABLED ("auto", "true", "false").
GPU_ENABLED = os.getenv("GPU_ENABLED", "auto").lower()  # auto|true|false
try:
    import torch as _torch  # local alias to avoid shadowing

    HAS_CUDA = _torch.cuda.is_available()
    CUDA_DEVICE_COUNT = _torch.cuda.device_count() if HAS_CUDA else 0
    CUDA_DEVICE_NAME = _torch.cuda.get_device_name(0) if HAS_CUDA else "None"
except Exception:
    HAS_CUDA = False
    CUDA_DEVICE_COUNT = 0
    CUDA_DEVICE_NAME = "None"

if GPU_ENABLED == "auto":
    GPU_MODE = "cuda" if HAS_CUDA else "cpu"
elif GPU_ENABLED == "true":
    GPU_MODE = "cuda"
else:
    GPU_MODE = "cpu"

# Adjust default STT compute type if CUDA is present and user left default
if STT_COMPUTE_TYPE == "int8" and HAS_CUDA:
    # prefer float16 on CUDA-capable devices for a balance of speed/quality
    STT_COMPUTE_TYPE = os.getenv("STT_COMPUTE_TYPE", "float16")

# expose these values for other modules
# Example: core/config.GPU_MODE -> "cuda" or "cpu"
