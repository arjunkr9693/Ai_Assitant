# import pyttsx3
# import logging
# import sys
#
# # Configure logging
# # Log to a file named 'tts_error.log'
# # Also log to console
# logging.basicConfig(
#     level=logging.ERROR,  # Set logging level to ERROR or INFO for more detail
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("tts_error.log"),
#         logging.StreamHandler(sys.stdout)  # This will print errors to the console
#     ]
# )
#
# try:
#     talk_engine = pyttsx3.init()
#
#     voices = talk_engine.getProperty('voices')
#
#     # Check if voices are available
#     if not voices:
#         logging.error("No voices found. Please check your text-to-speech engine installation.")
#         sys.exit(1)  # Exit if no voices are available
#
#     # Attempt to set the voice. Use a try-except for robustness.
#     try:
#         talk_engine.setProperty('voice', voices[0].id)
#         logging.info(f"Using voice: {voices[0].name} (ID: {voices[0].id})")
#     except Exception as e:
#         logging.error(f"Failed to set voice to voices[0].id: {e}")
#         # Fallback to default if setting a specific voice fails
#         logging.warning("Proceeding with default voice.")
#
#     talk_engine.setProperty('rate', 150)
#     logging.info(f"Set speech rate to: {talk_engine.getProperty('rate')}")
#
#     lines = [
#         'Welcome',
#         'How are you',
#         'I am good'
#     ]
#
#     for i, line in enumerate(lines):
#         try:
#             print(f"Attempting to speak: '{line}'")
#             logging.info(f"Calling say() for line {i + 1}: '{line}'")
#             talk_engine.say(line)
#
#             logging.info(f"Calling runAndWait() for line {i + 1}: '{line}'")
#             talk_engine.runAndWait()
#             logging.info(f"Finished speaking line {i + 1}: '{line}'")
#         except Exception as e:
#             logging.error(f"Error speaking line '{line}': {e}", exc_info=True)
#             # If an error occurs, you might want to try to stop and re-init the engine
#             # or skip to the next line depending on the desired behavior.
#             print(f"An error occurred while speaking '{line}'. Check tts_error.log for details.")
#             # Optionally, break the loop if a critical error occurs
#             # break
#
# except Exception as e:
#     logging.critical(f"An unhandled error occurred during engine initialization or main loop: {e}", exc_info=True)
#     print(f"A critical error occurred. Check tts_error.log for details.")
# finally:
#     # Ensure the engine is stopped gracefully
#     if 'talk_engine' in locals() and talk_engine is not None:
#         try:
#             talk_engine.stop()
#             logging.info("Text-to-speech engine stopped.")
#         except Exception as e:
#             logging.error(f"Error stopping the engine: {e}")



