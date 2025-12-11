# Building Executables

This guide will help you create standalone executables that can run without Python installed.

## Prerequisites

1. Make sure you have all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Install PyInstaller (for building executables):
   ```bash
   pip install pyinstaller
   ```
   Or use the build requirements:
   ```bash
   pip install -r build_requirements.txt
   ```

## Quick Build (Recommended)

Run the automated build script:

```bash
python build_executables.py
```

This will create both executables in the `dist` folder:
- `TelegramAPI_Server.exe` - The API server (port 8000)
- `TelegramAPI_Frontend.exe` - The frontend server (port 8001)

## Manual Build

If you prefer to build manually:

### Build API Server:
```bash
pyinstaller --name TelegramAPI_Server --onefile --console main.py
```

### Build Frontend Server:
```bash
pyinstaller --name TelegramAPI_Frontend --onefile --console frontend.py
```

## Using the Executables

1. **Create a `.env` file** in the same folder as the executables with your Telegram credentials:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_SESSION_NAME=telegram_session
   ```

2. **First-time setup**: Run `TelegramAPI_Server.exe` first to authenticate with Telegram.
   - It will prompt you for a verification code
   - Enter the code sent to your Telegram app
   - If you have 2FA, enter your password

3. **Start the servers**:
   - Run `TelegramAPI_Server.exe` (starts API on port 8000)
   - Run `TelegramAPI_Frontend.exe` (starts frontend on port 8001)

4. **Open your browser** to `http://localhost:8001` or `http://127.0.0.1:8001`

## Important Notes

- The executables will be large (50-100MB) because they include Python and all dependencies
- The first run may be slower as files are extracted
- Keep the `.env` file secure and never share it
- The session file (`.session` file) will be created in the same directory as the executable
- Both executables need to be in the same folder (or you can create shortcuts)

## Troubleshooting

### "Module not found" errors
If you get import errors, you may need to add more hidden imports. Edit `build_executable.py` and add the missing module to the `hidden_imports` list.

### Antivirus warnings
Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive. You can:
- Add an exception for the executable
- Build from source code instead

### Large file size
The executables are large because they bundle Python. To reduce size:
- Use `--onedir` instead of `--onefile` (creates a folder with multiple files)
- Use UPX compression (if available)

## Distribution

To share the executables:
1. Copy both `.exe` files
2. Include a `.env.example` file (without real credentials)
3. Include a README with setup instructions
4. Users will need to create their own `.env` file with their credentials


