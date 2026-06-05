import os
import io
import asyncio
import edge_tts
import re

def normalize_punctuation(text: str) -> str:
    """
    Cleans up text for logs, but preserves terminal punctuation 
    for the TTS engine to ensure natural inflections.
    """
    text = text.replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

VOICE = "en-GB-SoniaNeural"

async def get_audio_bytes(text: str, voice: str = VOICE) -> io.BytesIO:
    """Generates TTS audio and returns it as a BytesIO stream for Streamlit."""
    optimized_text = normalize_punctuation(text)
    communicate = edge_tts.Communicate(optimized_text, voice, pitch="+0Hz", rate="+10%")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return io.BytesIO(audio_data)