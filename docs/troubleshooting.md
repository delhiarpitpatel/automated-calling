# Troubleshooting

Common issues and solutions.

## Audio Issues

### Audio Device Not Found

**Error**: "No audio input device found" or "Invalid device ID"

**Solution**:
```bash
# Find your devices
python -m sounddevice
```

Look for your microphone and speakers in the list. Note the ID number.

Set in `.env`:
```env
INPUT_DEVICE=6    # Your microphone ID
OUTPUT_DEVICE=7   # Your speaker ID
```

### No Sound Output

**Problem**: Text-to-Speech runs but no audio from speakers

**Solutions**:
1. Check output device: `INPUT_DEVICE=0` (try default)
2. Check speaker volume: `alsamixer`
3. Check audio is not muted
4. Test with speaker directly: `speaker-test -t sine -f 1000 -l 1`

### Bluetooth Audio Dropouts

**Problem**: Audio cuts out on Bluetooth speaker

**Solution**: Enable upsampling in `.env`:
```env
UPSAMPLE_TTS_AUDIO=true
```

This converts 22.05kHz to 44.1kHz which Bluetooth prefers.

### Microphone Not Picking Up Voice

**Problem**: VAD detects nothing, or transcription is empty

**Solutions**:
1. Check mic is not muted (hardware switch)
2. Check OS volume: `alsamixer` (unmute, increase)
3. Increase VAD sensitivity: `VAD_THRESHOLD=0.6`
4. Try different microphone (USB headset better than laptop mic)
5. Test directly: `arecord -f S16_LE -r 16000 -d 5 test.wav`

## Performance Issues

### High Latency (>2 seconds per turn)

**Diagnosis**:
```bash
# Check CPU usage
htop
# Look for > 90% CPU on any core

# Check VRAM
nvidia-smi
# Check if out of memory
```

**Solutions**:

1. **Use faster STT model**
   ```env
   STT_MODEL=tiny.en    # Faster than base.en
   ```

2. **Use GPU for STT**
   ```env
   STT_DEVICE=cuda      # GPU is 2-3x faster
   ```

3. **Close other applications**
   - Browser, IDEs, media players
   - Free up CPU for transcription

4. **Use faster LLM**
   ```env
   OLLAMA_MODEL=qwen2.5:0.5b   # Fastest small model
   ```

5. **Increase silence detection** (wait longer before processing)
   ```env
   SILENCE_LIMIT_CHUNKS=45    # Wait ~1.5 seconds
   ```

### CPU Stuck at 100%

**Problem**: One core at 100%, slowing everything down

**Cause**: Either STT or LLM inference on CPU

**Solutions**:
1. Move STT to GPU: `STT_DEVICE=cuda`
2. Use smaller STT: `STT_MODEL=tiny.en`
3. Use smaller LLM: `OLLAMA_MODEL=qwen2.5:0.5b`

## Memory Issues

### Out of Memory (OOM)

**Error**: "CUDA out of memory" or "Cannot allocate memory"

**Check VRAM**:
```bash
nvidia-smi
```

**Solutions**:
1. **Use smaller STT model**
   ```env
   STT_MODEL=tiny.en      # Smaller than base.en
   STT_DEVICE=cpu         # Use CPU instead of GPU
   ```

2. **Use smaller LLM**
   ```env
   OLLAMA_MODEL=qwen2.5:0.5b   # 0.5B instead of 7B
   ```

3. **Use quantization**
   ```bash
   ollama pull phi:latest-q4_0   # 4-bit quantized version
   ```

4. **Disable other GPU applications**
   - Chrome, games, other ML
   - Only Automated Calling should use GPU

5. **Restart to clear memory**
   ```bash
   pkill -f "ollama|pytorch"
   # Wait 5 seconds
   ollama serve &
   ```

### System RAM Low (Laptop Becomes Slow)

**Problem**: Whole system slows down, not just Automated Calling

**Check RAM**:
```bash
free -h
htop    # Watch 'free' column
```

**Solutions**:
1. Close browser tabs (RAM hog)
2. Close IDEs and heavy applications
3. Reduce background services
4. Use smaller models (less context in memory)

## Transcription Quality Issues

### Poor Transcription (Wrong Words)

**Cause**: Model too small or audio quality

**Solutions**:

1. **Use larger STT model**
   ```env
   STT_MODEL=base.en      # Better than tiny.en
   ```

