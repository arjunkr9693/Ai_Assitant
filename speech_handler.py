"""
Speech handling module for Jarvis AI Assistant
Handles speech recognition, text-to-speech, and audio processing
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import re
import queue
from config import TTS_RATE, TTS_VOLUME, MICROPHONE_TIMEOUT, PHRASE_TIME_LIMIT, AMBIENT_NOISE_DURATION, WAKE_WORD

class SpeechHandler:
    def __init__(self):
        # Initialize speech recognition and text-to-speech
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()

        # TTS control flags
        self.tts_interrupted = False
        self.tts_active = False

        # Threading lock for TTS to prevent conflicts
        self.tts_lock = threading.Lock()

        # Queue for commands
        self.command_queue = queue.Queue()

        # Global flag for continuous listening
        self.listening = True

        # Setup TTS properties
        self._setup_tts()

    def _setup_tts(self):
        """Set up text-to-speech voice properties"""
        self.tts_engine.setProperty('rate', TTS_RATE)
        self.tts_engine.setProperty('volume', TTS_VOLUME)

    def interrupt_tts(self):
        """Interrupt the current TTS output"""
        if self.tts_active:
            self.tts_interrupted = True
            try:
                self.tts_engine.stop()
            except:
                pass

    def speak(self, text):
        """Output text as speech and print to console with interruption capability"""
        with self.tts_lock:
            print(f"Assistant: {text}")
            self.tts_interrupted = False
            self.tts_active = True

            try:
                # Split text into smaller chunks for better interruption responsiveness
                sentences = re.split(r'[.!?]+', text)

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    if self.tts_interrupted:
                        break

                    self.tts_engine.say(sentence)
                    self.tts_engine.runAndWait()

                    # Small delay to check for interruption
                    time.sleep(0.1)
                    if self.tts_interrupted:
                        break

            except Exception as e:
                print(f"TTS Error: {e}. Attempting to reinitialize TTS engine...")
                # Reinitialize TTS engine if there's an error
                self.tts_engine = pyttsx3.init()
                self._setup_tts()
                # Try speaking again after reinitialization
                try:
                    if not self.tts_interrupted:
                        self.tts_engine.say("I had a small glitch, but I'm back online.")
                        self.tts_engine.runAndWait()
                        if not self.tts_interrupted:
                            self.tts_engine.say(text)
                            self.tts_engine.runAndWait()
                except Exception as re_e:
                    print(f"Failed to speak even after reinitialization: {re_e}")
            finally:
                self.tts_active = False
                self.tts_interrupted = False

    def continuous_listen(self):
        """Continuously listen for voice commands in background"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)

        print(f"Continuous listening started. Say '{WAKE_WORD}' followed by your command...")

        while self.listening:
            try:
                with sr.Microphone() as source:
                    audio = self.recognizer.listen(source, timeout=MICROPHONE_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT)
                    command = self.recognizer.recognize_google(audio).lower()

                    # Check if command starts with wake word
                    if command.startswith(WAKE_WORD):
                        # Interrupt any ongoing TTS
                        self.interrupt_tts()

                        actual_command = command[len(WAKE_WORD):].strip()
                        if actual_command:
                            print(f"Command detected: {actual_command}")
                            self.command_queue.put(actual_command)
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

    def text_input_handler(self):
        """Handle text input in a separate thread"""
        while self.listening:
            try:
                user_input = input("Type command (or 'exit' to quit): ").strip().lower()
                if user_input:
                    if user_input in ["exit", "quit"]:
                        self.command_queue.put("exit")
                        break
                    else:
                        # Interrupt any ongoing TTS when text command is received
                        self.interrupt_tts()
                        self.command_queue.put(user_input)
            except EOFError:
                print("EOF detected, exiting text input handler.")
                self.command_queue.put("exit")
                break
            except Exception as e:
                print(f"Text input error: {e}")
                time.sleep(0.1)

    def stop_listening(self):
        """Stop all listening processes"""
        self.listening = False
        if self.tts_engine:
            self.tts_engine.stop()