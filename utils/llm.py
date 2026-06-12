import os
import json
import re
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

from utils.prompts import EXPLANATION_PROMPT, QUIZ_PROMPT, SUMMARIZE_PROMPT

load_dotenv()


@st.cache_resource
def configure_gemini():
    """Configure Gemini API with key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found in environment variables. Check .env file.")
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Gemini configuration failed: {str(e)}")
        return False


def get_gemini_model(model_name="models/gemini-2.5-flash"):
    """Get a Gemini model instance."""
    try:
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        st.error(f"Failed to load Gemini model: {str(e)}")
        return None


def generate_explanation(topic, grade_level=5, context=""):
    """Generate a classroom-friendly explanation using Gemini.

    Args:
        topic: The concept to explain (e.g. "photosynthesis")
        grade_level: Class/grade level (1-12)
        context: Optional textbook context from RAG

    Returns:
        Dictionary with explanation sections or None on error
    """
    if not configure_gemini():
        return None

    model = get_gemini_model()
    if model is None:
        return None

    prompt = EXPLANATION_PROMPT.format(
        topic=topic, grade_level=grade_level
    )

    if context:
        prompt = f"""Here is relevant context from the textbook:
{context}

{prompt}"""

    try:
        response = model.generate_content(prompt)
        return {
            "success": True,
            "text": response.text,
            "topic": topic,
            "grade_level": grade_level,
        }
    except Exception as e:
        st.error(f"Explanation generation failed: {str(e)}")
        return {"success": False, "error": str(e)}


def generate_quiz(topic, grade_level=5, difficulty="easy", num_questions=5):
    """Generate a multiple choice quiz using Gemini.

    Args:
        topic: Quiz topic (e.g. "human body")
        grade_level: Class/grade level
        difficulty: easy, medium, or hard
        num_questions: Number of questions to generate

    Returns:
        List of question dicts or None on error
    """
    if not configure_gemini():
        return None

    model = get_gemini_model()
    if model is None:
        return None

    prompt = QUIZ_PROMPT.format(
        topic=topic,
        difficulty=difficulty,
        grade_level=grade_level,
        num_questions=num_questions,
    )

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            quiz_data = json.loads(json_str)
            return quiz_data.get("questions", [])
        else:
            st.error("Could not parse quiz JSON from response")
            return None
    except json.JSONDecodeError as e:
        st.error(f"Quiz JSON parsing failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Quiz generation failed: {str(e)}")
        return None


def summarize_textbook_content(context, topic, grade_level=5):
    """Summarize textbook content for a student.

    Args:
        context: Extracted text from textbook PDF
        topic: The topic being studied
        grade_level: Class level

    Returns:
        Summary text or None on error
    """
    if not configure_gemini():
        return None

    model = get_gemini_model()
    if model is None:
        return None

    prompt = SUMMARIZE_PROMPT.format(
        context=context[:4000], topic=topic, grade_level=grade_level
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Summarization failed: {str(e)}")
        return None