# import queue
# import threading
# import time
#
# from core.commands import CommandProcessor
#
#
# def main():
#     """Main function to run the assistant."""
#     processor = CommandProcessor()
#
#     # Print security notice
#     print("=" * 60)
#     print("SECURE JARVIS AI ASSISTANT - SECURITY RESTRICTIONS ACTIVE")
#     print("=" * 60)
#     print("SECURITY FEATURES:")
#     print("✓ File operations restricted to D: and E: drives only")
#     print("✓ Cannot delete, format, or perform destructive operations")
#     print("✓ Cannot modify existing file content (only rename)")
#     print("✓ Cannot access system directories (C:, Windows, etc.)")
#     print("✓ Cannot execute dangerous system commands")
#     print("✓ All commands are safety-checked before execution")
#     print("=" * 60)
#
#     # Start continuous listening in a separate thread
#     listen_thread = threading.Thread(target=processor.continuous_listen, daemon=True)
#     listen_thread.start()
#
#     # Start text input handler in a separate thread
#     text_thread = threading.Thread(target=processor.text_input_handler, daemon=True)
#     text_thread.start()
#
#     print("\n--- Secure Assistant is ready! ---")
#     print("Say 'Jarvis' followed by your command (e.g., 'Jarvis open notepad')")
#     print("Or, type your command below (e.g., 'what time is it', or 'exit' to quit)")
#     print("SAFE Examples:")
#     print("  - 'search for weather today'")
#     print("  - 'open chrome'")
#     print("  - 'play music bohemian rhapsody'")
#     print("  - 'what time is it'")
#     print("  - 'rename D:\\myfile.txt to D:\\newname.txt'")
#     print("  - 'create D:\\notes.txt with Hello World'")
#     print("  - 'send whatsapp message to +1234567890 saying hello'")
#     print("----------------------------\n")
#
#     # Main command processing loop
#     while processor.listening:
#         try:
#             command = processor.command_queue.get(timeout=0.5)
#             if command == "exit":
#                 processor.speech.speak("Goodbye! Shutting down securely.")
#                 processor.listening = False
#                 break
#
#             processor.process_command(command)
#
#         except queue.Empty:
#             if not processor.listening:
#                 break
#             continue
#         except KeyboardInterrupt:
#             processor.speech.speak("Goodbye! Shutting down securely.")
#             processor.listening = False
#             break
#         except Exception as e:
#             print(f"Error in main loop processing command: {e}")
#             continue
#
#     # Clean shutdown
#     if listen_thread.is_alive():
#         print("Waiting for listening thread to finish...")
#         listen_thread.join(timeout=2)
#     if text_thread.is_alive():
#         print("Waiting for text input thread to finish...")
#         text_thread.join(timeout=2)
#
#     print("Secure Assistant has shut down.")
#
# if __name__ == "__main__":
#     main()


import speech_recognition as sr
import pyttsx3
import webbrowser
import pywhatkit
import os
import subprocess
from datetime import datetime
import threading
import time
import queue
import re
import google.generativeai as genai

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Queue for commands
command_queue = queue.Queue()

# Global flag for continuous listening
listening = True

# Global flag for TTS interruption
tts_interrupted = False
tts_active = False

# Google Gemini API configuration (API key is read from api_key.txt)
GEMINI_API_KEY = ""
try:
    with open("api_key.txt", "r") as f:
        GEMINI_API_KEY = f.read().strip()
    if not GEMINI_API_KEY:
        raise ValueError("API key not found in 'api_key.txt'. Please ensure it's not empty.")
except FileNotFoundError:
    print("Error: 'api_key.txt' not found. Please create the file in the same directory as this script.")
    print("Inside 'api_key.txt', paste your Google Gemini API key as the only content.")
    exit()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please ensure your Google Gemini API key is correctly pasted into 'api_key.txt'.")
    exit()

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Initialize chat sessions
action_chat = None
conversation_chat = None

# Set up text-to-speech voice properties
tts_engine.setProperty('rate', 150)  # Speed of speech
tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

# Threading lock for TTS to prevent conflicts
tts_lock = threading.Lock()

# Conversation context for Gemini
conversation_context = []


