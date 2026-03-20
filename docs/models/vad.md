# VAD: Voice Activity Detection

Voice Activity Detection identifies when the user is speaking.

## What is VAD?

VAD processes audio and returns a confidence score (0.0-1.0) indicating if speech is present:
- `0.0` = Definitely silence
- `0.5` = Maybe speech  
- `1.0` = Definitely speech

The agent listens continuously and only sends audio to STT when VAD detects speech + silence window.

## Silero VAD

**Implementation**: `src/models/vad.py`

**Technology**: Pre-trained neural network (ONNX format)
- Small size: 7MB
- CPU-only (no GPU needed)
- Fast: 1-2ms per chunk
- Accurate: ~88% precision

### Configuration

```bash
VAD_THRESHOLD=0.8          # Confidence threshold (0.5-0.95)
SILENCE_LIMIT_CHUNKS=30    # Chunks of silence before sending to STT
```

### Threshold Tuning

| Threshold | Sensitivity | Use Case |
|-----------|-----------|----------|
| `0.5` | Very sensitive | Quiet environments, don't miss any speech |
| `0.7` | Balanced | Normal office/home |
| `0.8` | Strict | Noisy environments, reduce false positives |
| `0.95` | Very strict | Only obvious speech |

**Recommended**: `0.8` (filters ambient noise)

### Silence Detection

At 16kHz with 512 samples = 32ms per chunk:

```
SILENCE_LIMIT_CHUNKS=30 → ~960ms of silence before processing
SILENCE_LIMIT_CHUNKS=15 → ~480ms of silence before processing
SILENCE_LIMIT_CHUNKS=45 → ~1440ms of silence before processing
```

**Recommended**: `30` (wait ~1 second for user to finish speaking)

## Performance

- **Latency**: 1-2ms per chunk ✅ (negligible)
- **CPU**: ~1-2% per core
- **Memory**: ~10MB
- **Accuracy**: ~88% (typical)

## Advanced Configuration

### For Noisy Environments

```env
VAD_THRESHOLD=0.85
SILENCE_LIMIT_CHUNKS=45
```

- Higher threshold filters more noise
- Longer silence wait ensures speech completion

### For Quick Response

```env
VAD_THRESHOLD=0.7
SILENCE_LIMIT_CHUNKS=15
```

- Lower threshold catches softer speech
- Shorter silence window for faster processing

## Troubleshooting

### "Misses quiet speech"
- Lower `VAD_THRESHOLD`: `0.7` or `0.6`
- Use better microphone
- Increase `SILENCE_LIMIT_CHUNKS` (wait longer)

### "False positives (detects noise as speech)"
- Raise `VAD_THRESHOLD`: `0.85` or `0.9`
- Improve audio quality
- Reduce background noise

### "Too slow to detect speech"
- Lower `VAD_THRESHOLD`
- Reduce `SILENCE_LIMIT_CHUNKS`
- Use more aggressive threshold

## Alternative: PyAnnote VAD (Modern Path)

For **Modern Path** setup, you can upgrade to PyAnnote VAD:

```bash
pip install pyannote.audio
```

**Advantages**:
- Slightly better accuracy (95%+)
- Better on difficult audio
- Supports voice activity boundaries

**Disadvantages**:
- Slower (5-10ms vs 1-2ms)
- Uses 0.4GB VRAM
- More complex setup

### Configuration

Replace `src/models/vad.py` with PyAnnote implementation:

```python
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained("pyannote/voice-activity-detection")
vad = pipeline("audio.wav")
```

---

See [Models Overview](overview.md) for comparison with other components.
