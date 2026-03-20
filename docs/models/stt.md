# STT: Speech-to-Text

Converts spoken audio to text using OpenAI Whisper.

## What is STT?

Speech-to-Text (transcription) takes audio chunks and returns text:

```
Audio: "What's the weather?" (3 seconds) → Text: "What's the weather?"
```

## Faster-Whisper (Conservative Path)

**Implementation**: `src/models/stt.py`

**Technology**: OpenAI Whisper via faster-whisper
- Multiple model sizes available
- int8 quantization for low VRAM
- CPU or GPU support
- Excellent accuracy (97-99%)

### Configuration

```bash
STT_MODEL=tiny.en           # Model size: tiny.en, base.en, small.en
STT_DEVICE=cpu              # cpu or cuda
STT_COMPUTE_TYPE=int8       # int8 or float32
```

### Model Comparison

| Model | Size | VRAM | Speed | Accuracy | Recommended |
|-------|------|------|-------|----------|-------------|
| `tiny.en` | 39M | 0.5GB | 200-500ms | 97% | Budget |
| `base.en` | 74M | 0.8GB | 100-300ms | 99% | ✅ Balanced |
| `small.en` | 244M | 1.5GB | 50-200ms | 99.5% | Premium |

**Recommended**: `base.en` (best balance)

### Device Selection

#### CPU Inference
```bash
STT_DEVICE=cpu
STT_COMPUTE_TYPE=int8
```

- **Pros**: No VRAM used, stable, CPU is idle (i3-9100F has 4 cores)
- **Cons**: Slower (200-500ms per sentence)
- **Use Case**: Conservative Path ✅

#### GPU Inference
```bash
STT_DEVICE=cuda
STT_COMPUTE_TYPE=int8
```

- **Pros**: 2-3x faster (100-200ms)
- **Cons**: Uses VRAM (0.5-1.5GB)
- **Use Case**: Modern Path with 4GB+ VRAM ✅

### Quantization

#### int8 (Quantized) - Recommended
```bash
STT_COMPUTE_TYPE=int8
```

- **Pros**: 75% smaller models, 2-3x faster, same accuracy
- **Cons**: Minimal (<1% accuracy difference)
- **VRAM**: 0.5-0.8GB per model
- **Speed**: 100-500ms per sentence
- **Quality**: Excellent (still 97-99% accuracy)

#### float32 (Full Precision)
```bash
STT_COMPUTE_TYPE=float32
```

- **Pros**: Maximum accuracy
- **Cons**: 4x larger, slower
- **VRAM**: 2-4GB per model
- **Speed**: Slower
- **Quality**: Slightly better (<1%)

## Performance

### Conservative Path (CPU)
- **Model**: tiny.en + int8
- **Device**: CPU
- **Latency**: 200-500ms per sentence
- **VRAM**: None
- **Accuracy**: 97%

### Modern Path (GPU)
- **Model**: base.en + int8
- **Device**: CUDA (GPU)
- **Latency**: 100-300ms per sentence
- **VRAM**: 0.8GB
- **Accuracy**: 99%

## Configuration Examples

### Budget Setup (Minimum VRAM)
```env
STT_MODEL=tiny.en
STT_DEVICE=cpu
STT_COMPUTE_TYPE=int8
```

- VRAM: None
- CPU: Moderate
- Latency: Slow (200-500ms)
- Accuracy: Good (97%)

### Balanced Setup (i3-9100F + 4GB)
```env
STT_MODEL=base.en
STT_DEVICE=cpu
STT_COMPUTE_TYPE=int8
```

- VRAM: None
- CPU: High (but 4-core i3 has capacity)
- Latency: Medium (100-300ms)
- Accuracy: Excellent (99%)

### Fast GPU Setup
```env
STT_MODEL=base.en
STT_DEVICE=cuda
STT_COMPUTE_TYPE=int8
```

- VRAM: 0.8GB
- CPU: Low
- Latency: Fast (100-200ms)
- Accuracy: Excellent (99%)

### Premium Setup
```env
STT_MODEL=small.en
STT_DEVICE=cuda
STT_COMPUTE_TYPE=float32
```

- VRAM: 1.5-2GB
- CPU: Low
- Latency: Very fast (50-150ms)
- Accuracy: Premium (99.5%)

## Advanced Configuration

### Multi-Language (Not Recommended)

Use full model (not .en variant) for multiple languages:

```env
STT_MODEL=base           # Instead of base.en
```

- Supports 99 languages
- Slower (2-3x)
- More VRAM
- Lower accuracy

**Recommendation**: Use `.en` variant for English-only deployment.

## Troubleshooting

### Poor Transcription

1. **Use better model**
   ```env
   STT_MODEL=base.en    # Instead of tiny.en
   ```

2. **Use GPU inference**
   ```env
   STT_DEVICE=cuda      # Instead of cpu
   ```

3. **Improve audio quality**
   - Use USB headset
   - Reduce background noise
   - Move closer to microphone

4. **Increase confidence**
   ```env
   STT_COMPUTE_TYPE=float32    # Instead of int8
   ```

### High Latency (>1 second)

1. **Use faster model**
   ```env
   STT_MODEL=tiny.en
   ```

2. **Use GPU**
   ```env
   STT_DEVICE=cuda
   ```

3. **Check CPU usage**
   - If >90%, reduce other processes
   - Close browser, IDEs, etc.

### Out of Memory (OOM)

1. **Use smaller model**
   ```env
   STT_MODEL=tiny.en
   ```

2. **Use CPU instead of GPU**
   ```env
   STT_DEVICE=cpu
   ```

3. **Use quantization**
   ```env
   STT_COMPUTE_TYPE=int8
   ```

## Seamless M4T (Modern Path Alternative)

For **Modern Path**, you can use Meta's Seamless M4T:

```bash
pip install audiocraft
```

**Advantages**:
- Faster (100-200ms)
- Multilingual
- Better on accents

**Disadvantages**:
- Requires 1.2GB VRAM
- More complex setup
- Not currently integrated

---

See [Models Overview](overview.md) for architecture overview.