def initialize_chat_sessions():
    """Initialize Gemini chat sessions with system context."""
    global action_chat, conversation_chat

    # Action analysis chat with system instructions
    action_history = [
        {
            "role": "user",
            "parts": [{
                "text": "You are an AI assistant that analyzes user commands and determines appropriate actions. IMPORTANT: Always respond in the SAME LANGUAGE as the user's input. If user speaks in Hindi, respond in Hindi. If user speaks in English, respond in English. Based on the user's input, identify if they want to: 1. Search the web (respond with: ACTION:SEARCH:<query>) 2. Open an application (respond with: ACTION:OPEN:<app_name>) 3. Send WhatsApp message (respond with: ACTION:WHATSAPP:<phone>:<message>) 4. Play music on YouTube (respond with: ACTION:MUSIC:<song/artist>) 5. Rename a file (respond with: ACTION:RENAME:<old_name>:<new_name>) 6. Get current time (respond with: ACTION:TIME) 7. Just have a conversation (respond with: ACTION:CHAT:<your_response>) IMPORTANT: Never suggest or perform any delete, remove, or destructive operations. If the user asks for something potentially harmful, respond with: ACTION:CHAT:I cannot perform destructive operations for safety reasons. Always respond in the ACTION: format and in the same language as the user."}]
        },
        {
            "role": "model",
            "parts": [{
                "text": "I understand. I will analyze user commands and respond with the appropriate ACTION: format in the SAME LANGUAGE as the user input. If user speaks Hindi, I'll respond in Hindi. If user speaks English, I'll respond in English. I will identify whether they want to search, open apps, send messages, play music, rename files, get time, or have a conversation. I will never suggest destructive operations and will refuse harmful requests. I'm ready to analyze commands in any language."}]
        }
    ]

    # Conversation chat for natural dialogue
    conversation_history = [
        {
            "role": "user",
            "parts": [{
                "text": "You are Jarvis, a helpful AI assistant. Be conversational, friendly, and concise. IMPORTANT: Always respond in the SAME LANGUAGE as the user's input. If user speaks in Hindi, respond in Hindi. If user speaks in English, respond in English. If user speaks in any other language, respond in that language. Remember our conversation context and respond naturally to the user's questions and comments in their preferred language."}]
        },
        {
            "role": "model",
            "parts": [{
                "text": "Hello! I'm Jarvis, your AI assistant. I'm here to help you with various tasks and have conversations. I'll remember our discussion and provide helpful, natural responses in whatever language you prefer to use. How can I assist you today?"}]
        }
    ]

    try:
        action_chat = model.start_chat(history=action_history)
        conversation_chat = model.start_chat(history=conversation_history)
        print("Gemini chat sessions initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Gemini chat sessions: {e}")
        action_chat = None
        conversation_chat = None


def interrupt_tts():
    """Interrupt the current TTS output."""
    global tts_interrupted, tts_engine
    if tts_active:
        tts_interrupted = True
        try:
            tts_engine.stop()
        except:
            pass


def speak(text):
    """Output text as speech and print to console with interruption capability."""
    global tts_engine, tts_interrupted, tts_active

    with tts_lock:
        print(f"Assistant: {text}")
        tts_interrupted = False
        tts_active = True

        try:
            # Split text into smaller chunks for better interruption responsiveness
            sentences = re.split(r'[.!?]+', text)

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                if tts_interrupted:
                    break

                tts_engine.say(sentence)
                tts_engine.runAndWait()

                # Small delay to check for interruption
                time.sleep(0.1)
                if tts_interrupted:
                    break

        except Exception as e:
            print(f"TTS Error: {e}. Attempting to reinitialize TTS engine...")
            # Reinitialize TTS engine if there's an error
            tts_engine = pyttsx3.init()
            tts_engine.setProperty('rate', 150)
            tts_engine.setProperty('volume', 0.9)
            # Try speaking again after reinitialization
            try:
                if not tts_interrupted:
                    tts_engine.say("I had a small glitch, but I'm back online.")
                    tts_engine.runAndWait()
                    if not tts_interrupted:
                        tts_engine.say(text)
                        tts_engine.runAndWait()
            except Exception as re_e:
                print(f"Failed to speak even after reinitialization: {re_e}")
        finally:
            tts_active = False
            tts_interrupted = False


def continuous_listen():
    """Continuously listen for voice commands in background."""
    global listening

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Continuous listening started. Say 'Jarvis' followed by your command...")

    while listening:
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                command = recognizer.recognize_google(audio).lower()

                # Check if command starts with wake word "jarvis"
                if command.startswith("jarvis"):
                    # Interrupt any ongoing TTS
                    interrupt_tts()

                    actual_command = command[6:].strip()
                    if actual_command:
                        print(f"Command detected: {actual_command}")
                        command_queue.put(actual_command)
                        time.sleep(0.1)

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            time.sleep(1)
        except Exception as e:
            print(f"Unexpected error in continuous listening: {e}")
            time.sleep(1)


def text_input_handler():
    """Handle text input in a separate thread."""
    global listening

    while listening:
        try:
            user_input = input("Type command (or 'exit' to quit): ").strip().lower()
            if user_input:
                if user_input in ["exit", "quit"]:
                    command_queue.put("exit")
                    break
                else:
                    # Interrupt any ongoing TTS when text command is received
                    interrupt_tts()
                    command_queue.put(user_input)
        except EOFError:
            print("EOF detected, exiting text input handler.")
            command_queue.put("exit")
            break
        except Exception as e:
            print(f"Text input error: {e}")
            time.sleep(0.1)


