"""
Command execution module for Jarvis AI Assistant
Handles all system commands and integrations
"""

import webbrowser
import pywhatkit
import subprocess
from datetime import datetime
from security_manager import SecurityManager, FileManager


class CommandExecutor:
    def __init__(self, speech_handler):
        self.speech_handler = speech_handler

    def web_search(self, query):
        """Perform a web search using the browser"""
        self.speech_handler.speak(f"Searching for {query} on Google.")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    def open_app(self, app_name):
        """Open a specified application with security checks"""
        is_safe, result = SecurityManager.is_safe_app(app_name)

        if not is_safe:
            self.speech_handler.speak(result)
            return

        # result contains the command to execute
        command = result
        try:
            subprocess.run(command, shell=True, check=True)
            self.speech_handler.speak(f"Opening {app_name}.")
        except subprocess.CalledProcessError:
            self.speech_handler.speak(f"Failed to open {app_name}. The application might not be installed.")
        except Exception as e:
            self.speech_handler.speak(f"An error occurred while trying to open {app_name}: {e}")

    def send_whatsapp_message(self, phone, message):
        """Send a WhatsApp message using pywhatkit"""
        try:
            self.speech_handler.speak(f"Attempting to send WhatsApp message to {phone}.")
            pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=15)
            self.speech_handler.speak(
                "WhatsApp message automation initiated. Please check your browser to confirm sending.")
        except Exception as e:
            self.speech_handler.speak(
                f"Failed to send WhatsApp message: {e}. Make sure WhatsApp Web is logged in on your default browser.")

    def play_music_youtube(self, query):
        """Play music from YouTube only"""
        if not query:
            self.speech_handler.speak("What song or artist would you like to play on YouTube?")
            return

        self.speech_handler.speak(f"Playing {query} on YouTube.")
        try:
            pywhatkit.playonyt(query)
        except Exception as e:
            self.speech_handler.speak(f"Failed to play music on YouTube: {e}")

    def get_current_time(self):
        """Tells the current time"""
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_date = now.strftime("%A, %B %d, %Y")
        self.speech_handler.speak(f"The current time is {current_time} on {current_date}.")

    def execute_file_operation(self, operation_type, *args):
        """Execute file operations safely"""
        success, message = FileManager.safe_file_operation(operation_type, *args)
        self.speech_handler.speak(message)
        return success