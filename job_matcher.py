from langchain_groq import ChatGroq
from config import GROQ_API_KEY


llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b"
)


def match_resume_with_job(resume_text, job_description):

    prompt = f"""
You are an expert Resume and Job Description Matching Assistant.

Compare the candidate's resume with the provided job description.

IMPORTANT RULES:

1. Use only information explicitly present in the resume.
2. Never claim that the candidate has a skill that is not present.
3. Clearly separate existing skills from missing/recommended skills.
4. Do not invent experience.
5. Do not claim that a company will select or reject the candidate.
6. Match the candidate based on evidence from the resume.
7. The job description can belong to ANY industry:
   IT, finance, sales, marketing, healthcare, education,
   engineering, operations, or any other field.

Analyze:

- Overall job match percentage
- Matching skills
- Missing skills
- Matching experience
- Experience gaps
- Role suitability
- Resume improvements for this specific job

Use this structure:

JOB MATCH SCORE:
Give a percentage from 0 to 100.

MATCHING SKILLS:
List skills present in BOTH the resume and job description.

MISSING / RECOMMENDED SKILLS:
List important job requirements that are not demonstrated in the resume.

MATCHING EXPERIENCE:
Explain which resume experience matches the job.

EXPERIENCE GAPS:
Explain important experience requirements not demonstrated in the resume.

ROLE SUITABILITY:
Explain why the candidate is or is not a reasonable match.

RESUME IMPROVEMENTS:
Give specific changes to make the resume more relevant to this job.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    response = llm.invoke(prompt)

    return response.content