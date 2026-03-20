# Quick Start

Get Automated Calling running in 5 minutes.

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/delhiarpitpatel/automated-calling.git
cd automated-calling
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Audio Devices

Find your audio device IDs:

```bash
python -m sounddevice
```

Edit `.env`:

```bash
cp .env.example .env
nano .env  # or edit in your editor
```

Set your audio devices:

```bash
INPUT_DEVICE=0    # Your microphone ID
OUTPUT_DEVICE=0   # Your speaker ID
```

### 5. Run

```bash
python -m src.main
```

The system will:
1. Listen for speech
2. Detect voice activity (VAD)
3. Transcribe when silence detected (STT)
4. Generate response via LLM
5. Speak response via TTS
6. Return to listening

## Configuration

All settings are in `.env`. Key options:

```bash
# Audio
INPUT_DEVICE=0              # Microphone device ID
OUTPUT_DEVICE=0             # Speaker device ID
SAMPLE_RATE=16000          # Sample rate (Hz)

# Voice Activity Detection
VAD_THRESHOLD=0.8          # Confidence threshold (0.5-0.95)
SILENCE_LIMIT_CHUNKS=30    # Chunks of silence before processing

# Speech-to-Text
STT_MODEL=tiny.en          # Model size: tiny.en, base.en, small.en
STT_DEVICE=cpu             # cpu or cuda
STT_COMPUTE_TYPE=int8      # int8 or float32

# Language Model
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:0.5b  # Model name

# Text-to-Speech
VOICE_MODEL_NAME=en_US-lessac-medium
UPSAMPLE_TTS_AUDIO=true    # Upsample to 44.1kHz
```

## n8n Integration (Optional)

Send voice commands to n8n webhooks:

1. Create n8n workflow with webhook trigger
2. Copy webhook URL
3. Set in `.env`:

```bash
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/...
```

The webhook receives:

```json
{
  "user_input": "What's the weather?",
  "timestamp": "2026-03-20T10:30:00Z",
  "confidence": 0.98
}
```

## Troubleshooting

### Audio Device Not Found

```bash
python -m sounddevice
# Find your device in the list, note the ID
# Update INPUT_DEVICE and OUTPUT_DEVICE in .env
```

### High Latency (>2s)

1. Check CPU usage: `htop` - other processes using CPU?
2. Try faster model: `STT_MODEL=tiny.en`
3. Check VRAM: `nvidia-smi` (if using GPU)

### No Sound Output

1. Verify `OUTPUT_DEVICE` is correct
2. Check speaker volume: `alsamixer`
3. Verify TTS is working: check logs

### Transcription Errors

1. Use USB headset for better audio
2. Reduce background noise
3. Try larger model: `STT_MODEL=base.en`

## Next Steps

- [Configure Advanced Options](configuration.md)
- [Understand Architecture](architecture.md)
- [Explore Models](models/overview.md)
- [Setup n8n Integration](integration/n8n.md)
- [Upgrade to Modern Path](../hardware-upgrade/GT730_MODERN_STACK.md)

## Getting Help

- 📖 [Full Documentation](index.md)
- 🐛 [GitHub Issues](https://github.com/delhiarpitpatel/automated-calling/issues)
- 💬 [Discussions](https://github.com/delhiarpitpatel/automated-calling/discussions)
