import os
import tempfile
from gtts import gTTS
import streamlit as st


def text_to_speech(text, lang="hi", slow=False):
    """Convert text to speech using Google TTS.

    Args:
        text: Text to convert to speech
        lang: Language code ('hi' for Hindi, 'en' for English)
        slow: Speak slowly if True

    Returns:
        Path to generated audio file, or None on error
    """
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name
            tts.save(tmp_path)

        return tmp_path
    except Exception as e:
        st.error(f"Text-to-speech conversion failed: {str(e)}")
        return None


def text_to_speech_hinglish(text, slow=False):
    """Convert Hinglish text to speech.
    Uses Hindi TTS for Hinglish text since gTTS handles mixed language well.

    Args:
        text: Hinglish text
        slow: Speak slowly if True

    Returns:
        Path to audio file or None
    """
    return text_to_speech(text, lang="hi", slow=slow)


def get_audio_bytes(audio_path):
    """Read audio file and return bytes for playback.

    Args:
        audio_path: Path to audio file

    Returns:
        Audio bytes or None
    """
    try:
        with open(audio_path, "rb") as f:
            return f.read()
    except Exception as e:
        st.error(f"Failed to read audio file: {str(e)}")
        return None


def cleanup_audio(audio_path):
    """Remove temporary audio file.

    Args:
        audio_path: Path to audio file to remove
    """
    try:
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
    except Exception as e:
        st.warning(f"Failed to cleanup audio: {str(e)}")
