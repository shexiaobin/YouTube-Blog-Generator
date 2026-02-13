"""
Configuration management for YouTube Blog Generator
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Base paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
BLOGS_DIR = OUTPUT_DIR / "blogs"
AUDIO_DIR = OUTPUT_DIR / "audio"
ENV_FILE = BASE_DIR / ".env"

# Create directories
OUTPUT_DIR.mkdir(exist_ok=True)
BLOGS_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Custom API (OpenAI-compatible endpoint, highest priority)
CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "")
CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY", "")
CUSTOM_API_MODEL = os.getenv("CUSTOM_API_MODEL", "")

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# TTS Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "edge")  # "openai" or "edge"
TTS_VOICE = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")  # Edge TTS voice

# Summarizer Configuration
# Priority: custom > openai > gemini > groq > local
if CUSTOM_API_URL and CUSTOM_API_KEY:
    SUMMARIZER = os.getenv("SUMMARIZER", "custom")
elif OPENAI_API_KEY:
    SUMMARIZER = os.getenv("SUMMARIZER", "openai")
elif GEMINI_API_KEY:
    SUMMARIZER = os.getenv("SUMMARIZER", "gemini")
elif GROQ_API_KEY:
    SUMMARIZER = os.getenv("SUMMARIZER", "groq")
else:
    SUMMARIZER = os.getenv("SUMMARIZER", "local")

# OAuth session storage (in-memory)
_oauth_token = None


def get_oauth_token():
    return _oauth_token


def set_oauth_token(token):
    global _oauth_token
    _oauth_token = token


def clear_oauth_token():
    global _oauth_token
    _oauth_token = None


# Check if APIs are available
def has_custom_api():
    return bool(CUSTOM_API_URL) and bool(CUSTOM_API_KEY) and bool(CUSTOM_API_MODEL)

def has_openai():
    return bool(OPENAI_API_KEY)

def has_gemini():
    return bool(GEMINI_API_KEY) or (_oauth_token is not None)

def has_groq():
    return bool(GROQ_API_KEY)

def has_ai():
    return has_custom_api() or has_openai() or has_gemini() or has_groq()

def has_google_oauth():
    return bool(GOOGLE_CLIENT_ID) and bool(GOOGLE_CLIENT_SECRET)

def is_oauth_logged_in():
    return _oauth_token is not None


def mask_key(key: str) -> str:
    """Mask an API key for display, showing only first 4 and last 4 characters."""
    if not key or len(key) < 10:
        return "****" if key else ""
    return f"{key[:4]}****{key[-4:]}"


def update_env_file(updates: dict):
    """
    Update .env file with new key-value pairs.
    Creates the file if it doesn't exist.
    """
    env_content = {}

    # Read existing .env
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_content[k.strip()] = v.strip()

    # Apply updates (skip empty values)
    for k, v in updates.items():
        if v:  # Only write non-empty values
            env_content[k] = v

    # Write back
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        for k, v in env_content.items():
            f.write(f"{k}={v}\n")


def reload_config():
    """Reload configuration from .env file."""
    global OPENAI_API_KEY, GEMINI_API_KEY, GROQ_API_KEY
    global CUSTOM_API_URL, CUSTOM_API_KEY, CUSTOM_API_MODEL
    global GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    global TTS_ENGINE, TTS_VOICE, SUMMARIZER

    load_dotenv(override=True)

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "")
    CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY", "")
    CUSTOM_API_MODEL = os.getenv("CUSTOM_API_MODEL", "")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    TTS_ENGINE = os.getenv("TTS_ENGINE", "edge")
    TTS_VOICE = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")

    if CUSTOM_API_URL and CUSTOM_API_KEY:
        SUMMARIZER = os.getenv("SUMMARIZER", "custom")
    elif OPENAI_API_KEY:
        SUMMARIZER = os.getenv("SUMMARIZER", "openai")
    elif GEMINI_API_KEY:
        SUMMARIZER = os.getenv("SUMMARIZER", "gemini")
    elif GROQ_API_KEY:
        SUMMARIZER = os.getenv("SUMMARIZER", "groq")
    else:
        SUMMARIZER = os.getenv("SUMMARIZER", "local")