def query_gemini(prompt, for_action_analysis=False):
    """Query Google Gemini API using chat sessions."""
    global action_chat, conversation_chat

    if not action_chat or not conversation_chat:
        speak("Gemini API is not properly configured. Cannot perform intelligent responses.")
        return "I cannot respond intelligently without proper API configuration."

    try:
        if for_action_analysis:
            response = action_chat.send_message(prompt)
        else:
            response = conversation_chat.send_message(prompt)

        return response.text.strip()

    except Exception as e:
        speak(f"Error querying Gemini: {e}")
        return "There was an error with the Gemini API."


def web_search(query):
    """Perform a web search using the browser."""
    speak(f"Searching for {query} on Google.")
    webbrowser.open(f"https://www.google.com/search?q={query}")


def open_app(app_name):
    """Open a specified application."""
    app_paths = {
        "whatsapp": "start whatsapp",
        "notepad": "notepad",
        "explorer": "explorer",
        "calculator": "calc",
        "paint": "mspaint",
        "chrome": "start chrome",
        "firefox": "start firefox",
        "word": "start winword",
        "excel": "start excel",
        "powerpoint": "start powerpnt",
        "cmd": "start cmd",
        "command prompt": "start cmd",
        "control panel": "start control",
        "settings": "start ms-settings:",
        "vlc": "start vlc",
        "spotify": "start spotify",
        "discord": "start discord",
        "steam": "start steam",
        "vscode": "code",
        "visual studio code": "code",
        "photoshop": "start photoshop",
        "illustrator": "start illustrator",
        "teams": "start teams",
        "zoom": "start zoom",
        "file manager": "explorer",
        "files": "explorer",
        "music": "start wmplayer",
        "media player": "start wmplayer"
    }

    normalized_app_name = app_name.lower().strip()

    if normalized_app_name in app_paths:
        try:
            subprocess.run(app_paths[normalized_app_name], shell=True, check=True)
            speak(f"Opening {normalized_app_name}.")
        except subprocess.CalledProcessError:
            speak(
                f"Failed to open {normalized_app_name}. The application might not be installed or configured correctly.")
        except FileNotFoundError:
            speak(f"Failed to open {normalized_app_name}. Application not found.")
        except Exception as e:
            speak(f"An unexpected error occurred while trying to open {normalized_app_name}: {e}")
    else:
        speak(
            f"I don't know how to open '{app_name}'. I can open apps like notepad, calculator, chrome, firefox, word, excel, and many others.")


def send_whatsapp_message(phone, message):
    """Send a WhatsApp message using pywhatkit."""
    try:
        speak(f"Attempting to send WhatsApp message to {phone}.")
        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=15)
        speak("WhatsApp message automation initiated. Please check your browser to confirm sending.")
    except Exception as e:
        speak(f"Failed to send WhatsApp message: {e}. Make sure WhatsApp Web is logged in on your default browser.")


def play_music_youtube(query):
    """Play music from YouTube only."""
    if not query:
        speak("What song or artist would you like to play on YouTube?")
        return

    speak(f"Playing {query} on YouTube.")
    try:
        pywhatkit.playonyt(query)
    except Exception as e:
        speak(f"Failed to play music on YouTube: {e}")


def rename_file(old_name, new_name):
    """Rename a file in the current directory."""
    try:
        if os.path.exists(old_name):
            if os.path.exists(new_name):
                speak(f"A file named '{new_name}' already exists. Cannot rename.")
                return
            os.rename(old_name, new_name)
            speak(f"Successfully renamed '{old_name}' to '{new_name}'.")
        else:
            speak(f"File '{old_name}' not found in the current directory.")
    except Exception as e:
        speak(f"Failed to rename file: {e}")


def get_current_time():
    """Tells the current time in appropriate language."""
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%A, %B %d, %Y")

    # Simple language detection - if previous commands were in Hindi, respond in Hindi
    # For better implementation, you could maintain a language preference variable
    speak(f"The current time is {current_time} on {current_date}.")


