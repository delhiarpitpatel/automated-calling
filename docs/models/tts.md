# TTS: Text-to-Speech

Converts response text back to speech for voice output.

## What is TTS?

Text-to-Speech synthesizes natural-sounding speech from text:

```
Input: "The weather is sunny today."
Output: Audio file with spoken sentence
```

## Piper TTS (Default)

**Implementation**: `src/models/tts.py`

**Technology**: ONNX-based voice synthesis
- Pre-trained ONNX models
- CPU-friendly
- Multiple voices available
- Natural-sounding output
- Fast inference (100-150ms)

### Configuration

```bash
VOICE_MODEL_NAME=en_US-lessac-medium    # Voice model name
UPSAMPLE_TTS_AUDIO=true                 # Upsample to 44.1kHz (Bluetooth)
```

### Available Voices

**Default** (recommended):
```
en_US-lessac-medium    # Clear, natural quality ✅
```

**Other Options**:
```
en_US-ljspeech-high    # Higher quality, larger file
en_US-rv-librispeak-small   # Smaller, faster
```

### Voice Comparison

| Voice | Quality | Size | Speed | File Size | Recommended |
|-------|---------|------|-------|-----------|-------------|
| `lessac-medium` | Good | 30MB | Fast | Medium | ✅ Default |
| `ljspeech-high` | Excellent | 50MB | Slower | Large | Premium |
| `librispeak-small` | Good | 15MB | Fastest | Small | Minimal |

**Recommended**: `en_US-lessac-medium` (best balance)

## Performance

- **Latency**: 100-150ms per sentence
- **CPU**: ~10-20%
- **Memory**: ~200MB for model
- **VRAM**: Minimal (CPU-based)
- **Quality**: Clear, natural-sounding

## Configuration

### Basic Setup

```env
VOICE_MODEL_NAME=en_US-lessac-medium
UPSAMPLE_TTS_AUDIO=true
```

### Upsampling (Bluetooth Fix)

**Problem**: Piper outputs 22.05kHz, Bluetooth expects 44.1kHz

**Solution**: Enable upsampling
```env
UPSAMPLE_TTS_AUDIO=true
```

- **Cost**: +50ms latency
- **Benefit**: No Bluetooth audio dropouts
- **Recommendation**: Enable if using Bluetooth speakers/headset ✅

**Disable upsampling** if using wired speakers:
```env
UPSAMPLE_TTS_AUDIO=false
```

## Voice Download

Voices are ONNX models stored in `models/voices/`:

```
models/voices/
├── en_US-lessac-medium.onnx           # Model file (30MB)
└── en_US-lessac-medium.onnx.json      # Metadata
```

### Download New Voices

```bash
# From Piper official repository
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Place in models/voices/ directory
mv en_US-lessac-medium.* models/voices/
```

### Available Languages

Piper supports 15+ languages:
- English (en_US, en_GB)
- Spanish (es_ES, es_MX)
- French, German, Italian, Dutch, Portuguese, Russian, Chinese, Japanese, Korean, Turkish, and more

See: https://github.com/rhasspy/piper/blob/master/VOICES.md

## Advanced Configuration

### Speed Control

Adjust speech speed (in code):

```python
from src.models.tts import TextToSpeech

tts = TextToSpeech()

# Slower speech
audio = tts.synthesize("Hello", speed=0.8)

# Faster speech
audio = tts.synthesize("Hello", speed=1.2)
```

### Multiple Voices

Support multiple voices for different speakers:

```python
# System response
system_audio = tts.synthesize(response, voice="en_US-lessac-medium")

# User would need separate TTS for playback
```

## Troubleshooting

### No Sound Output

1. **Check output device**
   ```bash
   python -m sounddevice
   OUTPUT_DEVICE=0    # Set correct device
   ```

2. **Check speaker volume**
   ```bash
   alsamixer         # Linux
   # Adjust Master volume
   ```

3. **Check TTS logs**
   ```bash
   grep "TTS" automated_calling.log
   ```

### Poor Audio Quality

1. **Use higher quality voice**
   ```env
   VOICE_MODEL_NAME=en_US-ljspeech-high
   ```

2. **Check audio settings**
   - Reduce background noise
   - Use better speakers
   - Improve microphone placement

3. **Check upsampling**
   - If Bluetooth, keep `UPSAMPLE_TTS_AUDIO=true`
   - If wired, try `false` for lower latency

### Bluetooth Audio Drops

1. **Enable upsampling**
   ```env
   UPSAMPLE_TTS_AUDIO=true
   ```

2. **Use different Bluetooth codec**
   - Some Bluetooth devices need specific sample rates
   - Try 44.1kHz (upsampled) vs 22.05kHz (native)

3. **Check Bluetooth connection**
   ```bash
   pactl list cards    # PulseAudio devices
   ```

### High Latency (>500ms for response)

1. **Disable upsampling**
   ```env
   UPSAMPLE_TTS_AUDIO=false    # Save 50ms
   ```

2. **Use faster voice**
   ```env
   VOICE_MODEL_NAME=en_US-rv-librispeak-small
   ```

## Alternative: CoquiTTS (Modern Path)

For **Modern Path** with more advanced features:

```bash
pip install TTS
```

**Advantages**:
- More voices available
- Better quality
- Supports custom speakers
- Multilingual

**Disadvantages**:
- Slower (200-300ms)
- Requires 0.5-1GB VRAM
- More complex setup

### Configuration

```python
from TTS.api import TTS

model_name = "tts_models/en/ljspeech/tacotron2-DDC"
device = "cuda"  # or "cpu"
tts = TTS(model_name=model_name, gpu=device=="cuda")

# Synthesize
audio = tts.tts(text="Hello world", speaker_idx=0)
```

---

See [Models Overview](overview.md) for architecture overview.
