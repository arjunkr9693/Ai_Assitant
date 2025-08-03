"""
Command processor for Jarvis AI Assistant
Main logic for processing and routing user commands
"""

import re
from security_manager import SecurityManager
from gemini_handler import GeminiHandler
from commands import CommandExecutor

class CommandProcessor:
    def __init__(self, speech_handler):
        self.speech_handler = speech_handler
        self.gemini_handler = GeminiHandler()
        self.command_executor = CommandExecutor(speech_handler)

    def process_command(self, command):
        """Process the user's command using Gemini API for context and execute actions with security checks"""
        if not command:
            return

        # Security pre-check
        is_safe, safety_message = SecurityManager.is_safe_operation(command)
        if not is_safe:
            self.speech_handler.speak(safety_message)
            return

        # Check for immediate exit commands
        if command.lower() in ["exit", "quit", "stop listening"]:
            self.speech_handler.speak("Goodbye! Shutting down.")
            return "exit"

        # Basic greeting responses
        if any(word in command.lower() for word in ["hello", "hi", "hey", "namaste"]):
            self.speech_handler.speak("Hello! How can I help you safely today?")
            return

        if any(word in command.lower() for word in ["how are you", "कैसे हो"]):
            self.speech_handler.speak("I am functioning well and ready to assist you securely!")
            return

        if any(word in command.lower() for word in ["who are you", "तुम कौन हो"]):
            self.speech_handler.speak("I am Jarvis, your secure AI assistant, powered by Google Gemini with enhanced safety features.")
            return

        # Direct command patterns - return immediately if handled
        result = self._handle_direct_commands(command)
        if result is not None:  # Command was handled directly
            return result

        # For complex commands, use Gemini for analysis
        self.speech_handler.speak("Let me understand what you want to do...")
        gemini_response = self.gemini_handler.query_gemini(command, for_action_analysis=True)

        # Parse Gemini's action recommendation
        action_type, action_data = GeminiHandler.parse_gemini_action(gemini_response)

        if action_type:
            self._execute_action(action_type, action_data)
        else:
            # If no specific action identified, treat as conversation
            self.speech_handler.speak(gemini_response)

    def _handle_direct_commands(self, command):
        """Handle direct command patterns that don't need Gemini analysis"""
        # Direct search command patterns (only when explicitly requested)
        if re.search(r"\b(search on google|google search|web search|खोज गूगल|गूगल खोज)\b", command.lower()):
            query = re.sub(r"\b(search|on|google|web|for|खोज|गूगल|पर|के|लिए|में)\b", "", command,
                           flags=re.IGNORECASE).strip()
            if query:
                self.command_executor.web_search(query)
            else:
                self.speech_handler.speak("What would you like me to search for on Google?")
            return "handled"  # Indicate command was handled

        if re.search(r"\b(open|खोल|खोलो|start|शुरू)\b", command.lower()):
            app_name = re.sub(r"\b(open|खोल|खोलो|start|शुरू|करो|कर)\b", "", command, flags=re.IGNORECASE).strip()
            if app_name:
                self.command_executor.open_app(app_name)
            else:
                self.speech_handler.speak("Which safe application would you like to open?")
            return "handled"  # Indicate command was handled

        if re.search(r"\b(time|समय|वक्त|what time|क्या समय)\b", command.lower()):
            self.command_executor.get_current_time()
            return "handled"  # Indicate command was handled

        if re.search(r"\b(play music|play song|music|song|गाना|संगीत)\b", command.lower()):
            query = re.sub(r"\b(play|music|song|on|youtube|गाना|संगीत|बजाओ|चलाओ)\b", "", command,
                           flags=re.IGNORECASE).strip()
            if query:
                self.command_executor.play_music_youtube(query)
            else:
                self.speech_handler.speak("What song would you like to play?")
            return "handled"  # Indicate command was handled

        # File operation patterns - handle directly if clear
        if re.search(r"\b(rename file|rename|move file)\b", command.lower()):
            # Extract old and new paths using regex
            rename_pattern = r"rename\s+(?:file\s+)?([^\s]+(?:\s+[^\s]+)*?)\s+to\s+([^\s]+(?:\s+[^\s]+)*)"
            match = re.search(rename_pattern, command.lower())
            if match:
                old_path = match.group(1).strip()
                new_path = match.group(2).strip()
                self.command_executor.execute_file_operation("rename", old_path, new_path)
                return "handled"

        if re.search(r"\b(create file|make file|new file)\b", command.lower()):
            # Extract file path and content
            create_pattern = r"create\s+(?:file\s+)?([^\s]+(?:\s+[^\s]+)*?)\s+(?:with\s+content\s+|containing\s+)(.+)"
            match = re.search(create_pattern, command.lower())
            if match:
                file_path = match.group(1).strip()
                content = match.group(2).strip()
                self.command_executor.execute_file_operation("create", file_path, content)
                return "handled"

        if re.search(r"\b(list files|show files|files in)\b", command.lower()):
            # Extract directory path
            list_pattern = r"(?:list\s+files\s+in\s+|show\s+files\s+in\s+|files\s+in\s+)([^\s]+(?:\s+[^\s]+)*)"
            match = re.search(list_pattern, command.lower())
            if match:
                directory = match.group(1).strip()
                self.command_executor.execute_file_operation("list", directory)
            else:
                self.command_executor.execute_file_operation("list", "D:\\")
            return "handled"

        return None  # Command not handled directly

    def _execute_action(self, action_type, action_data):
        """Execute the parsed action from Gemini"""
        if action_type == "SEARCH":
            self.command_executor.web_search(action_data)
        elif action_type == "OPEN":
            self.command_executor.open_app(action_data)
        elif action_type == "WHATSAPP":
            try:
                phone, message = action_data.split(":", 1)
                self.command_executor.send_whatsapp_message(phone.strip(), message.strip())
            except ValueError:
                self.speech_handler.speak("I need both a phone number and message to send WhatsApp.")
        elif action_type == "MUSIC":
            self.command_executor.play_music_youtube(action_data)
        elif action_type == "RENAME":
            try:
                old_path, new_path = action_data.split(":", 1)
                self.command_executor.execute_file_operation("rename", old_path.strip(), new_path.strip())
            except ValueError:
                self.speech_handler.speak("I need both the old filepath and new filepath to rename a file in D: or E: drives.")
        elif action_type == "CREATE":
            try:
                file_path, content = action_data.split(":", 1)
                self.command_executor.execute_file_operation("create", file_path.strip(), content.strip())
            except ValueError:
                self.speech_handler.speak("I need both filepath and content to create a new file in D: or E: drives.")
        elif action_type == "LIST":
            self.command_executor.execute_file_operation("list", action_data.strip() if action_data else "D:\\")
        elif action_type == "TIME":
            self.command_executor.get_current_time()
        elif action_type == "CHAT":
            self.speech_handler.speak(action_data)
        else:
            self.speech_handler.speak("I'm not sure how to safely handle that action.")