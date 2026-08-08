from agents.pdf_agent import read_pdf
from resume_analyzer import analyze_resume


pdf_path = "uploads/sample.pdf"

resume_text = read_pdf(pdf_path)

analysis = analyze_resume(resume_text)

print("\n===== RESUME ANALYSIS =====\n")

print(analysis)