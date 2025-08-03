# Jarvis AI Assistant

A secure, modular voice-controlled AI assistant powered by Google Gemini with enhanced safety features.

## 🏗️ Project Structure

```
jarvis-ai-assistant/
├── main.py                 # Main application entry point
├── config.py              # Configuration and constants
├── speech_handler.py      # Speech recognition and TTS
├── security_manager.py    # Security checks and file operations
├── gemini_handler.py      # AI response handling
├── commands.py            # System command execution
├── command_processor.py   # Main command processing logic
├── requirements.txt       # Project dependencies
├── api_key.txt           # Google Gemini API key (create this)
└── README.md             # This file
```

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
1. Get your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a file named `api_key.txt` in the project root
3. Paste your API key as the only content in the file

### 3. Run the Assistant
```bash
python main.py
```

## 🛡️ Security Features

- **Drive Restriction**: File operations limited to D: and E: drives only
- **Operation Blocking**: Prevents destructive operations (delete, format, etc.)
- **Safe Applications**: Only approved applications can be opened
- **System Protection**: Blocks access to system directories and dangerous commands
- **File Safety**: Only allows creating new files and renaming existing ones

## 🎯 Usage Examples

### Voice Commands
Say "Jarvis" followed by your command:

- **General Knowledge**: "What is the capital of India?"
- **Web Search**: "Search on Google current weather"
- **Open Apps**: "Open notepad"
- **Play Music**: "Play music bohemian rhapsody"
- **File Operations**: "Create file D:\\notes.txt with content Hello World"
- **Time**: "What time is it?"

### Text Commands
You can also type commands directly when prompted.

## 📁 Module Descriptions

### `main.py`
- Application entry point
- Coordinates all modules
- Manages main application loop and threading

### `config.py`
- Contains all configuration constants
- Manages Google Gemini API setup
- Defines security policies and safe applications

### `speech_handler.py`
- Handles speech recognition using Google Speech API
- Manages text-to-speech output with interruption capability
- Processes both voice and text input

### `security_manager.py`
- Implements all security checks
- Manages safe file operations
- Validates application access permissions

### `gemini_handler.py`
- Manages Google Gemini AI interactions
- Handles chat sessions and response parsing
- Processes natural language understanding

### `commands.py`
- Executes system commands safely
- Handles web searches, app launching, WhatsApp, YouTube
- Manages file operations through security layer

### `command_processor.py`
- Main command processing logic
- Routes commands to appropriate handlers
- Manages direct commands vs AI-analyzed commands

## 🔊 Supported Commands

### Direct Commands (No AI Processing)
- **Search**: "search on google [query]"
- **Apps**: "open [app_name]"
- **Time**: "what time is it"
- **Music**: "play music [song/artist]"

### AI-Analyzed Commands
- General knowledge questions
- Complex requests requiring context understanding
- File operations with natural language
- Multi-step instructions

### File Operations
- **Create**: "create file D:\\example.txt with content Hello"
- **Rename**: "rename file D:\\old.txt to D:\\new.txt"  
- **List**: "list files in D:\\MyFolder"

## 🚀 Features

- **Multilingual Support**: Responds in the same language as input
- **Continuous Listening**: Always ready for "Jarvis" wake word
- **Text Input Alternative**: Type commands when voice isn't available
- **TTS Interruption**: New commands interrupt ongoing speech
- **Safe Application Launching**: Only approved apps can be opened
- **Smart AI Routing**: Decides when to search vs use knowledge base

## 🛠️ Customization

### Adding New Safe Applications
Edit `SAFE_APPS` dictionary in `config.py`:
```python
SAFE_APPS = {
    "your_app": "command_to_run_app",
    # ... existing apps
}
```

### Modifying Security Settings
Update `BLOCKED_OPERATIONS` and `ALLOWED_DRIVES` in `config.py`:
```python
BLOCKED_OPERATIONS = [
    'your_blocked_operation',
    # ... existing operations
]
```

### Adjusting TTS Settings
Modify TTS parameters in `config.py`:
```python
TTS_RATE = 150      # Speech speed
TTS_VOLUME = 0.9    # Volume level
```

## 🔍 Troubleshooting

### Common Issues

1. **Speech Recognition Not Working**
   - Check microphone permissions
   - Install PyAudio: `pip install pyaudio`
   - Test microphone with other applications

2. **TTS Not Working**
   - Restart the application
   - Check system audio settings
   - Try: `pip install --upgrade pyttsx3`

3. **Gemini API Errors**
   - Verify `api_key.txt` contains valid API key
   - Check internet connection
   - Ensure API key has proper permissions

4. **Application Won't Open**
   - Verify application is installed
   - Check if application is in `SAFE_APPS` list
   - Run as administrator if necessary

### Debug Mode
Add debug prints in any module to trace execution flow.

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes maintaining the modular structure
4. Test security features thoroughly
5. Submit a pull request

## ⚠️ Security Notice

This assistant is designed with security in mind but should still be used responsibly:

- Only run on trusted systems
- Review code before modifications
- Keep API keys secure
- Monitor file operations
- Use in controlled environments

## 📄 License

This project is open source. Please maintain security features when modifying.