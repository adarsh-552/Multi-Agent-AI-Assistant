from langchain_groq import ChatGroq
from config import GROQ_API_KEY
from resume_schema import ResumeAnalysis


llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b"
)
structured_llm = llm.with_structured_output(ResumeAnalysis)


def analyze_resume(resume_text):

    prompt = f"""
You are a Universal Resume Analyzer.

Analyze the resume accurately.

IMPORTANT RULES:
1. Use ONLY information explicitly present in the resume.
2. Never invent skills, experience, education, projects,
   certifications or achievements.
3. Identify the professional domain automatically.
4. The domain can be IT or non-IT.
5. Recommended roles must match the candidate's actual background.
6. Clearly separate existing skills from skill gaps.
7. Skill gaps are recommendations, NOT existing skills.
8. If information is missing, do not invent it.
9. Do not claim to know why a company rejected the candidate.

Resume:

{resume_text}
"""

    response = structured_llm.invoke(prompt)

    return response