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

# SECURITY: Allowed directories (only D and E drives)
ALLOWED_DRIVES = ['D:', 'E:']
BLOCKED_OPERATIONS = [
    'delete', 'remove', 'rm', 'del', 'format', 'erase', 'wipe', 'destroy',
    'modify', 'edit', 'change', 'update', 'alter', 'overwrite', 'replace',
    'move', 'cut', 'copy to system', 'install', 'uninstall', 'registry',
    'system32', 'windows', 'program files', 'users', 'documents',
    'shutdown', 'restart', 'reboot', 'kill', 'taskkill', 'stop service'
]

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


def is_safe_operation(command):
    """Check if the command contains any blocked operations."""
    command_lower = command.lower()
    for blocked_op in BLOCKED_OPERATIONS:
        if blocked_op in command_lower:
            return False, f"Operation '{blocked_op}' is not allowed for security reasons."
    return True, ""


def is_allowed_path(file_path):
    """Check if the file path is in allowed directories (D: or E: drives only)."""
    if not file_path:
        return False

    # Convert to absolute path and normalize
    try:
        abs_path = os.path.abspath(file_path)
        drive = abs_path[:2].upper()
        return drive in ALLOWED_DRIVES
    except:
        return False


def safe_file_operation(operation_type, *args):
    """Safely perform file operations with security checks."""
    try:
        if operation_type == "rename":
            old_path, new_path = args

            # Check if both paths are in allowed directories
            if not is_allowed_path(old_path):
                return False, f"Access denied: '{old_path}' is not in allowed directories (D: or E: drives only)."

            if not is_allowed_path(new_path):
                return False, f"Access denied: '{new_path}' is not in allowed directories (D: or E: drives only)."

            # Check if source file exists
            if not os.path.exists(old_path):
                return False, f"File '{old_path}' not found."

            # Check if destination already exists
            if os.path.exists(new_path):
                return False, f"File '{new_path}' already exists. Cannot rename."

            # Perform rename operation
            os.rename(old_path, new_path)
            return True, f"Successfully renamed '{old_path}' to '{new_path}'."

        elif operation_type == "create":
            file_path, content = args

            # Check if path is in allowed directories
            if not is_allowed_path(file_path):
                return False, f"Access denied: '{file_path}' is not in allowed directories (D: or E: drives only)."

            # Check if file already exists
            if os.path.exists(file_path):
                return False, f"File '{file_path}' already exists. Cannot overwrite existing files."

            # Create new file with content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Successfully created file '{file_path}'."

        elif operation_type == "list":
            directory_path = args[0] if args else "D:\\"

            # Check if directory is in allowed drives
            if not is_allowed_path(directory_path):
                return False, f"Access denied: '{directory_path}' is not in allowed directories (D: or E: drives only)."

            # List files in directory
            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                files = os.listdir(directory_path)
                return True, f"Files in '{directory_path}': {', '.join(files)}"
            else:
                return False, f"Directory '{directory_path}' not found or is not a directory."

    except Exception as e:
        return False, f"Error performing {operation_type} operation: {str(e)}"

    return False, "Unknown file operation."


