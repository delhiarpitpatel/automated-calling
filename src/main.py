"""
Automated Calling: Main Application Loop

A production-ready voice agent that listens for speech, transcribes it,
generates intelligent responses, and speaks replies—all locally.

Usage:
    python -m src.main
"""

import asyncio
import logging
from typing import List

import numpy as np

from src.core.audio_io import AudioInterface
from src.core import config
from .models.vad import VADetector
from .models.stt import SpeechToText
from .models.llm import LocalLLM
from .models.tts import TextToSpeech

logger = logging.getLogger(__name__)

async def main() -> None:
    """
    Main application loop for the voice agent.
    
    Continuously:
    1. Listens for speech (VAD)
    2. Transcribes when silence detected (STT)
    3. Generates response (LLM)
    4. Speaks response (TTS)
    5. Returns to listening
    
    Raises:
        Exception: Any unhandled errors during initialization or main loop
    """
    try:
        logger.info("🚀 Initializing Full AI Agentic Pipeline...")
        print("🚀 Initializing Full AI Agentic Pipeline...")
        
        # Initialize all components
        audio_interface = AudioInterface()
        vad = VADetector()
        stt = SpeechToText()
        llm = LocalLLM(model_name=config.OLLAMA_MODEL)
        tts = TextToSpeech()
        
        audio_interface.start_listening()
        logger.info("✅ System Ready. Waiting for user input...")
        print("🎙️ System Ready. Waiting for user input...")
        
        silence_counter: int = 0
        is_user_speaking: bool = False
        audio_buffer: List[np.ndarray] = []
        
        while True:
            try:
                chunk = await audio_interface.audio_queue.get()
                
                # Detect speech
                if vad.is_speech(chunk):
                    if not is_user_speaking:
                        print("\r🗣️  User speaking...                 ", end="", flush=True)
                        is_user_speaking = True
                    silence_counter = 0
                
                # Buffer audio while speaking
                if is_user_speaking:
                    audio_buffer.append(chunk)
                    if not vad.is_speech(chunk):
                        silence_counter += 1
                
                # Process speech when silence detected
                if is_user_speaking and silence_counter > config.SILENCE_LIMIT_CHUNKS:
                    # Stop listening to prevent echo
                    audio_interface.is_listening = False
                    
                    print("\r✅ Processing...", end="", flush=True)
                    full_audio = np.concatenate(audio_buffer)
                    
                    # 1. Transcribe
                    try:
                        transcription = stt.transcribe(full_audio)
                        print(f"\n📝 You: {transcription}")
                        logger.info(f"Transcription: {transcription}")
                    except Exception as e:
                        logger.error(f"STT Error: {e}", exc_info=True)
                        print(f"\n❌ Transcription failed: {e}")
                        is_user_speaking = False
                        silence_counter = 0
                        audio_buffer = []
                        audio_interface.is_listening = True
                        continue
                    
                    # 2. Generate response (if input is valid)
                    if len(transcription.strip()) > 2:
                        try:
                            print("🧠 Thinking...", end="", flush=True)
                            ai_response = await llm.generate_response(transcription)
                            print(f"\r🤖 Agent: {ai_response}")
                            logger.info(f"LLM Response: {ai_response}")
                            
                            # 3. Speak response
                            try:
                                tts.speak(ai_response)
                                logger.info("TTS: Response spoken")
                            except Exception as e:
                                logger.error(f"TTS Error: {e}", exc_info=True)
                                print(f"\n❌ TTS failed: {e}")
                        except Exception as e:
                            logger.error(f"LLM Error: {e}", exc_info=True)
                            print(f"\n❌ LLM failed: {e}")
                    
                    # 4. Reset and restart listening
                    is_user_speaking = False
                    silence_counter = 0
                    audio_buffer = []
                    print("\n👂 Listening...")
                    audio_interface.is_listening = True
                
                await asyncio.sleep(0.001)
                
            except asyncio.CancelledError:
                logger.info("Main loop cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                print(f"\n❌ Unexpected error: {e}")
                continue
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        print("\n\n👋 Shutting down...")
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        print(f"\n❌ Critical error: {e}")
        raise
    finally:
        logger.info("Cleaning up resources...")
        try:
            audio_interface.stop_listening()
            logger.info("✅ Shutdown complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('automated_calling.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down.")
        logger.info("Application shutdown by user")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
