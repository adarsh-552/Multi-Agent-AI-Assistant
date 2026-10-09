"""Settings: model info, API status, interface preferences, session reset."""

import streamlit as st

from core.registry import AGENTS, model_for, temperature_for
from core.session import APP_VERSION, get_prefs, groq_key_configured, reset_session
from ui import components as ui
from ui.theme import page_title

page_title("Settings", "Model configuration, API status and interface preferences.")

prefs = get_prefs()

# ---------------- models ----------------
with st.container(border=True):
    ui.section("Models", "Read from the specialist modules. Change them in the code, not here.")
    rows = [
        {
            "Specialist": a["name"],
            "Model": model_for(a),
            "Temperature": temperature_for(a),
            "Source file": a["file"],
        }
        for a in AGENTS
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)
    ui.note("Provider: Groq, through LangChain. Max tokens are not set in the code, so library defaults apply.")

# ---------------- API ----------------
with st.container(border=True):
    ui.section("API configuration")
    if groq_key_configured():
        ui.html(ui.pill("Groq API key configured", "ok"))
    else:
        ui.html(ui.pill("Groq API key missing", "warn"))
        ui.note("Add GROQ_API_KEY to your environment or Streamlit secrets.")
    ui.note("This only checks that a key exists. It does not call the API, and the key is never shown.")


# ---------------- interface ----------------
def _save(pref_key, widget_key):
    prefs[pref_key] = st.session_state[widget_key]


with st.container(border=True):
    ui.section("Interface")
    for pref_key, label, help_text in [
        ("compact", "Compact layout", "Tighter spacing on every page."),
        ("run_details", "Show run details", "Show the model and response time under each result."),
        ("timestamps", "Show timestamps", "Show times in chat, results and recent activity."),
    ]:
        widget_key = f"pref_{pref_key}"
        if widget_key not in st.session_state:
            st.session_state[widget_key] = prefs[pref_key]
        st.toggle(label, key=widget_key, help=help_text, on_change=_save, args=(pref_key, widget_key))

# ---------------- session ----------------
with st.container(border=True):
    ui.section("Session")
    ui.note("Resetting clears the resume, all results, the chat and the run history for this session.")
    confirm = st.checkbox("I understand this cannot be undone", key="confirm_reset")
    if st.button("Reset session", icon=":material/restart_alt:", disabled=not confirm):
        reset_session()
        st.rerun()

# ---------------- about ----------------
with st.container(border=True):
    ui.section("About")
    ui.html(
        '<div class="acc-row"><span>Application</span><span class="acc-row-main">AI Command Center</span></div>'
        f'<div class="acc-row"><span>Version</span><span class="acc-row-main">{ui.esc(APP_VERSION)}</span></div>'
    )
