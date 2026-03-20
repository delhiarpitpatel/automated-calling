"""
Conversation state management for the voice agent.

This module encapsulates the state of the current conversation:
- Whether the user is speaking
- Count of silent chunks (to detect end of speech)
- Audio buffer (accumulates chunks until speech ends)

By separating state into a dedicated class, we make the main loop cleaner
and enable easier testing and debugging.
"""


class StateManager:
    """Tracks the current state of user interaction and audio buffering."""

    def __init__(self):
        """Initialize conversation state."""
        self.is_user_speaking = False
        self.silence_counter = 0
        self.audio_buffer = []

    def reset(self):
        """Reset all state for the next user interaction."""
        self.is_user_speaking = False
        self.silence_counter = 0
        self.audio_buffer = []

    def __repr__(self):
        return (
            f"ConversationState(speaking={self.is_user_speaking}, "
            f"silence={self.silence_counter}, buffer_len={len(self.audio_buffer)})"
        )
