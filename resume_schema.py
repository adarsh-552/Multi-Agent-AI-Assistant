from pydantic import BaseModel, Field
from typing import List


class ResumeAnalysis(BaseModel):

    name: str = Field(description="Candidate's name")

    professional_domain: str = Field(
        description="Main professional domain identified from the resume"
    )

    current_or_target_role: str = Field(
        description="Current or target role based only on resume evidence"
    )

    experience_level: str = Field(
        description="Experience level such as Fresher, Intern, Junior, Mid-level, etc."
    )

    technical_skills: List[str] = Field(
    default_factory=list,
    description=(
        "Technical skills explicitly mentioned in the resume, "
        "including programming languages, frameworks, databases, APIs, "
        "technical concepts, and technologies."
    )
    )

    professional_skills: List[str] = Field(
    default_factory=list,
    description=(
        "Soft/professional skills explicitly mentioned in the resume, "
        "such as communication, teamwork, leadership, problem-solving. "
        "Do not include programming languages, frameworks, tools, databases, "
        "or technical skills."
    )
    )
    tools: List[str] = Field(
    default_factory=list,
    description=(
        "Software tools explicitly mentioned in the resume, "
        "such as Git, GitHub, VS Code, Jupyter Notebook."
    )
    )

    

    strengths: List[str] = Field(default_factory=list)

    weaknesses: List[str] = Field(default_factory=list)

    recommended_roles: List[str] = Field(default_factory=list)

    skill_gaps: List[str] = Field(default_factory=list)

    resume_improvements: List[str] = Field(default_factory=list)