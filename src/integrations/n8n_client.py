"""
n8n Webhook Integration Client

This module handles asynchronous webhook calls to n8n, a low-code workflow
automation platform. It's used to:
- Trigger business workflows based on voice commands (e.g., create CRM records)
- Log interactions for analytics
- Send data to external services without blocking the main voice loop

Key Design Decisions:
1. Async/Await: Uses asyncio to prevent blocking the voice agent
2. Fire-and-Forget: Webhook sends are non-blocking (asyncio.create_task)
3. Retry Logic: Implements exponential backoff for transient failures
4. Timeout Handling: Prevents hanging if n8n is unreachable
5. Graceful Degradation: Webhook failures don't crash the main loop

Usage:
    Set N8N_WEBHOOK_URL in your .env file to enable this integration.
    Example: N8N_WEBHOOK_URL=https://n8n.example.com/webhook/voice-agent

    The webhook will receive JSON payloads:
    {
        "user_input": "what's the weather",
        "ai_response": "The weather is sunny today.",
        "timestamp": "2026-03-20T10:30:00Z"
    }
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Optional

import aiohttp

from src.core import config

logger = logging.getLogger(__name__)


class N8nClient:
    """
    Async client for sending interactions to n8n webhooks.

    Attributes:
        webhook_url: The n8n webhook endpoint URL
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts for failed requests
        session: Optional aiohttp session (created on first use)
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        timeout: Optional[float] = None,
        retry_attempts: Optional[int] = None,
    ):
        """
        Initialize the n8n webhook client.

        Args:
            webhook_url: n8n webhook URL (defaults to config.N8N_WEBHOOK_URL)
            timeout: Request timeout in seconds (defaults to config.N8N_REQUEST_TIMEOUT)
            retry_attempts: Max retry attempts (defaults to config.N8N_RETRY_ATTEMPTS)

        Raises:
            ValueError: If webhook_url is empty or None
        """
        self.webhook_url = webhook_url or config.N8N_WEBHOOK_URL
        if not self.webhook_url:
            raise ValueError(
                "n8n webhook URL is not configured. "
                "Set N8N_WEBHOOK_URL in your .env file."
            )

        self.timeout = timeout or config.N8N_REQUEST_TIMEOUT
        self.retry_attempts = retry_attempts or config.N8N_RETRY_ATTEMPTS
        self.session: Optional[aiohttp.ClientSession] = None

        logger.info(f"✅ n8n client initialized (URL: {self.webhook_url})")

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Lazily create and return an aiohttp session.

        This pattern ensures we only create a session when needed and can
        properly manage its lifecycle (close on shutdown).

        Returns:
            aiohttp.ClientSession: Reusable session for HTTP requests
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def send_interaction(
        self,
        user_input: str,
        ai_response: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Send a user interaction to the n8n webhook.

        This method is designed to be fire-and-forget:
        - It retries on transient failures (timeouts, 5xx errors)
        - It logs warnings but does NOT raise exceptions
        - The main voice loop is never blocked waiting for the webhook

        Args:
            user_input: The user's speech (transcribed text)
            ai_response: The AI agent's response
            metadata: Optional dict with additional data (e.g., user_id, session_id)

        Returns:
            bool: True if the webhook succeeded, False if all retries failed
        """
        payload = {
            "user_input": user_input,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Merge in optional metadata
        if metadata:
            payload.update(metadata)

        logger.debug(f"📤 Sending to n8n: {json.dumps(payload, indent=2)}")

        # Retry loop with exponential backoff
        for attempt in range(1, self.retry_attempts + 1):
            try:
                session = await self._get_session()

                async with asyncio.timeout(self.timeout):
                    async with session.post(
                        self.webhook_url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    ) as response:
                        if response.status == 200:
                            logger.info(
                                "✅ n8n webhook succeeded "
                                f"(user: '{user_input[:30]}...')"
                            )
                            return True
                        elif 500 <= response.status < 600:
                            # Server error; retry is sensible
                            error_text = await response.text()
                            logger.warning(
                                f"⚠️  n8n server error ({response.status}): "
                                f"{error_text[:100]}... "
                                f"(Attempt {attempt}/{self.retry_attempts})"
                            )
                        else:
                            # Client error (4xx); don't retry
                            error_text = await response.text()
                            logger.error(
                                f"❌ n8n client error ({response.status}): "
                                f"{error_text[:100]}"
                            )
                            return False

            except asyncio.TimeoutError:
                logger.warning(
                    f"⏱️  n8n request timeout ({self.timeout}s) "
                    f"(Attempt {attempt}/{self.retry_attempts})"
                )
            except aiohttp.ClientError as e:
                logger.warning(
                    f"⚠️  n8n connection error: {e} "
                    f"(Attempt {attempt}/{self.retry_attempts})"
                )
            except Exception as e:
                logger.error(
                    f"❌ Unexpected error sending to n8n: {e}", exc_info=True
                )
                return False

            # Exponential backoff: 0.5s, 1s, 2s, etc.
            if attempt < self.retry_attempts:
                backoff_delay = 0.5 * (2 ** (attempt - 1))
                logger.debug(f"⏳ Waiting {backoff_delay}s before retry...")
                await asyncio.sleep(backoff_delay)

        # All retries exhausted
        logger.error(
            f"❌ n8n webhook failed after {self.retry_attempts} attempts. "
            f"Check your .env configuration and n8n server status."
        )
        return False

    async def close(self):
        """
        Gracefully close the aiohttp session.

        Call this during shutdown to prevent resource leaks.
        """
        if self.session:
            await self.session.close()
            logger.info("✅ n8n session closed")

    async def health_check(self) -> bool:
        """
        Verify the n8n webhook is reachable.

        This is useful for startup validation before the main loop starts.

        Returns:
            bool: True if the webhook is reachable, False otherwise
        """
        logger.info(f"🔍 Checking n8n webhook health: {self.webhook_url}")

        try:
            session = await self._get_session()

            async with asyncio.timeout(5.0):
                async with session.get(self.webhook_url) as response:
                    is_ok = response.status < 400
                    status_msg = "✅ reachable" if is_ok else "❌ returned error"
                    logger.info(f"n8n webhook {status_msg} ({response.status})")
                    return is_ok

        except asyncio.TimeoutError:
            logger.error("❌ n8n webhook timed out")
            return False
        except Exception as e:
            logger.error(f"❌ n8n health check failed: {e}")
            return False
