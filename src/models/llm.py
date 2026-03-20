"""
Large Language Model (LLM) Integration via Ollama

This module interfaces with Ollama (https://ollama.ai), a local LLM server
that runs models like Qwen, Llama, and Mistral entirely on CPU.

Architecture:
- Ollama Server: Runs on localhost:11434 (must be started separately)
- Model: Qwen 2.5 0.5B (500M parameters, ~300MB RAM)
- Format: REST API (JSON over HTTP)

Why Qwen 0.5B?
- Only 500M parameters (fits comfortably in 8GB RAM)
- Fast inference: 50-100 tokens/sec on AMD E2-7110
- Good quality: Trained on high-quality data
- Bilingual: English + Chinese (bonus for global agents)

Performance on AMD APU:
- First token latency: ~500ms (model initialization)
- Subsequent tokens: ~20-30ms each
- Context window: 2048 tokens (sufficient for phone conversations)
"""

import asyncio
import json
import logging
from typing import Optional

import aiohttp

from src.core import config

logger = logging.getLogger(__name__)


class LocalLLM:
    """
    Async client for Ollama Local LLM inference.

    This implementation maintains conversation history (context), allowing
    the LLM to reference previous exchanges. This makes conversations more
    natural and coherent.

    Attributes:
        url: Ollama API endpoint (e.g., http://localhost:11434/api/chat)
        model_name: LLM model identifier (e.g., "qwen2.5:0.5b")
        system_prompt: System message that defines the agent's personality
        messages: Conversation history (system + user/assistant pairs)
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize the LLM client with Ollama.

        Args:
            model_name: Model to use (defaults to config.OLLAMA_MODEL)
            base_url: Ollama server URL (defaults to config.OLLAMA_BASE_URL)
            timeout: Request timeout in seconds (defaults to config.OLLAMA_REQUEST_TIMEOUT)

        Raises:
            ValueError: If model_name or base_url are empty
        """
        self.model_name = model_name or config.OLLAMA_MODEL
        base_url = base_url or config.OLLAMA_BASE_URL
        self.timeout = timeout or config.OLLAMA_REQUEST_TIMEOUT

        if not self.model_name:
            raise ValueError("LLM model_name is required")
        if not base_url:
            raise ValueError("Ollama base_url is required")

        self.url = f"{base_url}/api/chat"

        # System prompt defines the agent's personality and constraints
        self.system_prompt = config.LLM_SYSTEM_PROMPT

        # Conversation history: maintained for context-aware responses
        # Format: [{"role": "system"/"user"/"assistant", "content": "..."}]
        self.messages = [{"role": "system", "content": self.system_prompt}]

        logger.info(f"✅ LLM initialized: {self.model_name} @ {base_url}")

    # Record device preference (informational). Ollama manages device
    # placement itself; expose this for clarity and potential future use.
    self.device = getattr(config, "GPU_MODE", "cpu")

    async def generate_response(self, user_text: str) -> str:
        """
        Generate an AI response to user input, maintaining conversation context.

        This method:
        1. Appends the user's input to the conversation history
        2. Sends all messages to Ollama (context-aware)
        3. Saves the AI response to history for future turns
        4. Implements timeout and error handling

        Args:
            user_text: The user's spoken input (transcribed)

        Returns:
            str: The AI agent's response (natural language text)

        Performance:
        - First token: ~500ms
        - Subsequent tokens: ~20-30ms each (streamed)
        - Total response time: 1-3 seconds for a typical turn

        Error Handling:
        - Timeout: Returns a friendly error message instead of crashing
        - Connection Error: Indicates if Ollama server is unreachable
        - Invalid Response: Handles malformed JSON gracefully
        """
        # Add the user's input to the conversation history
        self.messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self.model_name,
            "messages": self.messages,
            "stream": False,  # Wait for the complete response before returning
        }

        logger.debug(
            f"LLM input (history depth={len(self.messages)}): '{user_text[:50]}...'"
        )

        try:
            # Use aiohttp for async HTTP requests (doesn't block the event loop)
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(self.timeout):
                    async with session.post(
                        self.url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            ai_reply = data.get("message", {}).get("content", "")

                            if not ai_reply:
                                logger.warning(
                                    "Ollama returned empty response"
                                )
                                ai_reply = "I didn't understand that."
                            else:
                                # Save AI response to history for future context
                                self.messages.append(
                                    {"role": "assistant", "content": ai_reply}
                                )
                                logger.info(f"LLM response: '{ai_reply[:50]}...'")

                            # Prevent unbounded context growth
                            # Keep only last 20 turns (~4KB of context)
                            if len(self.messages) > 20:
                                self.messages = (
                                    [self.messages[0]]
                                    + self.messages[-19:]  # Keep system prompt
                                )
                                logger.debug(
                                    "Pruned conversation history to prevent OOM"
                                )

                            return ai_reply

                        else:
                            error_text = await response.text()
                            logger.error(
                                f"Ollama error ({response.status}): {error_text[:100]}"
                            )
                            return "Sorry, my brain disconnected for a second."

        except asyncio.TimeoutError:
            logger.error(
                f"LLM timeout ({self.timeout}s). "
                f"Check if Ollama is running: `ollama serve`"
            )
            return "I'm thinking, but it's taking longer than usual."

        except aiohttp.ClientConnectorError as e:
            logger.error(
                f"Cannot connect to Ollama at {self.url}. "
                f"Start it with: `ollama serve`"
            )
            return "I can't connect to my brain right now."

        except Exception as e:
            logger.error(f"Unexpected LLM error: {e}", exc_info=True)
            return "I am having trouble thinking right now."

    async def generate_streaming(self, user_text: str):
        """
        Asynchronously stream tokens from Ollama (if supported).

        Yields partial strings as they arrive. Falls back to `generate_response`
        if streaming is not supported or an error occurs.

        Usage:
            async for chunk in llm.generate_streaming("Hello"):
                print(chunk)
        """
        # Append user message to history (stream also uses full context)
        self.messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self.model_name,
            "messages": self.messages,
            "stream": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(self.timeout):
                    async with session.post(
                        self.url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    ) as resp:
                        if resp.status != 200:
                            text = await resp.text()
                            logger.error(f"LLM stream error {resp.status}: {text[:200]}")
                            # Fallback to non-streaming
                            yield await self.generate_response(user_text)
                            return

                        # Read chunked response. Ollama may use SSE or chunked JSON.
                        partial = ""
                        async for raw_chunk in resp.content.iter_any():
                            try:
                                chunk = raw_chunk.decode("utf-8")
                            except Exception:
                                chunk = str(raw_chunk)

                            # Normalize SSE lines (data: {...})
                            for line in chunk.splitlines():
                                line = line.strip()
                                if not line:
                                    continue
                                if line.startswith("data:"):
                                    line = line[len("data:"):].strip()

                                # Try to parse JSON content
                                try:
                                    obj = json.loads(line)
                                except Exception:
                                    # Not JSON — yield raw line
                                    partial += line
                                    yield line
                                    continue

                                # Ollama streaming payloads may include `message` updates
                                msg = obj.get("message") or obj.get("delta") or obj
                                if isinstance(msg, dict):
                                    content = msg.get("content") or msg.get("text")
                                    if content:
                                        # yield incremental content
                                        yield content
                                else:
                                    # Unknown format: yield the whole object
                                    yield json.dumps(obj)

                        # After streaming completes, try to record final assistant message
                        # Attempt to parse final JSON body if available
                        try:
                            final = await resp.json()
                            ai_reply = final.get("message", {}).get("content", "")
                            if ai_reply:
                                self.messages.append({"role": "assistant", "content": ai_reply})
                        except Exception:
                            pass

        except Exception as e:
            logger.error(f"Streaming failed, falling back: {e}", exc_info=True)
            # Fallback: return non-streaming response as single yield
            text = await self.generate_response(user_text)
            yield text

    def reset_context(self):
        """
        Clear conversation history (useful between calls or users).

        This resets the agent to its initial state while keeping the
        system prompt, so it still has the same personality.
        """
        self.messages = [{"role": "system", "content": self.system_prompt}]
        logger.info("✅ Conversation context reset")
