# Telegram Channel API

A REST API to list and pull messages from Telegram channels using FastAPI and Telethon.

## Setup

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Create a new application
4. Copy your `api_id` and `api_hash`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `env.example` to `.env` and fill in your credentials:

```bash
cp env.example .env
```

Edit `.env` and add your credentials:
```
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890  # Optional, with country code
```

### 4. Authenticate

Run the setup script to authenticate your Telegram account:

```bash
python setup_telegram.py
```

This will:
- Send a code to your Telegram app
- Prompt you to enter the code
- If 2FA is enabled, prompt for your password
- Save the session for future use

### 5. Start the API Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

#### `GET /`
Root endpoint - returns API information

#### `GET /health`
Health check endpoint

#### `GET /channels`
List all channels/dialogs the user has access to

**Response:**
```json
[
  {
    "id": 123456789,
    "title": "Channel Name",
    "username": "channelname",
    "participants_count": 1000
  }
]
```

#### `GET /channels/{channel_id}/messages`
Get messages from a channel by ID

**Parameters:**
- `channel_id` (path): Channel ID (get from `/channels` endpoint)
- `limit` (query, optional): Number of messages (1-1000, default: 50)
- `offset_id` (query, optional): Message ID to start from (pagination)
- `min_id` (query, optional): Minimum message ID
- `max_id` (query, optional): Maximum message ID

**Example:**
```
GET /channels/123456789/messages?limit=100
```

#### `GET /channels/by-username/{username}/messages`
Get messages from a channel by username

**Parameters:**
- `username` (path): Channel username without @ (e.g., `channelname`)
- `limit` (query, optional): Number of messages (1-1000, default: 50)
- `offset_id` (query, optional): Message ID to start from (pagination)
- `min_id` (query, optional): Minimum message ID
- `max_id` (query, optional): Maximum message ID

**Example:**
```
GET /channels/by-username/channelname/messages?limit=100
```

**Response:**
```json
[
  {
    "id": 123,
    "date": "2024-01-01T12:00:00",
    "text": "Message content",
    "sender_id": 987654321,
    "sender_username": "sender",
    "views": 1000,
    "forwards": 50
  }
]
```

## Usage Examples

### List all channels
```bash
curl http://localhost:8000/channels
```

### Get messages from a channel by ID
```bash
curl http://localhost:8000/channels/123456789/messages?limit=50
```

### Get messages from a channel by username
```bash
curl http://localhost:8000/channels/by-username/channelname/messages?limit=50
```

### Pagination example
```bash
# Get first 50 messages
curl http://localhost:8000/channels/123456789/messages?limit=50

# Get next 50 messages (starting from message ID 100)
curl http://localhost:8000/channels/123456789/messages?limit=50&offset_id=100
```

## Notes

- The API uses your personal Telegram account to access channels
- You must be a member of private channels to access their messages
- Rate limiting may apply - the API handles Telegram's rate limits automatically
- Session files are stored locally and should be kept secure
- Media messages are indicated with `[Media: TypeName]` in the text field

## Building Executables

You can create standalone executables that run without Python installed.

### Quick Build (Windows)

Double-click `build.bat` or run:
```bash
build.bat
```

### Manual Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_executables.py
   ```

This creates two executables in the `dist` folder:
- `TelegramAPI_Server.exe` - API server (port 8000)
- `TelegramAPI_Frontend.exe` - Frontend server (port 8001)

### Using the Executables

1. Create a `.env` file with your Telegram credentials (see Setup step 3)
2. Run `TelegramAPI_Server.exe` first to authenticate
3. Run `TelegramAPI_Frontend.exe` to start the web interface
4. Open `http://localhost:8001` in your browser

For detailed instructions, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

## Frontend

A web-based frontend is available at `frontend.py`. Start it with:
```bash
python frontend.py
```

Then open `http://localhost:8001` in your browser.

Features:
- Telegram-like dark theme UI
- Message bubbles with reactions
- Auto-refresh with configurable interval
- Channel selection and browsing
- Translator mode (online Google, offline Argos), 5000 char limit
- Supports Russian→English and Ukrainian→English (can add more with packs)

### Translator (online/offline)

- Online mode uses Google Translate via `deep_translator`
- Offline mode uses Argos Translate (requires language packs)
- Input limit: 5000 characters (UI enforces this with an error)

#### Install Argos Translate and language packs

Already in `requirements.txt`, but you need language packs for offline:
```bash
python -m argostranslate.package install https://raw.githubusercontent.com/argosopentech/argospm-index/main/ru_en.argosmodel
python -m argostranslate.package install https://raw.githubusercontent.com/argosopentech/argospm-index/main/uk_en.argosmodel
```

You can add other language pairs by installing their `.argosmodel` URLs from the Argos index.

#### Using the translator UI

1. Open the app and choose mode:
   - Viewer: channel browsing/messages
   - Translator: two text areas for input/output
2. In Translator mode:
   - Pick Online (Google) or Offline (Argos)
   - Choose language pair (Russian→English or Ukrainian→English)
   - Enter text (≤5000 chars) and click Translate
3. Offline mode will only work if the matching Argos language pack is installed.

## Security

- Never commit your `.env` file or session files to version control
- Keep your API credentials secure
- The session file allows access to your Telegram account

