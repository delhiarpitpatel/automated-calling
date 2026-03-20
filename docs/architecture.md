# Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    Voice Agent Pipeline                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Microphone] → [VAD] → [STT] → [LLM] → [TTS] → [Speaker]     │
│                                   ↓                              │
│                           [n8n Webhook]                          │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│              Audio Processing & State Management                 │
│           (error handling, logging, configuration)              │
└──────────────────────────────────────────────────────────────────┘
```

## Components

### Audio I/O (`core/audio_io.py`)

Handles real-time audio input/output using `sounddevice` library.

**Responsibilities**:
- Capture audio chunks from microphone
- Queue audio for processing
- Play synthesized speech via speakers
- Handle device enumeration and configuration

**Key Features**:
- Async/await support
- Configurable sample rates (16kHz, 44.1kHz, etc.)
- Device auto-detection
- Error handling for audio glitches

### Voice Activity Detection (`models/vad.py`)

Detects when user is speaking using Silero VAD.

**Responsibilities**:
- Classify audio chunks as speech or silence
- Return confidence scores (0.0-1.0)
- Batch processing for efficiency

**Performance**:
- Latency: 1-2ms per chunk
- CPU-only (no GPU needed)
- Accuracy: ~88%

### Speech-to-Text (`models/stt.py`)

Transcribes speech to text using Faster-Whisper (OpenAI Whisper).

**Responsibilities**:
- Convert audio to text
- Handle multiple model sizes (tiny, base, small)
- Support int8 quantization for low VRAM
- Return confidence scores

**Performance** (Conservative Path):
- Model: `tiny.en` (74M parameters)
- VRAM: ~0.5GB
- Latency: 200-500ms per sentence
- Accuracy: 97% on clean audio

**Performance** (Modern Path):
- Model: `Seamless M4T` (int8)
- VRAM: ~1.2GB
- Latency: 100-200ms
- Accuracy: 98-99%

### Language Model (`models/llm.py`)

Generates responses using Ollama + local LLM.

**Responsibilities**:
- Convert user input to intelligent response
- Handle streaming/non-streaming inference
- Support multiple model backends
- Format responses for TTS

**Conservative Path**:
- Model: `qwen2.5:0.5b` (500M parameters)
- VRAM: ~0.8GB
- Latency: 400-600ms per response
- Quality: Good for basic conversations

**Modern Path**:
- Model: `Phi-1.5` (1.3B parameters, int8)
- VRAM: ~1.8GB
- Latency: 200-400ms
- Quality: Excellent, nuanced responses

### Text-to-Speech (`models/tts.py`)

Synthesizes responses to speech using Piper TTS.

**Responsibilities**:
- Convert text to speech audio
- Support multiple voices
- Adjust speed/pitch
- Upsample to 44.1kHz if needed (Bluetooth compatibility)

**Performance**:
- Model: `en_US-lessac-medium` (ONNX)
- VRAM: ~0.2GB
- Latency: 100-150ms per sentence
- Quality: Clear, natural-sounding speech

### Configuration (`core/config.py`)

Centralized configuration management.

**Responsibilities**:
- Load settings from `.env` file
- Validate configuration values
- Provide sensible defaults
- Handle environment variable overrides

**Key Settings**:
- Audio device IDs
- Model paths and parameters
- n8n webhook URL
- VAD thresholds
- STT/LLM/TTS model sizes

### State Manager (`core/state_manager.py`)

Tracks call state and conversation context.

**Responsibilities**:
- Track active call state
- Store conversation history
- Manage silence detection counters
- Handle error recovery

### n8n Integration (`integrations/n8n_client.py`)

Sends events to n8n webhooks.

**Responsibilities**:
- Format transcribed input
- Send webhook requests
- Handle webhook failures gracefully
- Log integration events

**Webhook Payload**:
```json
{
  "user_input": "What's the weather?",
  "timestamp": "2026-03-20T10:30:00Z",
  "confidence": 0.98
}
```

## Data Flow

### Complete Call Sequence

1. **Listen Phase**
   - Audio I/O captures microphone input
   - Audio queued as 512-sample chunks (32ms @ 16kHz)

2. **Detection Phase**
   - VAD runs on each chunk
   - When confidence > threshold → speech detected
   - Accumulate chunks while speaking

3. **Transcription Phase**
   - When silence detected for N chunks → stop listening
   - Feed accumulated audio to STT
   - STT returns transcribed text

4. **Webhook Phase** (if enabled)
   - Send text to n8n webhook
   - Webhook processes and returns actions
   - Log results

5. **Generation Phase**
   - Pass transcribed text to LLM
   - LLM generates response text
   - Return first sentence for immediate TTS

6. **Synthesis Phase**
   - Pass response text to TTS
   - TTS generates audio
   - Audio played via speakers

7. **Loop**
   - Return to Listen Phase
   - Continue conversation

## Performance Targets

### Conservative Path
```
Voice → VAD (1-2ms) → STT (200-500ms) → LLM (400-600ms) 
      → TTS (100-150ms) → Speaker
Total: 700-1200ms per turn
```

### Modern Path
```
Voice → VAD (5-10ms) → STT (100-200ms) → LLM (200-400ms)
      → TTS (50-100ms) → Speaker
Total: 350-500ms per turn (2.5-3x faster)
```

## Resource Usage

### Conservative Path
- **CPU**: 60-80% (all 4 cores on i3-9100F)
- **RAM**: 2-3.5GB
- **VRAM**: ~1.5GB
- **Disk**: 2-3GB (model files)

### Modern Path
- **CPU**: 30-40%
- **RAM**: 4-5GB
- **VRAM**: ~3.6GB / 4GB
- **Disk**: 5-8GB (larger models)

## Technical Decisions

### Why CPU VAD?
- Silero VAD runs on CPU with negligible overhead
- No GPU needed, reduces memory pressure
- Latency is excellent (1-2ms)

### Why Quantized Models?
- int8 quantization cuts VRAM use by 75%
- Minimal accuracy loss (<1%)
- Critical for 4GB GPU constraint

### Why Ollama?
- Easy local LLM management
- Automatic quantization
- Robust error handling
- Flexible model selection

### Why Piper TTS?
- ONNX format (no framework overhead)
- CPU-friendly (fast enough)
- Multiple voice options
- Good audio quality

## Thread Safety

All components are async-safe:
- Audio I/O uses `asyncio.Queue`
- Model inference uses thread pools
- State updates are atomic
- Logging is thread-safe

## Error Handling

Each component has try-except blocks:
- Audio device errors → fallback to default
- Model loading errors → graceful exit with logs
- Inference errors → skip component, continue
- Webhook errors → log and continue listening

---

See [Models](models/overview.md) for deep dives into each component.
