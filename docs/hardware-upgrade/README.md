# Hardware Upgrade Documentation Archive

This directory contains comprehensive planning and analysis documents for upgrading from **AMD E2-7110 (8GB RAM)** to **i3-9100F + GT 730 (4GB dedicated VRAM)**.

## Quick Links

### Getting Started
- **GT730_REAL_CONSTRAINTS.md** - Understanding your hardware limits (4GB dedicated VRAM only)
- **STACK_DECISION_MATRIX.md** - Compare conservative vs modern stack paths
- **GT730_UPDATE_SUMMARY.md** - Executive summary of recommendations

### Hardware Upgrade Guides
- **HARDWARE_UPGRADE_GUIDE.md** - Conservative path (proven, 4-5 hours)
- **GT730_MODERN_STACK.md** - Modern path (cutting-edge, 8-12 hours)
- **HARDWARE_UPGRADE_QUICK_REF.md** - Quick reference and troubleshooting

### Analysis & Planning
- **POCKET_TTS_ANALYSIS.md** - Piper vs Pocket-TTS comparison
- **UPGRADE_EXECUTIVE_SUMMARY.md** - Overview and timeline
- **HARDWARE_UPGRADE_DOC_INDEX.md** - Documentation navigation hub

## Which Path Should I Choose?

### Conservative Path (Proven)
**Best if**: You want something working quickly, minimal risk
- Stack: Silero VAD + Faster-Whisper + Ollama + Piper TTS
- Time: 4-5 hours
- Performance: 1.0-1.2s per turn
- Risk: Very Low

### Modern Path (Recommended)
**Best if**: You want best performance, have time for setup
- Stack: PyAnnote VAD + Seamless M4T + Phi-1.5 LLM + CoquiTTS
- Time: 8-12 hours
- Performance: 0.35-0.50s per turn (2.5-3x faster!)
- Risk: Low
- Memory: 3.6GB / 4GB VRAM

**Read**: STACK_DECISION_MATRIX.md for detailed comparison

## Key Constraint: 4GB Dedicated VRAM Only

⚠️ **Important**: Your GT 730 has:
- ✅ 4GB dedicated VRAM (for GPU/CUDA tasks)
- ❌ 10GB shared system RAM (CPU-only, not accessible to GPU)

NVIDIA CUDA kernels cannot use system RAM. Only the 4GB dedicated VRAM counts.

**Impact**: Use Phi-1.5 (2.5GB), not Mistral-7B (12-13GB)

## Implementation Roadmap

### Week 1: Setup & VAD
- Install PyTorch + CUDA 12.x
- Replace Silero with PyAnnote (95%+ accuracy)

### Week 2: STT Upgrade
- Replace Whisper with Seamless M4T (98-99% accuracy)

### Week 3: LLM Overhaul
- Replace Ollama with vLLM + Phi-1.5 (150-200ms response)

### Week 4: Framework & TTS
- Switch to FastAPI
- Integrate CoquiTTS (optional)

### Week 5: Testing & Deployment
- End-to-end testing
- Load testing (2-3 concurrent calls)
- Production deployment

## Performance Expectations

| Component | Conservative | Modern |
|-----------|--------------|--------|
| Latency | 1.0-1.2s | 0.35-0.50s |
| VAD Accuracy | 88% | 95%+ |
| STT Accuracy | 97% | 98-99% |
| LLM Speed | 400-600ms | 150-200ms |
| Memory | 2-3.5GB | 3.6GB / 4GB |
| Risk | Very Low | Low |
| Time | 4-5 hours | 8-12 hours |

## Main Implementation Code

The actual implementation is in the parent directories:
- `main.py` - Main application loop
- `core/` - Core modules (audio_io, config, state_manager)
- `models/` - Model modules (vad, stt, llm, tts)
- `integrations/` - GSM module integration

## Notes

- All documentation here is from the planning/analysis phase
- The actual code has been refactored for production use
- Refer to parent directory README.md for current setup instructions
- For GPU-specific issues, check GT730_REAL_CONSTRAINTS.md first

---

**Last Updated**: March 20, 2026
**Status**: Archive (planning docs for reference only)
