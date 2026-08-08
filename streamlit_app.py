import streamlit as st
import os

from rag.rag_pipeline import (
    create_vector_store,
    ask_pdf
)

from resume_analyzer import analyze_resume
from job_matcher import match_resume_with_job
from ats_scorer import calculate_resume_score
from resume_improver import improve_resume
from docx_generator import create_resume_docx
from job_resume_generator import generate_job_specific_resume
from career_advisor import analyze_job_suitability


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Resume & Career Assistant",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("🤖 AI Resume & Career Assistant")

st.write(
    "Upload your resume to analyze your skills, "
    "find suitable jobs, evaluate ATS readiness, "
    "generate tailored resumes and get career advice."
)


# =========================================================
# SESSION STATE
# =========================================================

if "resume_processed" not in st.session_state:
    st.session_state.resume_processed = False

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "index" not in st.session_state:
    st.session_state.index = None

if "chunks" not in st.session_state:
    st.session_state.chunks = None

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "improved_resume" not in st.session_state:
    st.session_state.improved_resume = None

if "tailored_resume" not in st.session_state:
    st.session_state.tailored_resume = None


# =========================================================
# PDF UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📄 Upload your Resume PDF",
    type=["pdf"],
    key="resume_pdf_upload"
)


# =========================================================
# PROCESS PDF
# =========================================================

if uploaded_file is not None:

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    file_path = os.path.join(
        "uploads",
        uploaded_file.name
    )

    # Process only when a new file is uploaded
    if (
        "processed_file_name" not in st.session_state
        or st.session_state.processed_file_name
        != uploaded_file.name
    ):

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )

        st.success(
            "✅ Resume uploaded successfully!"
        )

        # -------------------------------------------------
        # CREATE VECTOR STORE
        # -------------------------------------------------

        with st.spinner(
            "📖 Reading and processing resume..."
        ):

            index, chunks = create_vector_store(
                file_path
            )

        # -------------------------------------------------
        # SAVE IN SESSION
        # -------------------------------------------------

        st.session_state.index = index
        st.session_state.chunks = chunks

        st.session_state.resume_text = (
            "\n\n".join(chunks)
        )

        st.session_state.resume_processed = True

        st.session_state.processed_file_name = (
            uploaded_file.name
        )

        # Reset old generated outputs
        st.session_state.improved_resume = None
        st.session_state.tailored_resume = None

        st.success(
            "✅ Resume processed successfully!"
        )


# =========================================================
# MAIN APPLICATION
# =========================================================

