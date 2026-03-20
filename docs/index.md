---
layout: default
title: Automated Calling - Local AI Voice Agent
---

# Automated Calling

A production-ready, end-to-end **fully-local AI voice agent** that runs on consumer hardware without cloud APIs or expensive subscriptions.

## Quick Links

- [📖 Quick Start](quickstart.md) - Get running in 5 minutes
- [🏗️ Architecture](architecture.md) - System design overview
- [⚙️ Configuration](configuration.md) - Setup guide
- [🧠 Models](models/overview.md) - Component deep dives
- [🔌 n8n Integration](integration/n8n.md) - Webhook setup
- [🔧 Engineering](engineering/overview.md) - Technical details
- [❓ Troubleshooting](troubleshooting.md) - Common issues

## Features

✅ **Full Local Execution** - No cloud APIs, no data sharing  
✅ **CPU Optimized** - Tuned for i3-9100F + GT 730 (4GB VRAM)  
✅ **Low Latency** - Sub-second response times  
✅ **n8n Compatible** - Webhook integration built-in  
✅ **Production Ready** - Error handling, logging, state management  

## Performance

### Conservative Path (Default)
- **Response Time**: 1.0-1.2s per turn
- **VRAM Required**: ~1.5GB
- **Status**: ✅ Production-Ready

### Modern Path (Advanced)
- **Response Time**: 0.35-0.50s per turn (2.5-3x faster)
- **VRAM Required**: ~3.6GB / 4GB
- **Status**: ✅ Stable, GPU-optimized

## Hardware

**Optimized For**: i3-9100F + GT 730 (4GB dedicated VRAM)

**Minimum**:
- Quad-core CPU (3.5+ GHz)
- 8GB RAM
- 2GB dedicated VRAM (Conservative Path)
- Microphone + Speakers

**Recommended**:
- 6+ core CPU
- 16GB RAM  
- 4GB dedicated VRAM
- USB headset

---

[View on GitHub](https://github.com/delhiarpitpatel/automated-calling)
