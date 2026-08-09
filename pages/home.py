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

from db_manager import init_db, count_by_status

# ── Page configuration ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Southeast University Question Bank",
    page_icon="🎓",
    layout="centered",
)

# ── Initialise database on first run ────────────────────────────────────────

init_db()

# ── Stats ───────────────────────────────────────────────────────────────────

approved = count_by_status("Approved")
pending = count_by_status("Pending")
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