def parse_gemini_action(response):
    """Parse Gemini response for action commands."""
    if response.startswith("ACTION:"):
        parts = response.split(":", 2)
        if len(parts) >= 2:
            action_type = parts[1].upper()
            action_data = parts[2] if len(parts) > 2 else ""
            return action_type, action_data
    return None, response


def process_command(command):
    """Process the user's command using Gemini API for context and execute actions."""
    global listening

    if not command:
        return

    # Check for immediate exit commands
    if command.lower() in ["exit", "quit", "stop listening"]:
        speak("Goodbye! Shutting down.")
        listening = False
        return

    # Basic greeting responses with language detection
    if any(word in command.lower() for word in
           ["hello", "hi", "hey", "namaste", "namaskar", "हैलो", "नमस्ते", "नमस्कार"]):
        if any(word in command.lower() for word in ["namaste", "namaskar", "नमस्ते", "नमस्कार"]):
            speak("नमस्ते! मैं आपकी कैसे सहायता कर सकता हूं?")
        else:
            speak("Hello! How can I help you today?")
        return

    if any(word in command.lower() for word in ["how are you", "कैसे हो", "कैसे हैं", "क्या हाल है"]):
        if any(word in command.lower() for word in ["कैसे हो", "कैसे हैं", "क्या हाल है"]):
            speak("मैं ठीक हूं और आपकी सहायता करने के लिए तैयार हूं!")
        else:
            speak("I am functioning well and ready to assist you!")
        return

    if any(word in command.lower() for word in ["who are you", "तुम कौन हो", "आप कौन हैं"]):
        if any(word in command.lower() for word in ["तुम कौन हो", "आप कौन हैं"]):
            speak("मैं जार्विस हूं, आपका व्यक्तिगत एआई सहायक, जो गूगल जेमिनी द्वारा संचालित है।")
        else:
            speak("I am Jarvis, your personal AI assistant, powered by Google Gemini.")
        return

    # Direct command patterns (for faster execution) with language support
    if re.search(r"\b(search|खोज|खोजो|ढूंढो)\b", command.lower()):
        query = re.sub(r"\b(search|for|google|खोज|खोजो|ढूंढो|गूगल|के|लिए|में)\b", "", command,
                       flags=re.IGNORECASE).strip()
        if query:
            web_search(query)
        else:
            if any(word in command.lower() for word in ["खोज", "खोजो", "ढूंढो", "गूगल"]):
                speak("आप क्या खोजना चाहते हैं?")
            else:
                speak("What would you like me to search for?")
        return

    if re.search(r"\b(open|खोल|खोलो|start|शुरू)\b", command.lower()):
        app_name = re.sub(r"\b(open|खोल|खोलो|start|शुरू|करो|कर)\b", "", command, flags=re.IGNORECASE).strip()
        if app_name:
            open_app(app_name)
        else:
            if any(word in command.lower() for word in ["खोल", "खोलो", "शुरू"]):
                speak("कौन सा एप्लिकेशन खोलना है?")
            else:
                speak("Which application would you like to open?")
        return

    if re.search(r"\b(time|samay|समय|वक्त|what time|क्या समय|कितना बजा)\b", command.lower()):
        get_current_time()
        return

    if re.search(r"\b(play music|play song|music|song|गाना|संगीत|म्यूजिक|बजाओ)\b", command.lower()):
        query = re.sub(r"\b(play|music|song|on|youtube|गाना|संगीत|म्यूजिक|बजाओ|चलाओ)\b", "", command,
                       flags=re.IGNORECASE).strip()
        if query:
            play_music_youtube(query)
        else:
            if any(word in command.lower() for word in ["गाना", "संगीत", "म्यूजिक", "बजाओ"]):
                speak("कौन सा गाना बजाना है?")
            else:
                speak("What song would you like to play?")
        return

    # For complex commands, use Gemini for analysis
    if any(word in command.lower() for word in
           ["मुझे", "समझ", "बताओ", "क्या", "कैसे", "कौन", "कहां", "खोज", "खोजो", "ढूंढो", "गूगल", "खोल", "खोलो", "बजाओ",
            "चलाओ", "गाना", "संगीत"]):
        speak("मैं समझने की कोशिश कर रहा हूं कि आप क्या चाहते हैं...")
    else:
        speak("Let me understand what you want to do...")

    gemini_response = query_gemini(command, for_action_analysis=True)

    # Parse Gemini's action recommendation
    action_type, action_data = parse_gemini_action(gemini_response)

    if action_type:
        if action_type == "SEARCH":
            web_search(action_data)
        elif action_type == "OPEN":
            open_app(action_data)
        elif action_type == "WHATSAPP":
            try:
                phone, message = action_data.split(":", 1)
                send_whatsapp_message(phone.strip(), message.strip())
            except ValueError:
                if any(word in command.lower() for word in ["whatsapp", "व्हाट्सएप", "मैसेज", "संदेश"]):
                    speak("व्हाट्सएप भेजने के लिए मुझे फोन नंबर और मैसेज दोनों चाहिए।")
                else:
                    speak("I need both a phone number and message to send WhatsApp. Please specify both.")
        elif action_type == "MUSIC":
            play_music_youtube(action_data)
        elif action_type == "RENAME":
            try:
                old_name, new_name = action_data.split(":", 1)
                rename_file(old_name.strip(), new_name.strip())
            except ValueError:
                if any(word in command.lower() for word in ["नाम", "बदल", "rename"]):
                    speak("फाइल का नाम बदलने के लिए मुझे पुराना और नया नाम दोनों चाहिए।")
                else:
                    speak("I need both the old filename and new filename to rename a file.")
        elif action_type == "TIME":
            get_current_time()
        elif action_type == "CHAT":
            speak(action_data)
        else:
            if any(word in command.lower() for word in ["समझ", "नहीं", "पता", "कैसे"]):
                speak("मुझे समझ नहीं आया कि यह कैसे करना है।")
            else:
                speak("I'm not sure how to handle that action.")
    else:
        # If no specific action identified, treat as conversation
        speak(gemini_response)


