# Configuration

Complete configuration reference for Automated Calling.

## Environment Variables

All settings are configured via `.env` file or environment variables.

### Getting Started

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

## Audio Settings

### Input Device

```bash
INPUT_DEVICE=0
```

Device ID for microphone input. Find your device:

```bash
python -m sounddevice
```

- `0` = Default input device
- `>0` = Specific device by index
- Set to your USB headset for best quality

### Output Device

```bash
OUTPUT_DEVICE=0
```

Device ID for speaker output.

### Sample Rate

```bash
SAMPLE_RATE=16000
```

Audio sample rate in Hz. Options:
- `16000` - Standard (VAD/STT optimized) ✅ **Recommended**
- `44100` - Hi-fi (for music, not needed for voice)

### Chunk Size

```bash
CHUNK_SIZE=512
```

Audio frames per chunk. At 16kHz:
- `512` = 32ms per chunk ✅ **Recommended**
- `256` = 16ms (more CPU)
- `1024` = 64ms (higher latency)

## Voice Activity Detection (VAD)

### Threshold

```bash
VAD_THRESHOLD=0.8
```

Confidence threshold for speech detection (0.0-1.0):
- `0.5` - Sensitive (detects every sound)
- `0.7` - Balanced
- `0.8` - Strict (ignores ambient noise) ✅ **Recommended**
- `0.95` - Very strict (might miss speech)

### Silence Limit

```bash
SILENCE_LIMIT_CHUNKS=30
```

Number of non-speech chunks before stopping:
- At 16kHz with 512 samples = ~32ms per chunk
- `30` chunks = ~1 second of silence ✅ **Recommended**
- `15` = 500ms (might cut off speech)
- `60` = 2 seconds (waits longer)

## Speech-to-Text (STT)

### Model

```bash
STT_MODEL=tiny.en
```

Whisper model size:
- `tiny.en` - 39M params, 0.5GB VRAM, 97% accuracy ✅ **Recommended (Conservative)**
- `base.en` - 74M params, 0.8GB VRAM, 99% accuracy ✅ **Recommended (Modern)**
- `small.en` - 244M params, 1.5GB VRAM, 99.5% accuracy (Modern Path)

### Device

```bash
STT_DEVICE=cpu
```

Where to run STT:
- `cpu` - Run on CPU (slower but saves VRAM) ✅ **Recommended (Conservative)**
- `cuda` - Run on GPU (faster, requires VRAM) ✅ **Recommended (Modern, 4GB+)**

### Compute Type

```bash
STT_COMPUTE_TYPE=int8
```

Quantization for faster inference:
- `int8` - 8-bit quantization, 75% smaller, ~1% accuracy loss ✅ **Recommended**
- `float32` - Full precision, larger, slower, more accurate

## Language Model (LLM)

### Ollama Base URL

```bash
OLLAMA_BASE_URL=http://localhost:11434
```

URL to your Ollama instance. Must be running before starting the agent:

```bash
ollama serve  # In separate terminal
```

### Model Name

```bash
OLLAMA_MODEL=qwen2.5:0.5b
```

Which model to use:

**Conservative Path**:
- `qwen2.5:0.5b` - 0.5B params, 0.8GB VRAM ✅ **Recommended**
- `phi:latest` - 1.3B params, 1.2GB VRAM
- `neural-chat:latest` - 7B params (requires 4GB+, slow)

**Modern Path**:
- `phi:latest` with `--quantize q4_0` - 1.3B params, 0.6GB quantized
- `neural-chat:7b-v3` with quantization

See Ollama docs for available models: https://ollama.ai

## Text-to-Speech (TTS)

### Voice Model Name

```bash
VOICE_MODEL_NAME=en_US-lessac-medium
```

Piper voice to use. Included voices:
- `en_US-lessac-medium` ✅ **Default (good quality)**
- `en_US-ljspeech-high` (higher quality, slower)
- `en_US-rv-librispeak-small` (smaller, faster)

Download more voices: https://huggingface.co/rhasspy/piper-voices

