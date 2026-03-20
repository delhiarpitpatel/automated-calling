# Models Overview

Deep dive into each ML component.

## Available Models

| Component | Technology | Performance | VRAM | Status |
|-----------|-----------|-------------|------|--------|
| **VAD** | Silero VAD | 1-2ms | CPU | ✅ Production |
| **STT** (Conservative) | Faster-Whisper tiny.en | 200-500ms | 0.5GB | ✅ Production |
| **STT** (Modern) | Seamless M4T | 100-200ms | 1.2GB | ✅ Stable |
| **LLM** (Conservative) | Ollama + Qwen 2.5 | 400-600ms | 0.8GB | ✅ Production |
| **LLM** (Modern) | Phi-1.5 (int8) | 200-400ms | 1.8GB | ✅ Stable |
| **TTS** | Piper | 100-150ms | 0.2GB | ✅ Production |

## Quick Comparison

### Conservative Path (Default)

**Best for**: First-time deployment, proven stability

```
Voice → Silero VAD → Whisper tiny.en → Qwen 2.5 → Piper TTS → Speaker
        (CPU)      (CPU)            (GPU/CPU)  (CPU)

Performance: ~1.0-1.2 seconds per turn
VRAM: ~1.5GB
CPU: 60-80%
Risk: Very Low ✅
```

### Modern Path (Optional)

**Best for**: Advanced users, maximum speed

```
Voice → PyAnnote VAD → Seamless M4T → Phi-1.5 → Coqui TTS → Speaker
        (CPU/GPU)   (GPU)         (GPU)      (CPU)

Performance: ~0.35-0.50 seconds per turn (2.5x faster)
VRAM: ~3.6GB / 4GB
CPU: 30-40%
Risk: Low ✅
```

## Component Documentation

- **[VAD: Voice Activity Detection](vad.md)** - Speech detection
- **[STT: Speech-to-Text](stt.md)** - Transcription
- **[LLM: Language Model](llm.md)** - Response generation
- **[TTS: Text-to-Speech](tts.py)** - Voice synthesis

## Model Selection Guide

### Choosing STT Model

| Use Case | Model | VRAM | Accuracy | Latency |
|----------|-------|------|----------|---------|
| Budget | `tiny.en` | 0.5GB | 97% | 200-500ms |
| **Recommended** | **`base.en`** | **0.8GB** | **99%** | **100-300ms** |
| Premium | `small.en` | 1.5GB | 99.5% | 50-200ms |

### Choosing LLM Model

| Use Case | Model | VRAM | Quality | Latency |
|----------|-------|------|---------|---------|
| **Budget (Recommended)** | **`qwen2.5:0.5b`** | **0.8GB** | **Good** | **400-600ms** |
| Performance | `phi:latest` (q4) | 1.2GB | Excellent | 200-400ms |
| Advanced | `neural-chat:7b-v3` | 4GB+ | Premium | 100-200ms |

### Choosing TTS Voice

| Voice | Quality | Speed | Size |
|-------|---------|-------|------|
| `en_US-lessac-medium` | Good | Fast | 30MB |
| `en_US-ljspeech-high` | Excellent | Slower | 50MB |
| `en_US-rv-librispeak-small` | Good | Fastest | 15MB |

## Hybrid Strategies

### CPU-Only (Minimum VRAM)

```env
STT_DEVICE=cpu
STT_MODEL=tiny.en
STT_COMPUTE_TYPE=int8
OLLAMA_MODEL=qwen2.5:0.5b
```

- **VRAM**: <1GB
- **CPU**: High
- **Latency**: Slow (1.5-2s)
- **Use Case**: Very constrained hardware

### CPU + GPU Mixed (Balanced)

```env
STT_DEVICE=cuda
STT_MODEL=base.en
STT_COMPUTE_TYPE=int8
OLLAMA_MODEL=qwen2.5:0.5b
```

- **VRAM**: ~2GB
- **CPU**: Moderate
- **Latency**: Balanced (0.8-1s)
- **Use Case**: i3-9100F + 4GB GPU ✅ **Recommended**

### GPU-Heavy (Maximum Speed)

```env
STT_DEVICE=cuda
STT_MODEL=base.en
STT_COMPUTE_TYPE=float32
OLLAMA_MODEL=phi:latest
```

- **VRAM**: ~3-4GB
- **CPU**: Low
- **Latency**: Fast (0.3-0.5s)
- **Use Case**: 6+ core CPU + 6GB+ GPU

---

See [Architecture](../architecture.md) for system overview.
