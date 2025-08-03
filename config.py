"""
Configuration file for Jarvis AI Assistant
Contains all constants, API configurations, and security settings
"""

import os
import google.generativeai as genai

# SECURITY: Allowed directories (only D and E drives)
ALLOWED_DRIVES = ['D:', 'E:']

BLOCKED_OPERATIONS = [
    'delete', 'remove', 'rm', 'del', 'format', 'erase', 'wipe', 'destroy',
    'modify', 'edit', 'change', 'update', 'alter', 'overwrite', 'replace',
    'move', 'cut', 'copy to system', 'install', 'uninstall', 'registry',
    'system32', 'windows', 'program files', 'users', 'documents',
    'shutdown', 'restart', 'reboot', 'kill', 'taskkill', 'stop service'
]

# Safe applications that can be opened
SAFE_APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "chrome": "start chrome",
    "firefox": "start firefox",
    "explorer": "explorer",
    "vlc": "start vlc",
    "spotify": "start spotify",
    "discord": "start discord",
    "vscode": "code",
    "visual studio code": "code",
    "file manager": "explorer",
    "files": "explorer",
    "music": "start wmplayer",
    "media player": "start wmplayer"
}

# Blocked applications for security
BLOCKED_APPS = [
    "cmd", "command prompt", "powershell", "regedit", "registry editor",
    "control panel", "settings", "task manager", "services", "system32"
]

# TTS Settings
TTS_RATE = 150
TTS_VOLUME = 0.9

# Speech Recognition Settings
MICROPHONE_TIMEOUT = 1
PHRASE_TIME_LIMIT = 5
AMBIENT_NOISE_DURATION = 1

# Wake word
WAKE_WORD = "jarvis"


class GeminiConfig:
    """Handles Google Gemini API configuration"""

    def __init__(self):
        self.api_key = ""
        self.model = None
        self.action_chat = None
        self.conversation_chat = None
        self._load_api_key()
        self._configure_gemini()

    def _load_api_key(self):
        """Load API key from file"""
        try:
            with open("api_key.txt", "r") as f:
                self.api_key = f.read().strip()
            if not self.api_key:
                raise ValueError("API key not found in 'api_key.txt'. Please ensure it's not empty.")
        except FileNotFoundError:
            print("Error: 'api_key.txt' not found. Please create the file in the same directory as this script.")
            print("Inside 'api_key.txt', paste your Google Gemini API key as the only content.")
            exit()
        except ValueError as e:
            print(f"Configuration Error: {e}")
            print("Please ensure your Google Gemini API key is correctly pasted into 'api_key.txt'.")
            exit()

    def _configure_gemini(self):
        """Configure Gemini API"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def initialize_chat_sessions(self):
        """Initialize Gemini chat sessions with system context"""
        # Enhanced action analysis chat with strict security instructions
        action_history = [
            {
                "role": "user",
                "parts": [{
                    "text": """You are a SECURITY-FOCUSED AI assistant that analyzes user commands. CRITICAL SECURITY RULES:

1. NEVER suggest or perform ANY destructive operations (delete, remove, format, wipe, etc.)
2. File operations are ONLY allowed in D: and E: drives
3. ONLY allow file renaming and creating NEW files - NEVER modify existing file contents
4. NEVER suggest system operations (shutdown, restart, registry changes, etc.)
5. NEVER access system directories (C:, Windows, Program Files, etc.)

SMART ACTION DECISION:
- For general knowledge questions (capitals, history, science, explanations, definitions, etc.) → ACTION:CHAT:<direct_answer>
- For current events, live data, recent news → ACTION:SEARCH:<query>
- Only search if information is time-sensitive or requires real-time data

ALLOWED ACTIONS:
- Answer directly: ACTION:CHAT:<response> (for general knowledge, explanations, facts)
- Search web: ACTION:SEARCH:<query> (only for current/time-sensitive info)
- Open safe applications: ACTION:OPEN:<app_name>
- Send WhatsApp: ACTION:WHATSAPP:<phone>:<message>
- Play YouTube music: ACTION:MUSIC:<song/artist>
- Rename files (D:/E: only): ACTION:RENAME:<old_path>:<new_path>
- Create new files (D:/E: only): ACTION:CREATE:<file_path>:<content>
- List files (D:/E: only): ACTION:LIST:<directory_path>
- Get time: ACTION:TIME

Examples:
"What is capital of India?" → ACTION:CHAT:The capital of India is New Delhi.
"Tell me about Elon Musk" → ACTION:CHAT:[biographical information about Elon Musk]
"Current weather in Delhi" → ACTION:SEARCH:current weather Delhi
"Latest news today" → ACTION:SEARCH:latest news today

Always respond in the same language as user input."""}]
            },
            {
                "role": "model",
                "parts": [{
                    "text": "I understand. I will be smart about when to search vs chat. For general knowledge, facts, explanations, and stable information, I'll respond directly with ACTION:CHAT. I'll only use ACTION:SEARCH for current events, live data, or time-sensitive information. I'll strictly enforce all security rules and respond in the user's language."}]
            }
        ]

        # Conversation chat for natural dialogue
        conversation_history = [
            {
                "role": "user",
                "parts": [{
                    "text": "You are Jarvis, a helpful but SECURITY-CONSCIOUS AI assistant. You prioritize user safety and system security. Always respond in the same language as the user. You can discuss topics but will refuse to help with potentially harmful operations."}]
            },
            {
                "role": "model",
                "parts": [{
                    "text": "Hello! I'm Jarvis, your security-conscious AI assistant. I'm here to help you safely with various tasks while protecting your system. I'll respond in your preferred language. How can I assist you today?"}]
            }
        ]

        try:
            self.action_chat = self.model.start_chat(history=action_history)
            self.conversation_chat = self.model.start_chat(history=conversation_history)
            print("Secure Gemini chat sessions initialized successfully.")
            return True
        except Exception as e:
            print(f"Failed to initialize Gemini chat sessions: {e}")
            self.action_chat = None
            self.conversation_chat = None
            return False