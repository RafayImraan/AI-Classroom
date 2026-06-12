import os
import tempfile
import streamlit as st

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


@st.cache_resource
def load_whisper_model(model_size="base"):
    """Load Whisper model once and cache it.

    Args:
        model_size: Model size - tiny, base, small, medium, large

    Returns:
        Loaded whisper model or None on failure
    """
    if not WHISPER_AVAILABLE:
        st.error(
            "openai-whisper is not installed. "
            "Install it with: pip install openai-whisper"
        )
        return None
    try:
        model = whisper.load_model(model_size)
        return model
    except Exception as e:
        st.error(f"Failed to load Whisper model '{model_size}': {str(e)}")
        return None


def transcribe_audio(audio_path, model_size="base"):
    """Transcribe an audio file using Whisper.

    Args:
        audio_path: Path to the audio file (WAV, MP3, M4A, OGG, etc.)
        model_size: Whisper model size to use

    Returns:
        dict with keys:
            text: Transcribed text
            language: Detected language code (e.g. 'hi', 'en')
        or None on error
    """
    model = load_whisper_model(model_size)
    if model is None:
        return None

    try:
        result = model.transcribe(
            audio_path,
            task="transcribe",
            language=None,  # auto-detect language
            fp16=False,     # use float32 on CPU
        )
        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
        }
    except Exception as e:
        st.error(f"Whisper transcription failed: {str(e)}")
        return None


def transcribe_audio_bytes(audio_bytes, model_size="base"):
    """Transcribe raw audio bytes using Whisper.

    Writes bytes to a temp file, transcribes, then cleans up.

    Args:
        audio_bytes: Raw audio data
        model_size: Whisper model size

    Returns:
        dict with keys: text, language
        or None on error
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        return transcribe_audio(tmp_path, model_size)
    except Exception as e:
        st.error(f"Audio byte transcription failed: {str(e)}")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def transcribe_from_audio_file(uploaded_file, model_size="base"):
    """Transcribe an uploaded Streamlit audio file.

    Args:
        uploaded_file: Streamlit UploadedFile object
        model_size: Whisper model size

    Returns:
        Transcribed text string, or None on error
    """
    result = transcribe_audio_bytes(uploaded_file.getvalue(), model_size)
    if result:
        return result["text"]
    return None
