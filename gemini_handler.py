"""
Gemini AI handler for Jarvis AI Assistant
Manages all AI interactions and response parsing
"""

from config import GeminiConfig
from security_manager import SecurityManager


class GeminiHandler:
    def __init__(self):
        self.config = GeminiConfig()
        self.initialized = self.config.initialize_chat_sessions()

    def query_gemini(self, prompt, for_action_analysis=False):
        """Query Google Gemini API using chat sessions with security pre-check"""
        # Security check before sending to Gemini
        is_safe, safety_message = SecurityManager.is_safe_operation(prompt)
        if not is_safe:
            return f"ACTION:CHAT:{safety_message}"

        if not self.initialized or not self.config.action_chat or not self.config.conversation_chat:
            return "ACTION:CHAT:Gemini API is not properly configured. Cannot perform intelligent responses."

        try:
            if for_action_analysis:
                response = self.config.action_chat.send_message(prompt)
            else:
                response = self.config.conversation_chat.send_message(prompt)

            return response.text.strip()

        except Exception as e:
            return f"ACTION:CHAT:Error querying Gemini: {e}"

    @staticmethod
    def parse_gemini_action(response):
        """Parse Gemini response for action commands"""
        if response.startswith("ACTION:"):
            parts = response.split(":", 2)
            if len(parts) >= 2:
                action_type = parts[1].upper()
                action_data = parts[2] if len(parts) > 2 else ""
                return action_type, action_data
        return None, response