### Upsample Audio

```bash
UPSAMPLE_TTS_AUDIO=true
```

Upsample TTS output from 22.05kHz to 44.1kHz:
- `true` - Upsample for Bluetooth compatibility ✅ **Recommended if using Bluetooth**
- `false` - Keep 22.05kHz (lower latency)

## n8n Integration

### Webhook URL

```bash
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id
```

Leave empty to disable webhook:
```bash
N8N_WEBHOOK_URL=
```

To get webhook URL:
1. Create n8n workflow with Webhook trigger
2. Configure trigger as "POST"
3. Copy webhook URL

Payload sent:
```json
{
  "user_input": "What's the weather?",
  "timestamp": "2026-03-20T10:30:00Z",
  "confidence": 0.98
}
```

## Logging

### Log Level

```bash
LOG_LEVEL=INFO
```

Options:
- `DEBUG` - Very verbose (development)
- `INFO` - Standard (recommended) ✅
- `WARNING` - Errors only
- `ERROR` - Critical errors only

### Log File

```bash
LOG_FILE=automated_calling.log
```

Path to log file. Logs are written to both file and console.

## Development Settings

### Debug Mode

```bash
DEBUG=false
```

Enable extra debugging:
- `false` - Production mode ✅
- `true` - Debug mode (verbose logs, slower)

## Full Example `.env`

```bash
# Audio
INPUT_DEVICE=0
OUTPUT_DEVICE=0
SAMPLE_RATE=16000
CHUNK_SIZE=512

# VAD
VAD_THRESHOLD=0.8
SILENCE_LIMIT_CHUNKS=30

# STT
STT_MODEL=tiny.en
STT_DEVICE=cpu
STT_COMPUTE_TYPE=int8

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:0.5b

# TTS
VOICE_MODEL_NAME=en_US-lessac-medium
UPSAMPLE_TTS_AUDIO=true

# n8n Integration
N8N_WEBHOOK_URL=

# Logging
LOG_LEVEL=INFO
LOG_FILE=automated_calling.log

# Development
DEBUG=false
```

## Performance Tuning

### For Lower Latency

```bash
# Use faster models
STT_MODEL=tiny.en
OLLAMA_MODEL=qwen2.5:0.5b

# Reduce silence wait
SILENCE_LIMIT_CHUNKS=15

# Lower chunk size (more CPU)
CHUNK_SIZE=256

# Disable upsampling
UPSAMPLE_TTS_AUDIO=false
```

### For Better Quality

```bash
# Use larger models
STT_MODEL=base.en
OLLAMA_MODEL=neural-chat:latest

# Better voice
VOICE_MODEL_NAME=en_US-ljspeech-high

# Longer silence detection
SILENCE_LIMIT_CHUNKS=45

# Higher sample rate
SAMPLE_RATE=44100
```

### For Lower VRAM Usage

```bash
# Run STT on CPU
STT_DEVICE=cpu

# Use smaller models
STT_MODEL=tiny.en
OLLAMA_MODEL=qwen2.5:0.5b

# Quantization
STT_COMPUTE_TYPE=int8
```

## Troubleshooting Configuration

### "No audio input" error
- Check `INPUT_DEVICE` matches actual device: `python -m sounddevice`
- Verify microphone is not muted
- Try `INPUT_DEVICE=0` (default)

### High latency (>2 seconds)
- Check `STT_MODEL=tiny.en` (fastest)
- Verify `STT_DEVICE=cpu` for Conservative Path
- Increase `SILENCE_LIMIT_CHUNKS` to wait longer

### Out of memory (OOM) errors
- Check VRAM: `nvidia-smi`
- Reduce `STT_MODEL` to `tiny.en`
- Set `STT_DEVICE=cpu`
- Use smaller OLLAMA_MODEL

### Poor transcription quality
- Use larger model: `STT_MODEL=base.en`
- Improve audio: use USB headset
- Reduce background noise
- Set `STT_DEVICE=cuda` (GPU) for better accuracy

---

See [Quick Start](quickstart.md) for basic setup.
