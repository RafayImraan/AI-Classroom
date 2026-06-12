EXPLANATION_PROMPT = """You are an AI teacher assistant for Indian government schools. Students understand Hinglish. Explain concepts in simple language with examples. Avoid difficult words.

Topic: {topic}
Target Audience: Class {grade_level} students
Language: Hinglish (mix of Hindi and English)

Please provide the following sections:
1. **Simple Explanation** - Explain in basic English that a young student can understand
2. **Hinglish Explanation** - Same explanation but in Hinglish (Hindi + English mix)
3. **Real-Life Examples** - 2-3 examples from everyday life that students can relate to
4. **Important Points** - 3-5 key takeaways in bullet points
5. **Visual Learning Suggestions** - What diagrams, images or activities would help teach this concept

Keep each section concise. Total response should not exceed 500 words. Use simple words only.
"""

QUIZ_PROMPT = """You are an AI teacher assistant for Indian government schools. Students understand Hinglish.

Topic: {topic}
Difficulty Level: {difficulty}
Grade: Class {grade_level}
Number of Questions: {num_questions}

Generate a multiple choice quiz with the following JSON structure for each question:
{{
  "questions": [
    {{
      "question": "Question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Correct option text",
      "explanation": "Brief explanation in Hinglish why this is correct"
    }}
  ]
}}

Rules:
- Use simple language suitable for class {grade_level} students
- Questions should test understanding, not memorization
- Include real-life applications where possible
- Provide explanations in Hinglish mix
- Return ONLY valid JSON, no other text
"""

SUMMARIZE_PROMPT = """Summarize the following textbook content in simple terms for a Class {grade_level} student.

Textbook Content:
{context}

Topic: {topic}

Provide:
1. **Easy Summary** - 3-4 lines in simple English
2. **Key Points** - Bullet points of main ideas
3. **Hinglish Summary** - Same content in Hinglish
"""