def initialize_chat_sessions():
    """Initialize Gemini chat sessions with system context."""
    global action_chat, conversation_chat

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
        action_chat = model.start_chat(history=action_history)
        conversation_chat = model.start_chat(history=conversation_history)
        print("Secure Gemini chat sessions initialized successfully.")
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
    """Query Google Gemini API using chat sessions with security pre-check."""
    global action_chat, conversation_chat

    # Security check before sending to Gemini
    is_safe, safety_message = is_safe_operation(prompt)
    if not is_safe:
        return f"ACTION:CHAT:{safety_message}"

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
    """Open a specified application with security checks."""
    # List of safe applications
    safe_apps = {
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
    blocked_apps = [
        "cmd", "command prompt", "powershell", "regedit", "registry editor",
        "control panel", "settings", "task manager", "services", "system32"
    ]

    normalized_app_name = app_name.lower().strip()

    if normalized_app_name in blocked_apps:
        speak(f"I cannot open {app_name} for security reasons.")
        return

    if normalized_app_name in safe_apps:
        try:
            subprocess.run(safe_apps[normalized_app_name], shell=True, check=True)
            speak(f"Opening {normalized_app_name}.")
        except subprocess.CalledProcessError:
            speak(f"Failed to open {normalized_app_name}. The application might not be installed.")
        except Exception as e:
            speak(f"An error occurred while trying to open {normalized_app_name}: {e}")
    else:
        speak(
            f"I cannot open '{app_name}'. For security, I can only open approved applications like notepad, calculator, chrome, firefox, and media players.")


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


def get_current_time():
    """Tells the current time."""
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%A, %B %d, %Y")
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
    """Process the user's command using Gemini API for context and execute actions with security checks."""
    global listening

    if not command:
        return

    # Security pre-check
    is_safe, safety_message = is_safe_operation(command)
    if not is_safe:
        speak(safety_message)
        return

    # Check for immediate exit commands
    if command.lower() in ["exit", "quit", "stop listening"]:
        speak("Goodbye! Shutting down.")
        listening = False
        return

    # Basic greeting responses
    if any(word in command.lower() for word in ["hello", "hi", "hey", "namaste"]):
        speak("Hello! How can I help you safely today?")
        return

    if any(word in command.lower() for word in ["how are you", "कैसे हो"]):
        speak("I am functioning well and ready to assist you securely!")
        return

    if any(word in command.lower() for word in ["who are you", "तुम कौन हो"]):
        speak("I am Jarvis, your secure AI assistant, powered by Google Gemini with enhanced safety features.")
        return

    # Direct search command patterns (only when explicitly requested)
    if re.search(r"\b(search on google|google search|web search|खोज गूगल|गूगल खोज)\b", command.lower()):
        query = re.sub(r"\b(search|on|google|web|for|खोज|गूगल|पर|के|लिए|में)\b", "", command,
                       flags=re.IGNORECASE).strip()
        if query:
            web_search(query)
        else:
            speak("What would you like me to search for on Google?")
        return

    if re.search(r"\b(open|खोल|खोलो|start|शुरू)\b", command.lower()):
        app_name = re.sub(r"\b(open|खोल|खोलो|start|शुरू|करो|कर)\b", "", command, flags=re.IGNORECASE).strip()
        if app_name:
            open_app(app_name)
        else:
            speak("Which safe application would you like to open?")
        return

    if re.search(r"\b(time|समय|वक्त|what time|क्या समय)\b", command.lower()):
        get_current_time()
        return

    if re.search(r"\b(play music|play song|music|song|गाना|संगीत)\b", command.lower()):
        query = re.sub(r"\b(play|music|song|on|youtube|गाना|संगीत|बजाओ|चलाओ)\b", "", command,
                       flags=re.IGNORECASE).strip()
        if query:
            play_music_youtube(query)
        else:
            speak("What song would you like to play?")
        return

    # For complex commands, use Gemini for analysis
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
                speak("I need both a phone number and message to send WhatsApp.")
        elif action_type == "MUSIC":
            play_music_youtube(action_data)
        elif action_type == "RENAME":
            try:
                old_path, new_path = action_data.split(":", 1)
                success, message = safe_file_operation("rename", old_path.strip(), new_path.strip())
                speak(message)
            except ValueError:
                speak("I need both the old filepath and new filepath to rename a file in D: or E: drives.")
        elif action_type == "CREATE":
            try:
                file_path, content = action_data.split(":", 1)
                success, message = safe_file_operation("create", file_path.strip(), content.strip())
                speak(message)
            except ValueError:
                speak("I need both filepath and content to create a new file in D: or E: drives.")
        elif action_type == "LIST":
            success, message = safe_file_operation("list", action_data.strip() if action_data else "D:\\")
            speak(message)
        elif action_type == "TIME":
            get_current_time()
        elif action_type == "CHAT":
            speak(action_data)
        else:
            speak("I'm not sure how to safely handle that action.")
    else:
        # If no specific action identified, treat as conversation
        speak(gemini_response)


def main():
    """Main function to run the secure assistant."""
    global listening

    # Initialize Gemini chat sessions
    initialize_chat_sessions()

    print("Secure Jarvis AI Assistant started with enhanced safety features.")
    print("Security Features:")
    print("- File operations restricted to D: and E: drives only")
    print("- No destructive operations allowed (delete, format, etc.)")
    print("- No modification of existing files (only rename and create new)")
    print("- Blocked access to system directories and dangerous commands")
    print("- Safe application launching only")

    # Start continuous listening in a separate thread
    listen_thread = threading.Thread(target=continuous_listen, daemon=True)
    listen_thread.start()

    # Start text input handler in a separate thread
    text_thread = threading.Thread(target=text_input_handler, daemon=True)
    text_thread.start()

    print("\n--- Secure Assistant is ready! ---")
    print("Say 'Jarvis' followed by your command")
    print("Examples:")
    print("  General Knowledge: 'what is capital of India', 'tell me about Elon Musk'")
    print("  Web Search: 'search on google current weather', 'google search latest news'")
    print("  Apps: 'open notepad' (safe apps only)")
    print("  Music: 'play music bohemian rhapsody'")
    print("  Files: 'rename file D:\\old.txt to D:\\new.txt'")
    print("  Create: 'create file D:\\notes.txt with content Hello World'")
    print("  List: 'list files in D:\\MyFolder'")
    print("  Time: 'what time is it'")
    print("----------------------------\n")

    # Main command processing loop
    while listening:
        try:
            command = command_queue.get(timeout=0.5)
            if command == "exit":
                speak("Goodbye! Shutting down securely.")
                listening = False
                break

            process_command(command)

        except queue.Empty:
            if not listening:
                break
            continue
        except KeyboardInterrupt:
            speak("Goodbye! Shutting down securely.")
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

    print("Secure assistant has shut down.")
    if tts_engine:
        tts_engine.stop()


if __name__ == "__main__":
    main()