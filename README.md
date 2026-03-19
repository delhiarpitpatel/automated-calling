# Automated Calling: Local AI Voice Agent

A high-performance, end-to-end AI voice agent designed to run entirely on local hardware (optimized for AMD APU / 8GB RAM). This project enables zero-latency "Agentic" workflows without relying on any Cloud APIs.

## The Problem
Running a full voice-to-voice AI pipeline (VAD -> STT -> LLM -> TTS) usually requires massive GPU VRAM or expensive cloud subscriptions. On entry-level hardware like an AMD APU, high latency and hardware incompatibilities (like NNPACK errors or Linux audio routing) make a seamless conversation almost impossible.

## The Solution
I built this custom pipeline to solve these hardware constraints. By using highly optimized CPU models (int8 quantization and ONNX) and implementing low-level Linux audio hacks, this agent achieves sub-second response times on a standard laptop. It includes a built-in integration for n8n to turn voice commands into real-world business actions.

## Features
- Full Local Execution: No data leaves your machine.
- CPU Optimized: Specifically tuned for AMD E2-7110 / 8GB RAM environments.
- Low Latency: Sub-second voice activity detection and transcription.
- n8n Integration: Trigger webhooks and CRM workflows via voice.

## The Local Stack
- VAD: Silero VAD (CPU)
- STT: Faster-Whisper (tiny.en, int8)
- LLM: Ollama / Qwen 2.5 (0.5B)
- TTS: Piper TTS (ONNX)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/delhiarpitpatel/automated-calling.git
   cd automated-calling
   ```

3. Setup virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Download the Piper ONNX model:
   Place your .onnx and .json voice files in the models/voices/ directory.

## Usage
Run the core loop:
```bash
python main.py
```

## Engineering Hacks (The "Boss Battles")
- Static Bypass: Routed audio from a Google Meet call via a virtual loopback to bypass noisy internal laptop mics.
- Bluetooth Fix: Used Numpy to mathematically upsample 22.05kHz Piper audio to 44.1kHz in real-time to prevent Bluetooth stream drops.
- NNPACK Suppression: Hijacked OS file descriptors (FD2) to silence red PyTorch hardware warnings for a clean terminal.

## License
This project is licensed under the MIT License.

## Author
Arpit Patel
