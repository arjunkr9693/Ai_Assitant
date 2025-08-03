"""
Main entry point for Jarvis AI Assistant
Coordinates all modules and handles the main application loop
"""

import threading
import queue
from speech_handler import SpeechHandler
from command_processor import CommandProcessor


def main():
    """Main function to run the secure assistant"""

    # Initialize components
    speech_handler = SpeechHandler()
    command_processor = CommandProcessor(speech_handler)

    print("Secure Jarvis AI Assistant started with enhanced safety features.")
    print("Security Features:")
    print("- File operations restricted to D: and E: drives only")
    print("- No destructive operations allowed (delete, format, etc.)")
    print("- No modification of existing files (only rename and create new)")
    print("- Blocked access to system directories and dangerous commands")
    print("- Safe application launching only")

    # Start continuous listening in a separate thread
    listen_thread = threading.Thread(target=speech_handler.continuous_listen, daemon=True)
    listen_thread.start()

    # Start text input handler in a separate thread
    text_thread = threading.Thread(target=speech_handler.text_input_handler, daemon=True)
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
    while speech_handler.listening:
        try:
            command = speech_handler.command_queue.get(timeout=0.5)
            if command == "exit":
                speech_handler.speak("Goodbye! Shutting down securely.")
                speech_handler.listening = False
                break

            result = command_processor.process_command(command)
            if result == "exit":
                speech_handler.listening = False
                break

        except queue.Empty:
            if not speech_handler.listening:
                break
            continue
        except KeyboardInterrupt:
            speech_handler.speak("Goodbye! Shutting down securely.")
            speech_handler.listening = False
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
    speech_handler.stop_listening()


if __name__ == "__main__":
    main()