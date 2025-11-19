from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User, MessageReactions
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

load_dotenv()

app = FastAPI(title="Telegram Channel API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telegram API credentials from environment variables
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_session")

if not API_ID or not API_HASH:
    raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in environment variables")

# Initialize Telegram client
client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

# Helper function to extract reactions from a message
def extract_reactions(message) -> Optional[List]:
    """Extract reactions from a Telegram message"""
    try:
        if not message.reactions:
            return None
        
        reactions_list = []
        if isinstance(message.reactions, MessageReactions):
            # Check if results attribute exists
            if hasattr(message.reactions, 'results') and message.reactions.results:
                for reaction in message.reactions.results:
                    # Get emoji - can be a string emoji or a Document (custom emoji)
                    emoji_str = None
                    if hasattr(reaction, 'reaction'):
                        if hasattr(reaction.reaction, 'emoticon'):
                            emoji_str = reaction.reaction.emoticon
                        elif hasattr(reaction.reaction, 'document_id'):
                            # Custom emoji - use a placeholder or document ID
                            emoji_str = f"🎨{reaction.reaction.document_id}"
                        else:
                            # Try to get emoji from reaction object
                            emoji_str = str(reaction.reaction)
                    
                    if emoji_str and hasattr(reaction, 'count'):
                        reactions_list.append(ReactionModel(
                            emoji=emoji_str,
                            count=reaction.count
                        ))
        
        return reactions_list if reactions_list else None
    except Exception as e:
        # If reaction extraction fails, return None
        print(f"Warning: Could not extract reactions for message {message.id}: {e}")
        return None

# Translation function
def translate_russian_to_english(text: str) -> str:
    """
    Detects if text is in Russian and translates it to English.
    Returns original text if not Russian or if translation fails.
    """
    if not text or len(text.strip()) == 0:
        return text
    
    try:
        # Detect language
        detected_lang = detect(text)
        
        # If Russian detected, translate to English
        if detected_lang == 'ru':
            translator = GoogleTranslator(source='ru', target='en')
            translated = translator.translate(text)
            return translated
        else:
            return text
    except LangDetectException:
        # If language detection fails, try to translate anyway if it looks like Russian
        # (contains Cyrillic characters)
        if any('\u0400' <= char <= '\u04FF' for char in text):
            try:
                translator = GoogleTranslator(source='ru', target='en')
                translated = translator.translate(text)
                return translated
            except Exception:
                return text
    except Exception:
        # If translation fails, return original text
        return text

# Response models
class ReactionModel(BaseModel):
    emoji: str
    count: int

class MessageModel(BaseModel):
    id: int
    date: datetime
    text: str
    sender_id: Optional[int] = None
    sender_username: Optional[str] = None
    views: Optional[int] = None
    forwards: Optional[int] = None
    reactions: Optional[List[ReactionModel]] = None

class ChannelModel(BaseModel):
    id: int
    title: str
    username: Optional[str] = None
    participants_count: Optional[int] = None

@app.on_event("startup")
async def startup_event():
    """Initialize Telegram client on startup"""
    await client.start()
    if not await client.is_user_authorized():
        raise RuntimeError("Telegram client is not authorized. Please run setup script first.")

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect Telegram client on shutdown"""
    await client.disconnect()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Telegram Channel API", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "connected": client.is_connected()}

@app.get("/channels", response_model=List[ChannelModel])
async def list_channels():
    """
    List all channels/dialogs the user has access to
    """
    try:
        channels = []
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            if isinstance(entity, Channel):
                channel_info = ChannelModel(
                    id=entity.id,
                    title=entity.title,
                    username=entity.username,
                    participants_count=entity.participants_count if hasattr(entity, 'participants_count') else None
                )
                channels.append(channel_info)
        return channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing channels: {str(e)}")

@app.get("/channels/{channel_id}/messages", response_model=List[MessageModel])
async def get_messages(
    channel_id: int,
    limit: int = Query(default=50, ge=1, le=1000, description="Number of messages to retrieve"),
    offset_id: Optional[int] = Query(default=None, description="Offset message ID for pagination"),
    min_id: Optional[int] = Query(default=None, description="Minimum message ID to retrieve"),
    max_id: Optional[int] = Query(default=None, description="Maximum message ID to retrieve"),
    translate: bool = Query(default=True, description="Automatically translate Russian messages to English")
):
    """
    Get messages from a specific channel
    
    - **channel_id**: The ID of the channel (use /channels endpoint to find IDs)
    - **limit**: Number of messages to retrieve (1-1000)
    - **offset_id**: Message ID to start from (for pagination)
    - **min_id**: Minimum message ID to retrieve
    - **max_id**: Maximum message ID to retrieve
    """
    try:
        # Get the channel entity
        entity = await client.get_entity(channel_id)
        
        # Build kwargs for iter_messages, only including non-None values
        iter_kwargs = {"limit": limit}
        if offset_id is not None:
            iter_kwargs["offset_id"] = offset_id
        if min_id is not None:
            iter_kwargs["min_id"] = min_id
        if max_id is not None:
            iter_kwargs["max_id"] = max_id
        
        messages = []
        async for message in client.iter_messages(entity, **iter_kwargs):
            # Extract sender information
            sender_id = None
            sender_username = None
            if message.sender:
                if isinstance(message.sender, User):
                    sender_id = message.sender.id
                    sender_username = message.sender.username
                elif isinstance(message.sender, Channel):
                    sender_id = message.sender.id
                    sender_username = message.sender.username
            
            # Get message text
            text = message.message or ""
            if message.media and not text:
                text = f"[Media: {type(message.media).__name__}]"
            
            # Translate Russian to English if translate is enabled
            if translate:
                text = translate_russian_to_english(text)
            
            # Extract reactions
            reactions = extract_reactions(message)
            
            message_model = MessageModel(
                id=message.id,
                date=message.date,
                text=text,
                sender_id=sender_id,
                sender_username=sender_username,
                views=message.views,
                forwards=message.forwards,
                reactions=reactions
            )
            messages.append(message_model)
        
        return messages
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Channel not found: {str(e)}")
    except FloodWaitError as e:
        raise HTTPException(status_code=429, detail=f"Rate limited. Wait {e.seconds} seconds")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

@app.get("/channels/by-username/{username}/messages", response_model=List[MessageModel])
async def get_messages_by_username(
    username: str,
    limit: int = Query(default=50, ge=1, le=1000, description="Number of messages to retrieve"),
    offset_id: Optional[int] = Query(default=None, description="Offset message ID for pagination"),
    min_id: Optional[int] = Query(default=None, description="Minimum message ID to retrieve"),
    max_id: Optional[int] = Query(default=None, description="Maximum message ID to retrieve"),
    translate: bool = Query(default=True, description="Automatically translate Russian messages to English")
):
    """
    Get messages from a channel by username (e.g., 'channelname' without @)
    
    - **username**: The username of the channel (without @)
    - **limit**: Number of messages to retrieve (1-1000)
    - **offset_id**: Message ID to start from (for pagination)
    - **min_id**: Minimum message ID to retrieve
    - **max_id**: Maximum message ID to retrieve
    """
    try:
        # Get the channel entity by username
        entity = await client.get_entity(username)
        
        # Build kwargs for iter_messages, only including non-None values
        iter_kwargs = {"limit": limit}
        if offset_id is not None:
            iter_kwargs["offset_id"] = offset_id
        if min_id is not None:
            iter_kwargs["min_id"] = min_id
        if max_id is not None:
            iter_kwargs["max_id"] = max_id
        
        messages = []
        async for message in client.iter_messages(entity, **iter_kwargs):
            # Extract sender information
            sender_id = None
            sender_username = None
            if message.sender:
                if isinstance(message.sender, User):
                    sender_id = message.sender.id
                    sender_username = message.sender.username
                elif isinstance(message.sender, Channel):
                    sender_id = message.sender.id
                    sender_username = message.sender.username
            
            # Get message text
            text = message.message or ""
            if message.media and not text:
                text = f"[Media: {type(message.media).__name__}]"
            
            # Translate Russian to English if translate is enabled
            if translate:
                text = translate_russian_to_english(text)
            
            # Extract reactions
            reactions = extract_reactions(message)
            
            message_model = MessageModel(
                id=message.id,
                date=message.date,
                text=text,
                sender_id=sender_id,
                sender_username=sender_username,
                views=message.views,
                forwards=message.forwards,
                reactions=reactions
            )
            messages.append(message_model)
        
        return messages
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Channel not found: {str(e)}")
    except FloodWaitError as e:
        raise HTTPException(status_code=429, detail=f"Rate limited. Wait {e.seconds} seconds")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

