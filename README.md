# AI Classroom Copilot 🤖🎙️

A voice-enabled AI teaching assistant for Indian government school classrooms. Teachers speak naturally in **Hinglish (Hindi + English)** and the AI generates educational content with voice and visual output.

---

## Problem Solved

Government school teachers in Haryana and across India face:
- **Large class sizes** (40+ students)
- **Limited teaching resources**
- **Need for engaging, visual content**
- **Language barriers** - students understand Hinglish better than pure English

AI Classroom Copilot bridges this gap by providing instant, voice-driven educational support.

---

## Features

### 1. Live Concept Simplification
- Voice input → Whisper transcription → AI explanation → Voice output
- Simple English explanations
- Hinglish explanations
- Real-life examples students can relate to
- Important points summary
- Visual learning suggestions

### 2. Voice-Triggered Quiz Generation
- Speak a topic → AI generates MCQ quiz
- Adjustable difficulty (easy/medium/hard)
- Multiple choice questions with explanations
- Answer checking with feedback

### 3. Textbook RAG (Retrieval-Augmented Generation)
- Upload school textbook PDFs
- AI retrieves relevant context from textbooks
- More accurate, curriculum-aligned responses

---

## Architecture

```
User speaks (Hinglish)
        │
        ▼
  ┌─────────────┐
  │   Whisper    │  Speech-to-Text
  └──────┬──────┘
         │ text
         ▼
  ┌─────────────┐
  │   Gemini     │  AI Processing
  │     LLM      │
  └──────┬──────┘
         │ response
         ▼
  ┌─────────────┐
  │    gTTS      │  Text-to-Speech
  └──────┬──────┘
         │ audio
         ▼
  ┌─────────────┐
  │  Streamlit   │  Display + Playback
  └─────────────┘

Optional: Textbook PDFs → FAISS Vector DB → RAG Context
```

---

## Tech Stack

| Component          | Technology                          |
| ------------------ | ----------------------------------- |
| Frontend           | Streamlit                           |
| Speech-to-Text     | OpenAI Whisper                      |
| AI / LLM           | Google Gemini (gemini-1.5-flash)    |
| Text-to-Speech     | Google gTTS                         |
| Vector Database    | FAISS (via LangChain)               |
| Embeddings         | sentence-transformers (all-MiniLM)  |
| PDF Parsing        | PyPDF2                              |

---

## Installation

### Prerequisites
- Python 3.10+
- FFmpeg (for audio processing)
- Google Gemini API key

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/ai-classroom-copilot.git
cd ai-classroom-copilot
```

### Step 2: Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up environment variables
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 5: Run the application
```bash
streamlit run app.py
```

---

## Deployment on Streamlit Cloud

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/ai-classroom-copilot.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path to `app.py`
6. Add secrets:
   - `GEMINI_API_KEY`: your Google Gemini API key
   - `WHISPER_MODEL_SIZE`: `base` (or `tiny` for faster performance)
7. Deploy!

### Whisper on Streamlit Cloud
Whisper requires significant memory. Use the `tiny` or `base` model:
```
WHISPER_MODEL_SIZE=tiny
```

---

## Speech-to-Text Pipeline (Whisper)

The app uses **OpenAI Whisper** for all speech recognition:

1. Teacher uploads or records audio
2. Audio file is saved temporarily
3. Whisper model transcribes audio to text
4. Language is auto-detected (Hindi/English/Hinglish)
5. Text is passed to Gemini LLM for processing
6. Temporary audio file is deleted

**Model caching:** The Whisper model is loaded once using Streamlit's `@st.cache_resource` and reused across sessions.

**Supported audio formats:** WAV, MP3, M4A, OGG

**Model sizes:**
| Model   | Speed  | Accuracy | Disk Size |
| ------- | ------ | -------- | --------- |
| tiny    | ~10x   | lowest   | ~150 MB   |
| base    | ~7x    | low      | ~300 MB   |
| small   | ~4x    | medium   | ~1.5 GB   |
| medium  | ~2x    | high     | ~3.5 GB   |
| large   | 1x     | highest  | ~6 GB     |

For Streamlit Cloud, `tiny` or `base` is recommended. Set via `WHISPER_MODEL_SIZE` env variable.

---

## Adding Textbook PDFs

1. Place PDF files in `data/textbooks/`
2. Open the app
3. Click **"Build Textbook Index"** in the sidebar
4. Enable **"Use Textbook Context (RAG)"**
5. Generate explanations with textbook context

---

## AI Prompt Design

### Explanation Prompt
The AI is instructed to:
- Act as a teacher for Indian government schools
- Use Hinglish (Hindi + English mix)
- Explain in simple language with examples
- Avoid difficult words
- Structure output with sections

### Quiz Prompt
The AI generates:
- Multiple choice questions
- 4 options per question
- Correct answer with Hinglish explanation
- Difficulty-appropriate content

---

## Project Structure

```
ai-classroom-copilot/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── utils/
│   ├── __init__.py
│   ├── speech.py          # Whisper speech-to-text
│   ├── llm.py             # Gemini API integration
│   ├── tts.py             # gTTS text-to-speech
│   ├── rag.py             # FAISS vector DB + PDF loading
│   └── prompts.py         # AI system prompts
└── data/
    └── textbooks/         # Place PDF textbooks here
        └── faiss_index/   # (auto-generated) Vector index
```

---

## License

MIT

---

## Contributors

Built for Haryana government schools to make quality education accessible to every child.
