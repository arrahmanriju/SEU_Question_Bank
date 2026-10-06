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

# ── Main actions ────────────────────────────────────────────────────────────

btn1, btn2 = st.columns(2)
with btn1:
    st.page_link("pages/1_Question_Bank.py", label="Find papers", icon="📚", use_container_width=True)
with btn2:
    st.page_link("pages/2_Upload.py", label="Upload a paper", icon="📤", use_container_width=True)

# ── Stats cards ─────────────────────────────────────────────────────────────

col1, col2 = st.columns(2)
col1.metric("Papers available", approved)
col2.metric("Waiting for review", pending)

# ── Quick guide ─────────────────────────────────────────────────────────────

st.divider()
st.subheader("How it works")
st.markdown(
    """
1. **Find** — open the Question Bank, browse by department or search by course code.
2. **Share** — got an old paper? Upload a photo or PDF in under a minute. No login needed.
3. **Reviewed** — an admin checks every upload before it goes public.
"""
)