2. **Improve audio input**
   - Use USB headset (not laptop mic)
   - Reduce background noise
   - Move closer to microphone

3. **Use GPU inference**
   ```env
   STT_DEVICE=cuda
   STT_COMPUTE_TYPE=float32    # More accurate than int8
   ```

4. **Speak more clearly**
   - Reduce accent
   - Speak at normal pace
   - Avoid mumbling

### Model Doesn't Know Response

**Problem**: LLM says "I don't know" or gives bad answers

**Cause**: Model too small or bad input

**Solutions**:

1. **Use better LLM**
   ```env
   OLLAMA_MODEL=phi:latest    # Better than qwen2.5:0.5b
   ```

2. **Simplify questions**
   - Short, clear questions work better on small models
   - Avoid complex reasoning

3. **Add context in system prompt** (in code)
   ```python
   system_prompt="You are a helpful assistant. Keep answers short for voice output."
   ```

## n8n Integration Issues

### Webhook Not Receiving Calls

**Problem**: n8n webhook never triggered

**Debug**:
```bash
# Check webhook URL in .env
grep "N8N_WEBHOOK_URL" .env

# Test webhook with curl
curl -X POST http://localhost:5678/webhook/your-id \
  -H "Content-Type: application/json" \
  -d '{"user_input":"test","timestamp":"2026-03-20T10:30:00Z","confidence":0.95}'

# Check logs
grep "webhook" automated_calling.log
```

**Solutions**:
1. **Check n8n is running**: `curl http://localhost:5678`
2. **Check webhook URL is correct**: Copy from n8n exactly
3. **Check firewall**: `telnet localhost 5678`
4. **Check Automated Calling logs**: Full error message
5. **Restart services**: 
   ```bash
   pkill -f "n8n|ollama"
   sleep 5
   ollama serve &
   n8n start &
   python -m src.main
   ```

### Webhook Response Slow

**Problem**: n8n takes >5 seconds to respond

**Solutions**:
1. **Run n8n locally** (not cloud)
2. **Simplify workflow** (remove unnecessary nodes)
3. **Use async** (don't wait for webhook)
4. **Add timeout** (continue if webhook slow)

## Model Loading Issues

### "Model Not Found"

**Error**: "Could not load model: tiny.en"

**Solutions**:
1. **Check internet** (first run downloads models)
   ```bash
   ping huggingface.co
   ```

2. **Try manual download**
   ```bash
   python -c "from faster_whisper import WhisperModel; WhisperModel('tiny.en')"
   ```

3. **Check disk space**
   ```bash
   df -h
   # Need 5-10GB free
   ```

### Ollama Model Not Found

**Error**: "model 'qwen2.5:0.5b' not found"

**Solutions**:
1. **Pull model first**
   ```bash
   ollama pull qwen2.5:0.5b
   ```

2. **List available models**
   ```bash
   ollama list
   ```

3. **Check ollama is running**
   ```bash
   curl http://localhost:11434/api/tags
   ```

## Logging & Debugging

### Enable Debug Logging

```env
LOG_LEVEL=DEBUG
```

This shows detailed logs:
```
DEBUG: Loading VAD model...
DEBUG: Audio device opened (device 0)
DEBUG: Chunk received: 512 samples
DEBUG: VAD confidence: 0.92
DEBUG: Sending to STT...
...
```

### Check Logs

```bash
# View logs
tail -f automated_calling.log

# Search for errors
grep "ERROR" automated_calling.log

# Full trace with context
grep -A 3 -B 3 "your_error" automated_calling.log
```

### Test Individual Components

```bash
# Test VAD
python -c "from src.models.vad import VoiceActivityDetector; vad = VoiceActivityDetector(); print('VAD OK')"

# Test STT
python -c "from src.models.stt import SpeechToText; stt = SpeechToText(); print('STT OK')"

# Test LLM
python -c "from src.models.llm import LanguageModel; llm = LanguageModel(); print('LLM OK')"

# Test TTS
python -c "from src.models.tts import TextToSpeech; tts = TextToSpeech(); print('TTS OK')"
```

## Still Having Issues?

1. **Check logs**: `grep -i error automated_calling.log`
2. **Check hardware**: `nvidia-smi`, `lscpu`, `free -h`
3. **Verify config**: `cat .env`
4. **Test components**: Run individual component tests above
5. **Open GitHub issue**: https://github.com/delhiarpitpatel/automated-calling/issues

---

See [Configuration](configuration.md) for all options.
