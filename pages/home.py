"""
app.py — Main entry point for the University Question Bank System.

Run with:  streamlit run app.py
"""

import streamlit as st
import sys
import os

# Ensure the root directory is in sys.path so we can import db_manager on Streamlit Cloud
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from db_manager import init_db, get_status_counts
from loader import loading
from luck import exam_luck_game

# ── Page configuration ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Southeast University Question Bank",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Initialise database on first run ────────────────────────────────────────

with loading("Loading…"):
    init_db()


# ── Stats ───────────────────────────────────────────────────────────────────

with loading("Loading stats…"):
    counts = get_status_counts()
    approved = counts.get("Approved", 0)
    pending = counts.get("Pending", 0)
total = approved + pending

# ── Header ──────────────────────────────────────────────────────────────────

st.title("🎓 SEU Question Bank")
st.caption("A centralized platform for students to share and access previous exam question papers.")

# ── Stats cards ─────────────────────────────────────────────────────────────

col1, col2, col3 = st.columns(3)
col1.metric("Total Questions", total)
col2.metric("Approved", approved)
col3.metric("Pending Review", pending)

# ── Quick guide ─────────────────────────────────────────────────────────────

st.divider()
st.subheader("Get Started")
st.markdown(
    """
Use the **sidebar** to navigate:

- **📚 Question Bank** — Browse approved exam papers
- **📤 Upload** — Submit a new question paper
- **🔒 Admin** — Review pending uploads
"""
)

# ── Fun corner ──────────────────────────────────────────────────────────────

st.divider()
st.subheader("🎲 Exam Luck Today")
st.caption("One tap. No thinking. Let's see how lucky you are!")
exam_luck_game(show_study_link=False)