def main():
    """Main function to run the assistant."""
    global listening

    # Initialize Gemini chat sessions
    initialize_chat_sessions()

    # Removed the initial voice announcement - now only print to console
    print(
        "Jarvis AI Assistant started. I'm listening continuously for voice commands that start with 'Jarvis'. You can also type commands or type 'exit' to quit.")

    # Start continuous listening in a separate thread
    listen_thread = threading.Thread(target=continuous_listen, daemon=True)
    listen_thread.start()

    # Start text input handler in a separate thread
    text_thread = threading.Thread(target=text_input_handler, daemon=True)
    text_thread.start()

    print("\n--- Assistant is ready! ---")
    print("Say 'Jarvis' followed by your command (e.g., 'Jarvis open notepad')")
    print("Or, type your command below (e.g., 'what time is it', or 'exit' to quit)")
    print("Examples:")
    print("  - 'search for weather today'")
    print("  - 'open chrome'")
    print("  - 'play music bohemian rhapsody'")
    print("  - 'what time is it'")
    print("  - 'send whatsapp message to +1234567890 saying hello'")
    print("----------------------------\n")

    # Main command processing loop
    while listening:
        try:
            command = command_queue.get(timeout=0.5)
            if command == "exit":
                speak("Goodbye! Shutting down.")
                listening = False
                break

            process_command(command)

        except queue.Empty:
            if not listening:
                break
            continue
        except KeyboardInterrupt:
            speak("Goodbye! Shutting down.")
            listening = False
            break
        except Exception as e:
            print(f"Error in main loop processing command: {e}")
            continue

    # Clean shutdown
    if listen_thread.is_alive():
        print("Waiting for listening thread to finish...")
        listen_thread.join(timeout=2)
    if text_thread.is_alive():
        print("Waiting for text input thread to finish...")
        text_thread.join(timeout=2)

    print("Assistant has shut down.")
    if tts_engine:
        tts_engine.stop()


if __name__ == "__main__":
    main()