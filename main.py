import asyncio
import numpy as np
from core.audio_io import AudioInterface
from models.vad import VADetector
from models.stt import SpeechToText
from models.llm import LocalLLM
from models.tts import TextToSpeech  # <--- Import the Voice
from core import config

async def main():
    print("🚀 Initializing Full AI Agentic Pipeline...")
    
    audio_interface = AudioInterface()
    vad = VADetector()
    stt = SpeechToText()
    llm = LocalLLM(model_name="qwen2.5:0.5b") # Forcing Qwen for max speed
    tts = TextToSpeech() # <--- Initialize the Voice
    
    audio_interface.start_listening()
    print("🎙️ System Ready. Waiting for user input...")
    
    silence_counter = 0
    is_user_speaking = False
    audio_buffer = []
    
    try:
        while True:
            chunk = await audio_interface.audio_queue.get()
            
            if vad.is_speech(chunk):
                if not is_user_speaking:
                    print("\r🗣️  User speaking...                 ", end="", flush=True)
                    is_user_speaking = True
                silence_counter = 0 
            
            if is_user_speaking:
                audio_buffer.append(chunk)
                if not vad.is_speech(chunk):
                    silence_counter += 1
                
            if is_user_speaking and silence_counter > config.SILENCE_LIMIT_CHUNKS:
                # 1. STOP LISTENING so the AI doesn't hear itself talk
                audio_interface.is_listening = False 
                
                print("\r✅ Processing...", end="", flush=True)
                full_audio = np.concatenate(audio_buffer)
                
                # 2. Transcribe
                transcription = stt.transcribe(full_audio)
                print(f"\n📝 You: {transcription}")
                
                if len(transcription.strip()) > 2: # Ignore accidental coughs or 1-word static
                    print("🧠 Thinking...", end="", flush=True)
                    
                    # 3. Get LLM Reply
                    ai_response = await llm.generate_response(transcription)
                    print(f"\r🤖 Agent: {ai_response}")
                    
                    # 4. SPEAK!
                    tts.speak(ai_response)
                
                # 5. Reset and START LISTENING again
                is_user_speaking = False
                silence_counter = 0
                audio_buffer = []
                print("\n👂 Listening...")
                audio_interface.is_listening = True
                
            await asyncio.sleep(0.001) 
            
    except asyncio.CancelledError:
        pass
    finally:
        audio_interface.stop_listening()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down.")
