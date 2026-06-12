import os
import streamlit as st
from dotenv import load_dotenv

from utils.speech import transcribe_from_audio_file, transcribe_audio
from utils.llm import generate_explanation, generate_quiz
from utils.tts import text_to_speech, text_to_speech_hinglish, get_audio_bytes, cleanup_audio
from utils.rag import get_rag_system, TextbookRAG

load_dotenv()

st.set_page_config(
    page_title="AI Classroom Copilot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
TTS_LANG = os.getenv("TTS_LANG", "hi")


UI = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, sans-serif; }

    .stApp { background: #F8F9FA; }

    .main > div { padding: 0.5rem 2rem 1.5rem 2rem; }

    .block-container { max-width: 1280px !important; padding-top: 0.8rem !important; }

    .header {
        background: linear-gradient(135deg, #0F2E59 0%, #1D3D68 100%);
        border-radius: 14px;
        padding: 2.2rem 2rem 1.8rem 2rem;
        margin-bottom: 1.8rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(15, 46, 89, 0.2);
    }
    .header h1 {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .header .subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.7);
        margin-top: 0.3rem;
        font-weight: 400;
        letter-spacing: 0.2px;
    }
    .header .pill {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.85);
        padding: 0.25rem 1.1rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        margin-top: 0.7rem;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1.3rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #D1D5DB;
    }
    .card-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #0F2E59;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-bottom: 0.1rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .card .micro-label {
        font-size: 0.72rem;
        color: #9CA3AF;
        margin-bottom: 0.9rem;
        font-weight: 400;
    }

    .crimson-btn button {
        background: #721C24 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1.2rem !important;
    }
    .crimson-btn button:hover { background: #5A0B16 !important; }
    .crimson-btn button:active { transform: scale(0.97) !important; }

    .blue-btn button {
        background: #0F2E59 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1.2rem !important;
    }
    .blue-btn button:hover { background: #1D3D68 !important; }

    .outline-btn button {
        background: transparent !important;
        color: #0F2E59 !important;
        border: 1.5px solid #CED4DA !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
    .outline-btn button:hover { border-color: #0F2E59 !important; }

    .stTextInput input, .stSelectbox select {
        border-radius: 8px !important;
        border: 1px solid #E9ECEF !important;
        background: #FFFFFF !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 0.8rem !important;
    }
    .stTextInput input:focus { border-color: #0F2E59 !important; box-shadow: 0 0 0 2px rgba(15,46,89,0.1) !important; }

    .stSlider > div { padding-top: 0.3rem; }
    .stSlider label { font-weight: 500 !important; font-size: 0.85rem !important; color: #374151 !important; }

    .stRadio > div { gap: 0.3rem; }
    .stRadio label { font-weight: 500 !important; font-size: 0.85rem !important; }

    .stCheckbox label { font-weight: 500 !important; font-size: 0.85rem !important; }

    .stFileUploader section {
        border-radius: 8px !important;
        border: 1.5px dashed #CED4DA !important;
        background: #F8F9FA !important;
        padding: 0.6rem !important;
    }

    .waveform {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 3px;
        height: 40px;
        margin: 0.5rem 0;
    }
    .waveform span {
        display: block;
        width: 3px;
        background: #721C24;
        border-radius: 2px;
        animation: wave 1.2s ease-in-out infinite;
    }
    .waveform span:nth-child(1) { height: 12px; animation-delay: 0s; }
    .waveform span:nth-child(2) { height: 24px; animation-delay: 0.1s; }
    .waveform span:nth-child(3) { height: 32px; animation-delay: 0.2s; }
    .waveform span:nth-child(4) { height: 20px; animation-delay: 0.3s; }
    .waveform span:nth-child(5) { height: 36px; animation-delay: 0.4s; }
    .waveform span:nth-child(6) { height: 28px; animation-delay: 0.5s; }
    .waveform span:nth-child(7) { height: 16px; animation-delay: 0.6s; }
    .waveform span:nth-child(8) { height: 30px; animation-delay: 0.7s; }
    .waveform span:nth-child(9) { height: 22px; animation-delay: 0.8s; }
    .waveform span:nth-child(10) { height: 34px; animation-delay: 0.9s; }
    .waveform span:nth-child(11) { height: 18px; animation-delay: 1.0s; }
    .waveform span:nth-child(12) { height: 26px; animation-delay: 1.1s; }

    @keyframes wave {
        0%, 100% { transform: scaleY(0.6); opacity: 0.5; }
        50% { transform: scaleY(1); opacity: 1; }
    }

    .segmented-control {
        display: flex;
        background: #F3F4F6;
        border-radius: 8px;
        padding: 3px;
        margin-bottom: 0.8rem;
    }
    .segmented-control button {
        flex: 1;
        border: none;
        background: transparent;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 500;
        color: #6B7280;
        cursor: pointer;
        transition: all 0.15s;
    }
    .segmented-control button.active {
        background: #FFFFFF;
        color: #0F2E59;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        font-weight: 600;
    }

    .toggle-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.35rem 0;
        border-bottom: 1px solid #F3F4F6;
    }
    .toggle-row:last-child { border-bottom: none; }
    .toggle-label { font-size: 0.85rem; font-weight: 500; color: #374151; display: flex; align-items: center; gap: 0.5rem; }
    .toggle-label .icon { font-size: 1rem; }

    .resource-item {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid #F3F4F6;
        font-size: 0.85rem;
        font-weight: 500;
        color: #374151;
    }
    .resource-item:last-child { border-bottom: none; }
    .resource-item .r-icon { font-size: 1.2rem; color: #0F2E59; }

    .results-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1.8rem;
        margin-top: 0.3rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #D1D5DB;
    }
    .results-card h2 {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0F2E59;
        margin-bottom: 1rem;
    }
    .section-label {
        font-size: 1rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 1.2rem 0 0.8rem 0;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        background: #0F2E59;
        border-bottom: 2px solid #0F2E59;
    }

    .quiz-question {
        background: #F0F4F8;
        border-radius: 10px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        border-left: 4px solid #0F2E59;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .quiz-question .q-num {
        display: inline-block;
        background: #0F2E59;
        color: #fff;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.15rem 0.6rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .quiz-question .q-text {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 0.8rem;
    }

    .success-box {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        color: #065F46;
        font-size: 0.82rem;
        font-weight: 500;
    }
    .error-box {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        color: #991B1B;
        font-size: 0.82rem;
        font-weight: 500;
    }
    .warning-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        color: #92400E;
        font-size: 0.82rem;
        font-weight: 500;
    }

    .footer {
        margin-top: 2rem;
        padding: 0.6rem 1rem;
        background: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #f0f0f0;
        font-size: 0.75rem;
        color: #9CA3AF;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .footer .deploy {
        background: #721C24;
        color: #fff;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
    }

    @media (max-width: 768px) {
        .header h1 { font-size: 1.6rem; }
        .main > div { padding: 0.5rem 1rem; }
    }
</style>
"""


def init_session_state():
    if "audio_input" not in st.session_state:
        st.session_state.audio_input = None
    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = ""
    if "ai_response" not in st.session_state:
        st.session_state.ai_response = None
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = None
    if "rag_context" not in st.session_state:
        st.session_state.rag_context = ""
    if "last_feature" not in st.session_state:
        st.session_state.last_feature = None


def handle_explanation(topic, grade_level, use_textbook):
    context = ""
    if use_textbook:
        rag = get_rag_system()
        if rag.is_index_available():
            context = rag.retrieve_context(topic)
            if context:
                st.session_state.rag_context = context

    result = generate_explanation(topic, grade_level, context=context)

    if result and result.get("success"):
        st.session_state.ai_response = result["text"]
        st.session_state.quiz_data = None
        st.session_state.last_feature = "Concept Explanation"
    else:
        st.session_state.ai_response = None
        st.error("Failed to generate explanation. Check your API key.")


def handle_quiz(topic, grade_level, difficulty, num_questions):
    questions = generate_quiz(topic, grade_level, difficulty, num_questions)

    if questions:
        st.session_state.quiz_data = questions
        st.session_state.ai_response = None
        st.session_state.last_feature = "Quiz Generator"
    else:
        st.session_state.quiz_data = None
        st.error("Failed to generate quiz. Check your API key and try again.")


def display_quiz(questions):
    for i, q in enumerate(questions, 1):
        st.markdown(
            f'<div class="quiz-question">'
            f'<span class="q-num">Q{i}</span>'
            f'<div class="q-text">{q["question"]}</div>',
            unsafe_allow_html=True,
        )
        options = q.get("options", [])
        correct = q.get("correct_answer", "")

        if options:
            selected = st.radio(
                "options",
                options,
                key=f"q_{i}",
                index=None,
                label_visibility="collapsed",
            )

            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Check", key=f"check_{i}", use_container_width=True):
                    if selected == correct:
                        st.markdown('<div class="success-box">Correct!</div>', unsafe_allow_html=True)
                    elif selected is None:
                        st.markdown('<div class="warning-box">Select an answer first</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">Incorrect. Answer: {correct}</div>', unsafe_allow_html=True)
            with c2:
                if st.button("Explain", key=f"explain_{i}", use_container_width=True):
                    explanation = q.get("explanation", "")
                    if explanation:
                        st.info(explanation)

        st.markdown("</div>", unsafe_allow_html=True)


def main():
    init_session_state()

    st.markdown(UI, unsafe_allow_html=True)

    st.markdown(
        '<div class="header">'
        '<h1>AI Classroom Copilot</h1>'
        '<div class="subtitle">Voice powered Hinglish teaching assistant</div>'
        '<div class="pill">For Haryana Government Schools</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">Lesson Setup</div>'
            '<div class="micro-label">Step 1: Set lesson topic and complexity</div>',
            unsafe_allow_html=True,
        )
        topic = st.text_input(
            "Topic",
            placeholder="photosynthesis",
            key="topic_input",
            label_visibility="collapsed",
        )

        st.markdown(
            "<div style='display:flex; justify-content:space-between; font-size:0.78rem; color:#6B7280; margin-top:0.2rem;'>"
            "<span>Easy</span><span>Medium</span><span>Hard</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        grade_level = st.slider(
            "Difficulty",
            min_value=1, max_value=12, value=5,
            key="grade_slider",
            label_visibility="collapsed",
        )
        st.markdown("<div style='font-size:0.72rem; color:#9CA3AF; margin-top:-0.3rem;'>Class level: " + str(grade_level) + "</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="card">'
            '<div class="card-title">Input Controls</div>'
            '<div class="micro-label">Step 2: Speak or upload your lesson topic</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="waveform">'
            + "".join(["<span></span>" for _ in range(12)])
            + "</div>",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="crimson-btn">', unsafe_allow_html=True)
        mic_col1, mic_col2 = st.columns([1, 3])
        with mic_col1:
            st.button("🎤", key="mic_btn")
        with mic_col2:
            st.markdown("<div style='font-size:0.82rem; color:#6B7280; padding-top:0.3rem;'>Click to record or upload below</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        audio_file = st.file_uploader(
            "Upload audio",
            type=["wav", "mp3", "m4a", "ogg"],
            help="Speak in Hindi, English, or Hinglish",
            label_visibility="collapsed",
        )
        st.markdown(
            "<div style='font-size:0.72rem; color:#9CA3AF; margin-top:0.2rem;'>Supports WAV, MP3, M4A, OGG</div>",
            unsafe_allow_html=True,
        )

        if st.button("Transcribe Audio", use_container_width=True):
            if audio_file:
                with st.spinner("Transcribing audio with Whisper..."):
                    text = transcribe_from_audio_file(audio_file, WHISPER_MODEL_SIZE)
                    if text:
                        st.session_state.transcribed_text = text
                        st.success("Transcription complete!")
                    else:
                        st.error("Transcription failed.")
            else:
                st.warning("Please upload an audio file first.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown(
            '<div class="card">'
            '<div class="card-title">Modes &amp; Settings</div>'
            '<div class="micro-label">Configure how the AI assists you</div>',
            unsafe_allow_html=True,
        )

        feature = st.radio(
            "Mode",
            options=["Teaching Mode", "Conversation Mode"],
            index=0,
            key="feature_select",
            horizontal=True,
            label_visibility="collapsed",
        )

        mode_map = {"Teaching Mode": "Concept Explanation", "Conversation Mode": "Quiz Generator"}
        mapped_feature = mode_map[feature]

        st.markdown(
            '<div class="toggle-row">'
            '<div class="toggle-label"><span class="icon">🌐</span> Enable Hinglish</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        diff_row = st.columns([1, 1])
        with diff_row[0]:
            st.markdown(
                '<div class="toggle-row">'
                '<div class="toggle-label"><span class="icon">🎯</span> Adaptive Difficulty</div>'
                "</div>",
                unsafe_allow_html=True,
            )
        with diff_row[1]:
            if mapped_feature == "Quiz Generator":
                difficulty = st.selectbox(
                    "Difficulty",
                    options=["easy", "medium", "hard"],
                    index=0,
                    key="difficulty_select",
                    label_visibility="collapsed",
                )
                num_questions = st.slider(
                    "Questions", min_value=3, max_value=10, value=5, key="num_q_slider",
                )
            else:
                difficulty = "easy"
                num_questions = 5

        st.markdown(
            '<div class="toggle-row">'
            '<div class="toggle-label"><span class="icon">🔒</span> Focus Mode</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="toggle-row">'
            '<div class="toggle-label"><span class="icon">📚</span> Use School Textbook Knowledge</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        use_textbook = st.checkbox(
            "Use School Textbook Knowledge",
            value=False,
            help="Enable if you have uploaded textbook PDFs",
            key="rag_checkbox",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div style="display:flex; gap:0.5rem; margin-top:0.8rem;">',
            unsafe_allow_html=True,
        )
        act_cols = st.columns([1, 1])
        with act_cols[0]:
            st.markdown('<div class="blue-btn">', unsafe_allow_html=True)
            if st.button("Process", use_container_width=True):
                final_topic = topic or st.session_state.transcribed_text
                if not final_topic:
                    st.warning("Please enter a topic or transcribe audio first.")
                else:
                    with st.spinner("Working..."):
                        if mapped_feature == "Concept Explanation":
                            handle_explanation(final_topic, grade_level, use_textbook)
                        else:
                            handle_quiz(final_topic, grade_level, difficulty, num_questions)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with act_cols[1]:
            st.markdown('<div class="crimson-btn">', unsafe_allow_html=True)
            if st.button("Generate", use_container_width=True):
                final_topic = topic or st.session_state.transcribed_text
                if not final_topic:
                    st.warning("Please enter a topic or transcribe audio first.")
                else:
                    inverse_mode = "Quiz Generator" if mapped_feature == "Concept Explanation" else "Concept Explanation"
                    with st.spinner("Working..."):
                        if inverse_mode == "Concept Explanation":
                            handle_explanation(final_topic, grade_level, use_textbook)
                        else:
                            handle_quiz(final_topic, grade_level, difficulty, num_questions)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="card">'
            '<div class="card-title">Learning Resources</div>'
            '<div class="micro-label">Supporting materials for your lesson</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="resource-item"><span class="r-icon">📄</span> Textbook PDF Integration</div>'
            '<div class="resource-item"><span class="r-icon">🎬</span> Visual Learning Suggestions</div>'
            '<div class="resource-item"><span class="r-icon">📝</span> Quiz &amp; Assessment Generator</div>',
            unsafe_allow_html=True,
        )
        if st.button("Prepare Learning Material", use_container_width=True):
            with st.spinner("Building textbook index..."):
                rag = TextbookRAG()
                rag.initialize()
                if rag.build_index():
                    st.success("Textbook index built successfully!")
                else:
                    st.error("No PDFs found. Add PDFs to data/textbooks/ and try again.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="card">'
            '<div class="card-title">Transcription</div>',
            unsafe_allow_html=True,
        )
        st.text_area(
            "Transcribed text",
            value=st.session_state.transcribed_text,
            height=90,
            key="transcribed_display",
            label_visibility="collapsed",
        )
        if st.session_state.transcribed_text:
            if st.button("Use as Topic", use_container_width=True):
                st.session_state.topic_input = st.session_state.transcribed_text
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-label'>Results</div>", unsafe_allow_html=True)

    if st.session_state.get("last_feature") == "Concept Explanation" and st.session_state.ai_response:
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown(f"<h2>{st.session_state.get('topic_input', 'Explanation')}</h2>", unsafe_allow_html=True)
        st.markdown(st.session_state.ai_response)

        if st.button("Read Aloud", key="read_aloud_main"):
            audio_path = text_to_speech(
                st.session_state.ai_response,
                lang=TTS_LANG,
            )
            if audio_path:
                audio_bytes = get_audio_bytes(audio_path)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                cleanup_audio(audio_path)

        if st.session_state.rag_context:
            with st.expander("Textbook Context Used"):
                st.text(st.session_state.rag_context[:2000])
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("last_feature") == "Quiz Generator" and st.session_state.quiz_data:
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown("<h2>Quiz</h2>", unsafe_allow_html=True)
        display_quiz(st.session_state.quiz_data)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="footer">'
        "<span>AI Classroom Copilot v1.0 &mdash; Source file ready</span>"
        '<span><button class="deploy">Deploy</button></span>'
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
