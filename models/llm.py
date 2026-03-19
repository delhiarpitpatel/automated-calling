import aiohttp
import json

class LocalLLM:
    def __init__(self, model_name="qwen2.5:0.5b"):
        self.url = "http://localhost:11434/api/chat"
        self.model_name = model_name
        self.system_prompt = (
            "You are a helpful, conversational AI phone agent. "
            "Keep your answers extremely concise, natural, and friendly. "
            "Never use emojis, formatting, or lists. Speak exactly as a human would on the phone."
        )
        # We will store the conversation history here later!
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    async def generate_response(self, user_text: str) -> str:
        """Sends the user's text to Ollama and returns the AI's response asynchronously."""
        
        # Add the user's new message to our context
        self.messages.append({"role": "user", "content": user_text})
        
        payload = {
            "model": self.model_name,
            "messages": self.messages,
            "stream": False # We will wait for the full sentence for now
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_reply = data["message"]["content"]
                        
                        # Save the AI's reply to the history
                        self.messages.append({"role": "assistant", "content": ai_reply})
                        
                        return ai_reply
                    else:
                        return "Sorry, my brain disconnected for a second."
        except Exception as e:
            print(f"\n[LLM Error] {e}")
            return "I am having trouble thinking right now."
