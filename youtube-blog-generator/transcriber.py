"""
Audio Transcription Module
Uses Groq Whisper API to transcribe audio files
"""
import os
import requests
import config

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file using Groq API (Whisper-large-v3).
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Transcribed text
    """
    if not config.has_groq():
        print("Groq API key not found, processing skipped.")
        return None
        
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}"
    }
    
    try:
        with open(audio_path, "rb") as file:
            files = {
                "file": (os.path.basename(audio_path), file, "audio/mpeg"),
                "model": (None, "whisper-large-v3"),
                "response_format": (None, "json"),
                "language": (None, "zh")  # Default to Chinese, or auto-detect if omitted
            }
            
            print(f"Transcribing audio: {audio_path}...")
            response = requests.post(url, headers=headers, files=files, timeout=300)
            
            if response.status_code != 200:
                print(f"Transcription failed: {response.text}")
                return None
                
            result = response.json()
            return result.get("text", "")
            
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None
