# 🤖 Multi-Agent AI Assistant

An AI-powered resume and career assistant built with Python, Streamlit, and Groq LLMs. It helps users analyze resumes, evaluate ATS compatibility, match resumes with job descriptions, and generate job-specific resumes through specialized AI agents.

## 🚀 Features

* **Resume Analyzer** — Extracts and summarizes relevant resume information, including skills and experience.
* **ATS Scorer** — Evaluates resume compatibility with Applicant Tracking System (ATS) criteria.
* **Job Matcher** — Compares a resume with a job description to identify relevant skills and potential skill gaps.
* **Tailor Resume** — Generates a job-specific resume based on the provided resume and target job description.
* **Resume Q&A** — Allows users to ask questions about their resume.
* **Resume Context** — Supports resume-related context for more relevant responses.
* **Analytics Dashboard** — Displays application and agent activity information.
* **Interactive UI** — Provides a Streamlit interface to access the available features.

## 🛠️ Tech Stack

* **Programming Language:** Python
* **Frontend & Dashboard:** Streamlit
* **LLM Provider:** Groq
* **LLM Integration:** LangChain
* **Data & Document Processing:** Python-based processing utilities
* **Version Control:** Git and GitHub
* **Deployment:** Streamlit Community Cloud

## 🏗️ Project Structure

```text
Multi-Agent-AI-Assistant/
├── .streamlit/
│   └── config.toml
├── core/
│   ├── actions.py
│   ├── parsing.py
│   ├── registry.py
│   ├── runner.py
│   └── session.py
├── ui/
│   ├── __init__.py
│   ├── components.py
│   └── theme.py
├── views/
│   ├── agents.py
│   ├── analytics.py
│   ├── overview.py
│   ├── resume_context.py
│   ├── settings.py
│   └── workspace.py
├── career_advisor.py
├── job_resume_generator.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

``` bash
git clone https://github.com/adarsh-552/Multi-Agent-AI-Assistant.git
```

### 2. Navigate to the project directory

```bash
cd Multi-Agent-AI-Assistant
```

### 3. Create a virtual environment (recommended)

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure your Groq API key

Create a `.streamlit/secrets.toml` file locally and add:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Replace the placeholder with your own Groq API key. Never commit API keys or secrets to GitHub.

For Streamlit Community Cloud, configure `GROQ_API_KEY` in the application's **Settings → Secrets** section.

### 6. Run the application

```bash
python -m streamlit run streamlit_app.py
```

Open the local URL displayed in the terminal to access the application.

## 🧪 Testing the Agents

1. Open the application and navigate to the relevant workspace or agent page.
2. Provide the resume content or upload a supported resume document.
3. For job matching and resume tailoring, provide the target job description.
4. Run the selected agent and review its output.
5. Verify extracted skills, experience, ATS feedback, and generated resume details against the original resume.

## 🔐 Security Considerations

* Store API keys in Streamlit secrets or environment variables.
* Do not commit `.env`, `secrets.toml`, private resumes, or other sensitive files.
* Avoid including personal information in public screenshots or sample documents.

## ⚠️ Limitations

* AI-generated outputs can contain inaccurate or unsupported information.
* ATS scores are estimates and do not guarantee selection or interview calls.
* Always verify generated resume details before using them in job applications.
* Results depend on input quality, model availability, and API configuration.

## 🎯 Project Objective

The objective of this project is to explore how specialized AI agents can assist with resume analysis, job-description matching, ATS-oriented feedback, and job-specific resume generation through a single interactive application.

## 👨‍💻 Author

**Adarsh Nallannagiri**

* GitHub: [adarsh-552](https://github.com/adarsh-552)
## 🌐 Live Demo

Try the deployed application here:

[Launch Multi-Agent AI Assistant](https://multi-agent-ai-assistant-brb5mp59shft8tsembunyw.streamlit.app/agents)

---

*Built with Python, Streamlit, and Groq-powered LLMs.*