if st.session_state.resume_processed:

    resume_text = st.session_state.resume_text

    index = st.session_state.index

    chunks = st.session_state.chunks


    # =====================================================
    # RESUME ANALYSIS
    # =====================================================

    if st.session_state.analysis is None:

        with st.spinner(
            "🤖 Analyzing your resume..."
        ):

            st.session_state.analysis = (
                analyze_resume(
                    resume_text
                )
            )

    analysis = st.session_state.analysis

    st.success(
        "✅ Resume analysis completed!"
    )


    # =====================================================
    # RESUME ANALYSIS
    # =====================================================

    st.markdown("---")

    st.header(
        "📊 Resume Analysis"
    )


    # =====================================================
    # CANDIDATE PROFILE
    # =====================================================

    st.subheader(
        "👤 Candidate Profile"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "**Name:**",
            analysis.name
        )

        st.write(
            "**Domain:**",
            analysis.professional_domain
        )

    with col2:

        st.write(
            "**Target Role:**",
            analysis.current_or_target_role
        )

        st.write(
            "**Experience:**",
            analysis.experience_level
        )


    # =====================================================
    # TECHNICAL SKILLS
    # =====================================================

    st.subheader(
        "💻 Existing Technical Skills"
    )

    if analysis.technical_skills:

        st.write(
            " • ".join(
                analysis.technical_skills
            )
        )

    else:

        st.info(
            "No technical skills identified."
        )


    # =====================================================
    # PROFESSIONAL SKILLS
    # =====================================================

    st.subheader(
        "🤝 Professional Skills"
    )

    if analysis.professional_skills:

        st.write(
            " • ".join(
                analysis.professional_skills
            )
        )

    else:

        st.info(
            "No professional skills identified."
        )


    # =====================================================
    # TOOLS
    # =====================================================

    st.subheader(
        "🛠️ Tools"
    )

    if analysis.tools:

        st.write(
            " • ".join(
                analysis.tools
            )
        )

    else:

        st.info(
            "No tools identified."
        )


    # =====================================================
    # STRENGTHS AND WEAKNESSES
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "💪 Resume Strengths"
        )

        if analysis.strengths:

            for strength in analysis.strengths:

                st.write(
                    "✅",
                    strength
                )

        else:

            st.info(
                "No strengths identified."
            )


    with col2:

        st.subheader(
            "⚠️ Resume Weaknesses"
        )

        if analysis.weaknesses:

            for weakness in analysis.weaknesses:

                st.write(
                    "•",
                    weakness
                )

        else:

            st.info(
                "No weaknesses identified."
            )


    # =====================================================
    # RECOMMENDED JOB ROLES
    # =====================================================

    st.subheader(
        "🎯 Recommended Job Roles"
    )

    if analysis.recommended_roles:

        for role in analysis.recommended_roles:

            st.write(
                "💼",
                role
            )

    else:

        st.info(
            "No recommended roles identified."
        )


    # =====================================================
    # SKILL GAPS
    # =====================================================

    st.subheader(
        "📚 Recommended / Missing Skills"
    )

    if analysis.skill_gaps:

        for skill in analysis.skill_gaps:

            st.write(
                "📌",
                skill
            )

    else:

        st.info(
            "No skill gaps identified."
        )


    # =====================================================
    # RESUME IMPROVEMENTS
    # =====================================================

    st.subheader(
        "📝 Resume Improvements"
    )

    if analysis.resume_improvements:

        for improvement in (
            analysis.resume_improvements
        ):

            st.write(
                "➡️",
                improvement
            )

    else:

        st.info(
            "No improvements identified."
        )


    # =====================================================
    # ATS SCORE
    # =====================================================

    st.markdown("---")

    st.header(
        "📈 Resume Quality / ATS Score"
    )

    st.write(
        "Evaluate the resume based on structure, "
        "skills, projects, experience and ATS readiness."
    )

    if st.button(
        "📊 Calculate Resume Score",
        key="calculate_resume_score"
    ):

        with st.spinner(
            "🤖 Calculating resume score..."
        ):

            ats_result = (
                calculate_resume_score(
                    resume_text
                )
            )

        st.success(
            "✅ Resume score generated!"
        )

        st.subheader(
            "📊 Resume Score Report"
        )

        st.markdown(
            ats_result
        )


    # =====================================================
    # JOB MATCHER
    # =====================================================

    st.markdown("---")

    st.header(
        "🔍 Resume vs Job Description"
    )

    st.write(
        "Paste a job description to check how well "
        "your resume matches the role."
    )

    job_description = st.text_area(
        "📋 Job Description",
        height=300,
        placeholder=(
            "Paste the complete job description here..."
        ),
        key="matcher_job_description"
    )

    if st.button(
        "🔍 Analyze Job Match",
        key="analyze_resume_job_match"
    ):

        if not job_description.strip():

            st.warning(
                "⚠️ Please paste a job description."
            )

        else:

            with st.spinner(
                "🤖 Comparing resume and job..."
            ):

                match_result = (
                    match_resume_with_job(
                        resume_text,
                        job_description
                    )
                )

            st.success(
                "✅ Job match analysis completed!"
            )

            st.subheader(
                "📊 Job Match Analysis"
            )

            st.markdown(
                match_result
            )


    # =====================================================
    # GENERAL RESUME IMPROVER
    # =====================================================

    st.markdown("---")

    st.header(
        "✨ Improve My Resume"
    )

    st.write(
        "Generate a more professional and ATS-friendly "
        "version of your resume."
    )

    improve_job_description = st.text_area(
        "📋 Optional Job Description",
        height=250,
        placeholder=(
            "Paste a job description if you want "
            "the resume optimized for a particular role."
        ),
        key="improve_resume_job_description"
    )

    if st.button(
        "✨ Generate Improved Resume",
        key="generate_general_resume"
    ):

        with st.spinner(
            "🤖 Improving your resume..."
        ):

            improved_resume = improve_resume(
                resume_text,
                improve_job_description
            )

        st.session_state.improved_resume = (
            improved_resume
        )

        st.success(
            "✅ Improved resume generated!"
        )


    # =====================================================
    # SHOW IMPROVED RESUME
    # =====================================================

    if st.session_state.improved_resume:

        improved_resume = (
            st.session_state.improved_resume
        )

        st.subheader(
            "📄 Improved Resume"
        )

        st.markdown(
            improved_resume
        )

        # -------------------------------------------------
        # TXT
        # -------------------------------------------------

        st.download_button(
            label=(
                "⬇️ Download Improved Resume (.txt)"
            ),
            data=improved_resume,
            file_name="improved_resume.txt",
            mime="text/plain",
            key="download_general_resume_txt"
        )

        # -------------------------------------------------
        # DOCX
        # -------------------------------------------------

        improved_docx_path = os.path.join(
            "uploads",
            "improved_resume.docx"
        )

        try:

            create_resume_docx(
                improved_resume,
                improved_docx_path
            )

            with open(
                improved_docx_path,
                "rb"
            ) as file:

                improved_docx_data = (
                    file.read()
                )

            st.download_button(
                label=(
                    "📄 Download Improved Resume (.docx)"
                ),
                data=improved_docx_data,
                file_name="improved_resume.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                key="download_general_resume_docx"
            )

        except Exception as e:

            st.error(
                f"❌ DOCX generation failed: {e}"
            )


    # =====================================================
    # JOB-SPECIFIC RESUME
    # =====================================================

    st.markdown("---")

    st.header(
        "🎯 Create Job-Specific Resume"
    )

    st.write(
        "Generate a tailored resume for any job role "
        "using only your actual skills and experience."
    )

    st.info(
        "💡 Missing technologies from the job description "
        "will NOT be falsely added to your resume."
    )

    tailored_job_description = st.text_area(
        "📋 Job Description for Tailored Resume",
        height=300,
        placeholder=(
            "Paste the complete job description here..."
        ),
        key="tailored_job_description"
    )

    if st.button(
        "🎯 Generate Job-Specific Resume",
        key="generate_tailored_resume"
    ):

        if not tailored_job_description.strip():

            st.warning(
                "⚠️ Please paste a job description first."
            )

        else:

            with st.spinner(
                "🤖 Creating job-specific resume..."
            ):

                tailored_resume = (
                    generate_job_specific_resume(
                        resume_text,
                        tailored_job_description
                    )
                )

            st.session_state.tailored_resume = (
                tailored_resume
            )

            st.success(
                "✅ Job-specific resume generated!"
            )


    # =====================================================
    # SHOW TAILORED RESUME
    # =====================================================

    if st.session_state.tailored_resume:

        tailored_resume = (
            st.session_state.tailored_resume
        )

        st.subheader(
            "📄 Tailored Resume"
        )

        st.markdown(
            tailored_resume
        )

        # -------------------------------------------------
        # TXT DOWNLOAD
        # -------------------------------------------------

        st.download_button(
            label=(
                "⬇️ Download Tailored Resume (.txt)"
            ),
            data=tailored_resume,
            file_name="job_specific_resume.txt",
            mime="text/plain",
            key="download_tailored_resume_txt"
        )

        # -------------------------------------------------
        # DOCX DOWNLOAD
        # -------------------------------------------------

        tailored_docx_path = os.path.join(
            "uploads",
            "job_specific_resume.docx"
        )

        try:

            create_resume_docx(
                tailored_resume,
                tailored_docx_path
            )

            with open(
                tailored_docx_path,
                "rb"
            ) as file:

                tailored_docx_data = (
                    file.read()
                )

            st.download_button(
                label=(
                    "📄 Download Tailored Resume (.docx)"
                ),
                data=tailored_docx_data,
                file_name="job_specific_resume.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                key="download_tailored_resume_docx"
            )

        except Exception as e:

            st.error(
                f"❌ Tailored DOCX generation failed: {e}"
            )


    # =====================================================
    # CAREER ADVISOR
    # =====================================================

    st.markdown("---")

    st.header(
        "🧭 Should I Apply for This Job?"
    )

    st.write(
        "Paste a job description and the AI will compare "
        "it with your actual resume and explain whether "
        "you should apply."
    )

    st.info(
        "💡 The recommendation is based on resume/job "
        "matching. It does not guarantee job selection."
    )

    career_job_description = st.text_area(
        "📋 Job Description for Career Advice",
        height=300,
        placeholder=(
            "Paste the complete job description here..."
        ),
        key="career_advisor_job_description"
    )

    if st.button(
        "🧭 Analyze Job Suitability",
        key="analyze_career_suitability"
    ):

        if not career_job_description.strip():

            st.warning(
                "⚠️ Please paste a job description first."
            )

        else:

            with st.spinner(
                "🤖 Analyzing your suitability..."
            ):

                suitability_result = (
                    analyze_job_suitability(
                        resume_text,
                        career_job_description
                    )
                )

            st.success(
                "✅ Career analysis completed!"
            )

            st.subheader(
                "🧭 Career Recommendation"
            )

            st.markdown(
                suitability_result
            )


    # =====================================================
    # RAG QUESTION ANSWERING
    # =====================================================

    st.markdown("---")

    st.header(
        "💬 Ask Questions About Your Resume"
    )

    st.write(
        "Ask questions based on the information "
        "contained in your uploaded PDF."
    )

    question = st.text_input(
        "Ask your question:",
        placeholder=(
            "Example: What are my technical skills?"
        ),
        key="resume_question"
    )

    if question:

        with st.spinner(
            "🤖 Finding the answer..."
        ):

            answer = ask_pdf(
                question,
                index,
                chunks
            )

        st.subheader(
            "🤖 AI Response"
        )

        st.write(
            answer
        )


# =========================================================
# NO RESUME UPLOADED
# =========================================================

else:

    st.info(
        "👆 Upload your resume PDF to get started."
    )

    st.markdown(
        """
        ### 🚀 Features

        - 📄 Resume PDF Upload
        - 📊 Resume Analysis
        - 💻 Technical Skill Extraction
        - 🤝 Professional Skill Detection
        - 🛠️ Tool Detection
        - 💪 Resume Strength Analysis
        - ⚠️ Resume Weakness Analysis
        - 🎯 Recommended Job Roles
        - 📚 Skill Gap Detection
        - 📈 Resume Quality / ATS Score
        - 🔍 Resume vs Job Description Matching
        - ✨ AI Resume Improvement
        - 🎯 Job-Specific Resume Generation
        - 🧭 Career Apply Recommendation
        - ⬇️ TXT Resume Download
        - 📄 DOCX Resume Download
        - 💬 RAG-based Resume Q&A
        """
    )