"""Visual system: light SaaS look, one indigo accent, white cards on a soft grey page."""

import streamlit as st

from core.runner import agent_stats
from core.session import APP_VERSION, get_prefs, groq_key_configured, resume_status

APP_NAME = "AI Command Center"
APP_SUBTITLE = "AI Resume & Career Assistant"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp button, .stApp input, .stApp textarea, .acc-root {
    font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1180px; }
h1 { font-size: 1.7rem !important; font-weight: 700 !important; letter-spacing: -0.015em; }
h2 { font-size: 1.3rem !important; font-weight: 650 !important; }
h3 { font-size: 1.08rem !important; font-weight: 620 !important; }

/* ---------- header ---------- */
.acc-header {
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
    padding-bottom: 0.9rem; margin-bottom: 1.4rem; border-bottom: 1px solid #E4E7EF;
}
.acc-title { font-size: 1.05rem; font-weight: 700; line-height: 1.2; }
.acc-subtitle { font-size: 0.85rem; color: #5B6275; line-height: 1.3; }
.acc-page-title { font-size: 1.7rem; font-weight: 700; letter-spacing: -0.015em; margin: 0 0 0.2rem 0; }
.acc-page-caption { font-size: 0.97rem; color: #5B6275; margin: 0 0 1.4rem 0; max-width: 68ch; }
.acc-section { font-size: 1.02rem; font-weight: 650; margin: 0 0 0.15rem 0; }
.acc-section-sub { font-size: 0.87rem; color: #5B6275; margin: 0 0 0.8rem 0; }
.acc-note { font-size: 0.85rem; color: #5B6275; margin: 0.2rem 0 0.8rem 0; }

/* ---------- hero ---------- */
.acc-hero {
    background: linear-gradient(135deg, #EEE9FF 0%, #F8F9FF 100%);
    border: 1px solid #DDD3FF; border-radius: 18px; padding: 1.7rem 1.9rem; margin-bottom: 1.1rem;
}
.acc-hero-title { font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.2; margin: 0 0 0.5rem 0; }
.acc-hero-text { font-size: 1rem; color: #4A5163; max-width: 62ch; margin: 0; line-height: 1.55; }

/* ---------- pills and chips ---------- */
.acc-pill {
    display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.2rem 0.7rem; border-radius: 999px;
    font-size: 0.82rem; font-weight: 600; border: 1px solid #D5D9E4; white-space: nowrap; color: #3A4153; background: #F1F3F7;
}
.acc-pill-ok { background: #E8F6EE; border-color: #BFE3CD; color: #17613A; }
.acc-pill-warn { background: #FFF4E0; border-color: #F3D7A1; color: #7A4F00; }
.acc-pill-err { background: #FDECEC; border-color: #F3C9C9; color: #8F1F1F; }
.acc-pill-idle { background: #F1F3F7; border-color: #D5D9E4; color: #3A4153; }
.acc-chips { display: flex; flex-wrap: wrap; gap: 0.1rem; }
.acc-chip {
    display: inline-block; padding: 0.22rem 0.65rem; border-radius: 999px; font-size: 0.83rem; font-weight: 550;
    border: 1px solid #DDD3FF; background: #F3EFFF; color: #4B2FD0; margin: 0 0.35rem 0.35rem 0;
}
.acc-chip-ok { background: #E8F6EE; border-color: #BFE3CD; color: #17613A; }
.acc-chip-warn { background: #FFF4E0; border-color: #F3D7A1; color: #7A4F00; }
.acc-chip-neutral { background: #F1F3F7; border-color: #E1E5EC; color: #3A4153; }

/* ---------- cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF; border: 1px solid #E4E7EF !important; border-radius: 14px;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}
.acc-kpi {
    background: #FFFFFF; border: 1px solid #E4E7EF; border-radius: 14px; padding: 1rem 1.1rem;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04); height: 100%; box-sizing: border-box;
}
.acc-kpi-label { font-size: 0.82rem; color: #5B6275; font-weight: 550; margin-bottom: 0.35rem; }
.acc-kpi-value { font-size: 1.65rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; }
.acc-kpi-hint { font-size: 0.82rem; color: #5B6275; margin-top: 0.35rem; overflow-wrap: anywhere; }

/* ---------- workflow ---------- */
.acc-flow { display: flex; flex-wrap: wrap; align-items: center; gap: 0.45rem; }
.acc-step {
    display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.42rem 0.8rem; border-radius: 10px;
    border: 1px solid #E4E7EF; background: #FFFFFF; font-size: 0.88rem; font-weight: 560; color: #3A4153;
}
.acc-step-done { background: #F1FAF5; border-color: #BFE3CD; color: #17613A; }
.acc-step-next { background: #F3EFFF; border-color: #6C47FF; color: #4B2FD0; }
.acc-arrow { color: #9AA1B2; font-size: 0.95rem; }
.acc-stage { flex: 1 1 180px; border: 1px solid #E4E7EF; border-radius: 12px; padding: 0.8rem 0.95rem; background: #FAFBFE; }
.acc-stage b { display: block; font-size: 0.92rem; margin-bottom: 0.2rem; }
.acc-stage span { font-size: 0.84rem; color: #5B6275; }

/* ---------- score ring and bars ---------- */
.acc-ring-wrap { display: flex; justify-content: center; padding: 0.4rem 0; }
.acc-ring { width: 148px; height: 148px; border-radius: 50%; display: grid; place-items: center; }
.acc-ring-inner {
    width: 112px; height: 112px; border-radius: 50%; background: #FFFFFF; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
}
.acc-ring-val { font-size: 2.1rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1; }
.acc-ring-max { font-size: 0.82rem; color: #5B6275; margin-top: 0.2rem; }
.acc-ring-caption { text-align: center; font-size: 0.85rem; color: #5B6275; margin-top: 0.1rem; }
.acc-bar-row { margin: 0.6rem 0; }
.acc-bar-top { display: flex; justify-content: space-between; gap: 0.6rem; font-size: 0.88rem; margin-bottom: 0.25rem; }
.acc-bar { height: 8px; border-radius: 99px; background: #E9ECF3; overflow: hidden; }
.acc-bar > div { height: 100%; background: #6C47FF; border-radius: 99px; }

/* ---------- lists, rows, file chip ---------- */
.acc-list { margin: 0.2rem 0 0.2rem 1.1rem; padding: 0; }
.acc-list li { margin: 0.28rem 0; line-height: 1.5; font-size: 0.93rem; }
.acc-row {
    display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.6rem 0;
    border-bottom: 1px solid #EEF0F5; font-size: 0.9rem;
}
.acc-row:last-child { border-bottom: none; }
.acc-row-main { font-weight: 600; }
.acc-row-meta { color: #5B6275; font-size: 0.84rem; }
.acc-file { display: flex; align-items: center; gap: 0.85rem; }
.acc-file-icon {
    width: 44px; height: 44px; border-radius: 11px; background: #EEE9FF; color: #4B2FD0; display: grid;
    place-items: center; font-weight: 700; font-size: 0.8rem; flex: 0 0 auto;
}
.acc-file-name { font-weight: 650; overflow-wrap: anywhere; }
.acc-file-meta { font-size: 0.85rem; color: #5B6275; }

/* ---------- agent cards ---------- */
.acc-agent-head { display: flex; align-items: center; justify-content: space-between; gap: 0.8rem; margin-bottom: 0.55rem; }
.acc-agent-id { display: flex; align-items: center; gap: 0.7rem; }
.acc-avatar {
    width: 38px; height: 38px; border-radius: 10px; background: #EEE9FF; color: #4B2FD0; display: grid;
    place-items: center; font-weight: 700; font-size: 0.82rem; flex: 0 0 auto;
}
.acc-agent-name { font-weight: 650; font-size: 1rem; line-height: 1.25; }
.acc-agent-role { font-size: 0.9rem; color: #4A5163; line-height: 1.5; margin-bottom: 0.7rem; }
.acc-stats { display: flex; flex-wrap: wrap; gap: 1.2rem; font-size: 0.84rem; color: #5B6275; margin-top: 0.4rem; }
.acc-stats b { color: #1A1D29; }

/* ---------- decision, empty and error states ---------- */
.acc-decision {
    display: inline-flex; align-items: center; gap: 0.6rem; padding: 0.55rem 1.1rem; border-radius: 12px;
    font-size: 1.15rem; font-weight: 700; border: 1px solid #D5D9E4;
}
.acc-decision-ok { background: #E8F6EE; border-color: #BFE3CD; color: #17613A; }
.acc-decision-warn { background: #FFF4E0; border-color: #F3D7A1; color: #7A4F00; }
.acc-decision-err { background: #FDECEC; border-color: #F3C9C9; color: #8F1F1F; }
.acc-empty {
    text-align: center; padding: 2.2rem 1.2rem; border: 1px dashed #CBD1E0; border-radius: 14px; background: #FAFBFE;
}
.acc-empty-icon {
    width: 44px; height: 44px; border-radius: 12px; background: #EEE9FF; color: #4B2FD0; display: inline-grid;
    place-items: center; font-weight: 700; margin-bottom: 0.7rem;
}
.acc-empty-title { font-size: 1.05rem; font-weight: 650; margin-bottom: 0.3rem; }
.acc-empty-text { font-size: 0.92rem; color: #5B6275; max-width: 48ch; margin: 0 auto; line-height: 1.5; }
.acc-err { border: 1px solid #F3C9C9; background: #FFF5F5; border-radius: 14px; padding: 1rem 1.2rem; margin-bottom: 0.6rem; }
.acc-err-title { font-weight: 650; color: #8F1F1F; margin-bottom: 0.25rem; }
.acc-err-text { font-size: 0.92rem; color: #5A2A2A; line-height: 1.5; }
.acc-stale { font-size: 0.85rem; color: #7A4F00; background: #FFF4E0; border: 1px solid #F3D7A1; border-radius: 10px; padding: 0.45rem 0.8rem; margin: 0.5rem 0; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E4E7EF; }
[data-testid="stSidebarNavLink"] { border-radius: 10px; font-weight: 550; }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: #EEE9FF; color: #4B2FD0; }
.acc-side-label { font-size: 0.8rem; color: #5B6275; margin: 1rem 0 0.35rem 0; font-weight: 650; }
.acc-side-row { display: flex; justify-content: space-between; gap: 0.5rem; font-size: 0.85rem; padding: 0.15rem 0; }
.acc-side-row span:first-child { color: #5B6275; }

/* ---------- tabs, controls, chat ---------- */
[data-baseweb="tab-list"] { gap: 0.2rem; border-bottom: 1px solid #E4E7EF; }
button[data-baseweb="tab"] { padding: 0.65rem 0.95rem; font-weight: 600; }
.stButton > button, .stDownloadButton > button, [data-testid="stPageLink"] a {
    border-radius: 10px; font-weight: 600; transition: border-color 0.12s ease, background-color 0.12s ease;
}
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input { border-radius: 10px; }
[data-testid="stFileUploaderDropzone"] { border: 1.5px dashed #B8A6FF; border-radius: 14px; background: #FBFAFF; padding: 1.6rem; }
[data-testid="stChatMessage"] { border-radius: 14px; border: 1px solid #E4E7EF; background: #FFFFFF; padding: 0.9rem 1rem; }
[data-testid="stExpander"] { border-radius: 12px; background: #FFFFFF; }
[data-testid="stStatusWidget"], [data-testid="stStatus"] { border-radius: 12px; }

button:focus-visible, a:focus-visible, textarea:focus-visible, input:focus-visible {
    outline: 2px solid #6C47FF !important; outline-offset: 2px;
}
@media (max-width: 640px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .acc-hero { padding: 1.2rem 1.1rem; }
    .acc-hero-title { font-size: 1.4rem; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }

/* ================= v2: reference-inspired layer ================= */
.stApp {
    background:
        radial-gradient(900px 420px at 6% -8%, #E9E1FF 0%, rgba(233,225,255,0) 70%),
        radial-gradient(700px 360px at 100% 0%, #FDE8F3 0%, rgba(253,232,243,0) 70%),
        #F7F7FC;
}
[data-testid="stSidebar"] { background: #FFFFFF; }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: #EEE9FF; color: #4B2FD0; font-weight: 650; }

/* greeting + ask box */
.acc-greet { text-align: center; font-size: 2.15rem; font-weight: 700; letter-spacing: -0.025em; margin-top: 0.4rem; }
.acc-accent { color: #6C47FF; }
.acc-greet-sub { text-align: center; color: #5B6275; font-size: 1.02rem; margin: 0.3rem 0 1.4rem 0; }
.st-key-ask_box {
    max-width: 820px; margin: 0 auto 0.4rem auto; padding: 0.75rem 0.9rem; border-radius: 18px; border: 2px solid transparent;
    background: linear-gradient(#FFFFFF, #FFFFFF) padding-box, linear-gradient(90deg, #60A5FA, #8B5CF6, #EC4899, #F59E0B) border-box;
    box-shadow: 0 10px 34px rgba(108, 71, 255, 0.14);
}
.st-key-ask_box [data-testid="stForm"] { border: none; padding: 0; }
.st-key-ask_box input { border: none !important; box-shadow: none !important; font-size: 1rem; }
.acc-center-note { text-align: center; font-size: 0.86rem; color: #5B6275; margin: 0.4rem 0 1.6rem 0; }
.acc-starters-title { text-align: center; font-size: 0.95rem; font-weight: 650; margin: 1.4rem 0 0.9rem 0; }

/* clickable gradient tiles (the whole tile is the button) */
.acc-tile {
    border-radius: 16px; padding: 1rem 1.1rem; color: #FFFFFF; min-height: 118px; box-sizing: border-box;
    box-shadow: 0 6px 18px rgba(30, 20, 80, 0.10); transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.acc-tile-icon { width: 36px; height: 36px; border-radius: 10px; background: rgba(255, 255, 255, 0.22); display: grid; place-items: center; }
.acc-tile-title { font-weight: 650; font-size: 1.02rem; margin: 0.7rem 0 0.2rem 0; }
.acc-tile-text { font-size: 0.85rem; line-height: 1.4; opacity: 0.95; }
.acc-tile-blue   { background: linear-gradient(135deg, #3B82F6, #2563EB); }
.acc-tile-purple { background: linear-gradient(135deg, #8B5CF6, #6D28D9); }
.acc-tile-green  { background: linear-gradient(135deg, #10B981, #047857); }
.acc-tile-orange { background: linear-gradient(135deg, #EA580C, #C2410C); }
.acc-tile-teal   { background: linear-gradient(135deg, #14B8A6, #0F766E); }
.acc-tile-pink   { background: linear-gradient(135deg, #EC4899, #BE185D); }
[class*="st-key-tile_"] { position: relative; }
[class*="st-key-tile_"] [data-testid="stElementContainer"]:has(button) { position: absolute; inset: 0; z-index: 2; }
[class*="st-key-tile_"] button { width: 100%; height: 100%; opacity: 0; cursor: pointer; }
[class*="st-key-tile_"]:hover .acc-tile { transform: translateY(-2px); box-shadow: 0 12px 26px rgba(30, 20, 80, 0.18); }
[class*="st-key-tile_"]:focus-within .acc-tile { outline: 3px solid #6C47FF; outline-offset: 2px; }

/* workspace section switcher: a radio styled as tabs */
.st-key-ws_section_w [role="radiogroup"] {
    gap: 0.3rem; flex-wrap: wrap; background: #FFFFFF; border: 1px solid #E4E7EF; border-radius: 14px; padding: 0.3rem; width: fit-content; max-width: 100%;
}
.st-key-ws_section_w label { margin: 0; padding: 0.45rem 0.95rem; border-radius: 10px; cursor: pointer; }
.st-key-ws_section_w label > div:first-child { display: none; }
.st-key-ws_section_w label p { margin: 0; font-weight: 600; font-size: 0.92rem; }
.st-key-ws_section_w label:has(input:checked) { background: #EEE9FF; color: #4B2FD0; }
.st-key-ws_section_w label:hover { background: #F6F3FF; }

/* big score ring + document title (analyzer view) */
.acc-ring-lg { width: 200px; height: 200px; }
.acc-ring-lg .acc-ring-inner { width: 156px; height: 156px; }
.acc-ring-lg .acc-ring-val { font-size: 3rem; }
.acc-ring-empty { background: #ECE9F7 !important; }
.acc-ring-empty .acc-ring-val { color: #9AA1B2; }
.acc-doc-title { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.01em; margin-top: 0.6rem; overflow-wrap: anywhere; }
.acc-doc-sub { font-size: 0.92rem; color: #5B6275; margin-bottom: 0.9rem; }

/* feedback rows */
.acc-fb { display: flex; align-items: flex-start; gap: 0.6rem; padding: 0.55rem 0.8rem; border-radius: 10px; margin: 0.4rem 0; font-size: 0.9rem; line-height: 1.45; }
.acc-fb-ok { background: #E8F6EE; color: #17613A; }
.acc-fb-warn { background: #FFF4E0; color: #7A4F00; }
.acc-fb b { flex: 0 0 auto; }

/* chips with a leading plus (missing keywords) */
.acc-chip-plus::before { content: "+ "; font-weight: 700; }

/* gradient avatar on agent cards */
.acc-avatar { background: linear-gradient(135deg, #8B5CF6, #6C47FF); color: #FFFFFF; }
.acc-kpi-ico { display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 8px; background: #EEE9FF; color: #4B2FD0; margin-bottom: 0.5rem; }
</style>
"""

_COMPACT_CSS = """
<style>
.block-container { padding-top: 1rem; }
[data-testid="stVerticalBlock"] { gap: 0.6rem; }
.acc-hero { padding: 1.1rem 1.3rem; }
</style>
"""


def apply_theme():
    st.markdown(_CSS, unsafe_allow_html=True)
    if get_prefs().get("compact"):
        st.markdown(_COMPACT_CSS, unsafe_allow_html=True)
    try:
        st.logo("assets/logo.svg")
    except Exception:
        pass


def status_pill(label, kind="idle"):
    """Pill HTML. Every state has an icon and a text label, never colour alone."""
    icons = {"ok": "\u25cf", "warn": "\u25b2", "err": "\u2715", "idle": "\u25cb"}
    icon = icons.get(kind, "\u25cb")
    return (
        f'<span class="acc-pill acc-pill-{kind}">'
        f'<span aria-hidden="true">{icon}</span>{label}</span>'
    )


def render_header():
    if groq_key_configured():
        pill = status_pill("API key configured", "ok")
    else:
        pill = status_pill("API key missing", "warn")
    st.markdown(
        f'<div class="acc-header acc-root"><div><div class="acc-title">{APP_NAME}</div>'
        f'<div class="acc-subtitle">{APP_SUBTITLE}</div></div><div>{pill}</div></div>',
        unsafe_allow_html=True,
    )


def page_title(title, caption=None):
    markup = f'<div class="acc-page-title">{title}</div>'
    if caption:
        markup += f'<div class="acc-page-caption">{caption}</div>'
    st.markdown(markup, unsafe_allow_html=True)


def render_sidebar_status():
    status = resume_status()
    stats = agent_stats()
    rows = [
        ("Resume", "Loaded" if status["loaded"] else "Not loaded"),
        ("Analysis", "Complete" if status["analysis_done"] else "Pending"),
        ("Runs this session", str(stats["total"])),
    ]
    system = [
        ("LLM provider", "Groq"),
        ("API key", "Configured" if groq_key_configured() else "Missing"),
        ("Version", APP_VERSION),
    ]

    def block(label, items):
        body = "".join(f'<div class="acc-side-row"><span>{k}</span><span>{v}</span></div>' for k, v in items)
        return f'<div class="acc-side-label">{label}</div>{body}'

    with st.sidebar:
        st.markdown(block("Session", rows) + block("System", system), unsafe_allow_html=True)