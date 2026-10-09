"""AI Command Center: app shell.

Entry point (unchanged, so Streamlit Cloud settings stay the same). It only
sets up the page, session defaults, theme and navigation. Each page lives in
views/, and the original resume UI is views/workspace.py.
"""

import streamlit as st

st.set_page_config(
    page_title="AI Command Center",
    page_icon=":material/hub:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.session import init_session
from ui.theme import apply_theme, render_header, render_sidebar_status

init_session()
apply_theme()

pages = [
    st.Page(
        "views/overview.py",
        title="Overview",
        icon=":material/home:",
        url_path="overview",
        default=True,
    ),
    st.Page(
        "views/workspace.py",
        title="Resume Workspace",
        icon=":material/description:",
        url_path="workspace",
    ),
    st.Page(
        "views/agents.py",
        title="Agents",
        icon=":material/smart_toy:",
        url_path="agents",
    ),
    st.Page(
        "views/analytics.py",
        title="Analytics",
        icon=":material/monitoring:",
        url_path="analytics",
    ),
    st.Page(
        "views/resume_context.py",
        title="Resume Context",
        icon=":material/folder_open:",
        url_path="resume-context",
    ),
    st.Page(
        "views/settings.py",
        title="Settings",
        icon=":material/settings:",
        url_path="settings",
    ),
]

navigation = st.navigation(pages, position="sidebar")

render_sidebar_status()
render_header()

navigation.run()
