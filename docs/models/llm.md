# LLM: Language Model

Generates intelligent responses to user input.

## What is an LLM?

A Language Model takes text input and generates natural language output:

```
Input: "What's the weather?"
Output: "I don't have internet access, but I can tell you it's sunny outside..."
```

## Conservative Path: Ollama + Qwen 2.5

**Implementation**: `src/models/llm.py`

**Technology**: Local LLM via Ollama
- Small 0.5B parameter model
- Runs on CPU or GPU
- Good quality for basic conversations
- Fast inference (400-600ms)

### Setup

1. **Install Ollama**: https://ollama.ai
2. **Start Ollama service**:
   ```bash
   ollama serve
   # Runs on http://localhost:11434
   ```

3. **Configure** in `.env`:
   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5:0.5b
   ```

### Configuration

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:0.5b
```

### Model Comparison

| Model | Size | VRAM | Speed | Quality | Use Case |
|-------|------|------|-------|---------|----------|
| `qwen2.5:0.5b` | 0.5B | 0.8GB | 400-600ms | Good | ✅ Conservative |
| `phi:latest` | 1.3B | 1.2GB | 200-400ms | Excellent | Balanced |
| `neural-chat:7b-v3` | 7B | 4GB+ | 100-200ms | Premium | Modern |

**Recommended**: `qwen2.5:0.5b` (best for 4GB GPU)

## Performance

### Conservative Path
- **Model**: Qwen 2.5 (0.5B)
- **Device**: CPU or GPU
- **Latency**: 400-600ms
- **VRAM**: 0.8GB
- **Quality**: Good (handles basic conversations)

### Modern Path
- **Model**: Phi 1.5 (1.3B, int8)
- **Device**: GPU
- **Latency**: 200-400ms
- **VRAM**: 1.8GB
- **Quality**: Excellent (nuanced responses)

## Ollama Model Selection

### Available Models

```bash
# Check available models
ollama list
```

### Downloading Models

```bash
# Conservative Path
ollama pull qwen2.5:0.5b

# Modern Path
ollama pull phi:latest
```

### Model Details

#### Qwen 2.5 (Conservative Path)
- **Size**: 0.5B parameters
- **VRAM**: 0.8GB
- **Speed**: 400-600ms per response
- **Quality**: Good for basic conversations
- **Use Case**: Budget-friendly, stable ✅

```env
OLLAMA_MODEL=qwen2.5:0.5b
```

#### Phi 1.5 (Modern Path)
- **Size**: 1.3B parameters
- **VRAM**: 1.8GB (with int8 quantization)
- **Speed**: 200-400ms per response
- **Quality**: Excellent, nuanced responses
- **Use Case**: Better quality, still local

```env
OLLAMA_MODEL=phi:latest
```

#### Neural-Chat (Advanced)
- **Size**: 7B parameters
- **VRAM**: 4GB+ (requires quantization)
- **Speed**: 100-200ms (with good GPU)
- **Quality**: Premium
- **Use Case**: Maximum quality (resource-intensive)

```env
OLLAMA_MODEL=neural-chat:7b-v3
```

## Advanced Configuration

### Memory Optimization

For models larger than available VRAM, Ollama automatically uses quantization:

```bash
# Smaller quantization (uses less VRAM)
ollama pull neural-chat:7b-v3-q4_0     # 4-bit quantization

# Larger quantization (better quality, more VRAM)
ollama pull neural-chat:7b-v3-q8_0     # 8-bit quantization
```

### System Prompts

You can customize system behavior (in code, not .env):

```python
from src.models.llm import LanguageModel

llm = LanguageModel()
response = llm.generate(
    user_input="What's the weather?",
    system_prompt="You are a helpful voice assistant. Keep responses short (1-2 sentences) for voice output."
)
```

### Temperature/Sampling

Control response randomness:

```python
# More random/creative (0.7-1.0)
response = llm.generate(user_input, temperature=0.8)

# More deterministic (0.0-0.3)
response = llm.generate(user_input, temperature=0.1)
```

## Troubleshooting

### "Connection refused" error

```
Error: Failed to connect to Ollama at http://localhost:11434
```

**Fix**: Start Ollama service:
```bash
ollama serve
```

### Slow responses (>2 seconds)

1. **Use faster model**
   ```env
   OLLAMA_MODEL=qwen2.5:0.5b   # Faster than 7B models
   ```

2. **Use GPU**
   - Check: `nvidia-smi`
   - Ollama uses GPU automatically if available

3. **Reduce response length**
   - Set temperature lower
   - Add length limit in code

### Poor response quality

1. **Use larger model**
   ```env
   OLLAMA_MODEL=phi:latest      # 1.3B instead of 0.5B
   ```

2. **Use higher temperature**
   ```python
   temperature=0.7   # More creative
   ```

3. **Add system prompt**
   ```python
   system_prompt="You are a helpful assistant..."
   ```

### Out of Memory (OOM)

1. **Use smaller model**
   ```env
   OLLAMA_MODEL=qwen2.5:0.5b
   ```

2. **Use quantization**
   ```bash
   ollama pull phi:latest-q4_0   # 4-bit quantized
   ```

3. **Reduce context length**
   - Limit conversation history
   - Only keep last 2-3 messages

## Alternative: Phi-1.5 (Modern Path)

For better performance with 4GB+ VRAM:

1. **Download quantized Phi**
   ```bash
   ollama pull phi:latest
   ```

2. **Configure**
   ```env
   OLLAMA_MODEL=phi:latest
   ```

3. **Expected**: 200-400ms per response, excellent quality

## Alternative: vLLM (Advanced)

For maximum speed with large models (requires 6GB+ VRAM):

```bash
pip install vllm
```

**Advantages**:
- 10-100x faster than standard inference
- Supports large models
- Better concurrency

**Disadvantages**:
- More complex setup
- Higher VRAM requirement
- Not integrated (requires code changes)

---

See [Models Overview](overview.md) for architecture overview.
