"""Resume Context: what the AI actually reads and how it retrieves from it."""

import streamlit as st

from core.registry import RAG
from core.session import reset_resume, resume_status
from ui import components as ui
from ui.theme import page_title

ss = st.session_state

page_title(
    "Resume Context",
    "The text and chunks built from your resume. Every specialist works from this, nothing else.",
)

status = resume_status()

if not status["loaded"]:
    ui.empty_state(
        "No resume loaded",
        "Upload a PDF in the Resume Workspace and its extracted text and search index will show up here.",
        "CV",
    )
    st.page_link("views/workspace.py", label="Open Resume Workspace", icon=":material/description:")
    st.stop()

index = ss.index
dimension = getattr(index, "d", None)
vectors = getattr(index, "ntotal", None)

c1, c2, c3, c4 = st.columns(4)
with c1:
    ui.kpi("File", status["file_name"] or "Unknown", ui.human_size(status["file_size"]) or None)
with c2:
    ui.kpi("Chunks", status["chunk_count"])
with c3:
    ui.kpi("Extracted text", f'{status["characters"]:,}', "characters, chunks joined")
with c4:
    ui.kpi("Indexed vectors", vectors if vectors is not None else "Unknown", f"{dimension} dimensions" if dimension else None)

st.write("")
left, right = st.columns(2)
with left:
    with st.container(border=True):
        ui.section("Embedding and index")
        ui.html(
            '<div class="acc-row"><span>Embedding model</span>'
            f'<span class="acc-row-main">{ui.esc(RAG["embedding_model"])}</span></div>'
            '<div class="acc-row"><span>Index</span>'
            f'<span class="acc-row-main">{ui.esc(RAG["index_type"])}</span></div>'
        )
with right:
    with st.container(border=True):
        ui.section("Retrieval settings")
        ui.html(
            '<div class="acc-row"><span>Chunk size</span>'
            f'<span class="acc-row-main">{RAG["chunk_size"]} characters</span></div>'
            '<div class="acc-row"><span>Chunk overlap</span>'
            f'<span class="acc-row-main">{RAG["chunk_overlap"]} characters</span></div>'
            '<div class="acc-row"><span>Chunks retrieved per question</span>'
            f'<span class="acc-row-main">{RAG["top_k"]}</span></div>'
        )
        ui.note("These values are defined in rag/rag_pipeline.py.")

st.write("")
with st.container(border=True):
    ui.section("Search the chunks", "Plain text search over the chunks stored for this resume.")
    query = st.text_input(
        "Search chunks", key="chunk_search", placeholder="Type a word or phrase", label_visibility="collapsed"
    )
    chunks = ss.chunks or []
    numbered = list(enumerate(chunks, 1))
    if query.strip():
        needle = query.strip().lower()
        numbered = [(i, c) for i, c in numbered if needle in c.lower()]
        ui.note(f"{len(numbered)} of {len(chunks)} chunks match.")
    if not numbered:
        ui.empty_state("No matching chunks", "Try a different word or phrase.", "?")
    else:
        for i, chunk in numbered[:40]:
            with st.expander(f"Chunk {i}  \u00b7  {len(chunk)} characters"):
                st.text(chunk)
        if len(numbered) > 40:
            ui.note(f"Showing the first 40 of {len(numbered)} chunks. Narrow the search to see others.")

with st.expander("Full extracted text"):
    st.text(ss.resume_text)

st.write("")
st.button("Clear resume and results", on_click=reset_resume, icon=":material/delete:")
ui.note("This removes the resume, its index and every result. Run history stays in Analytics.")
