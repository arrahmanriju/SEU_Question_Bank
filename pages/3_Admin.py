"""
🔒 Admin — Review and approve (or reject) pending question uploads.
Requires login with admin credentials.
"""

import streamlit as st
from dotenv import load_dotenv
import sys
import os

# Ensure the root directory is in sys.path so we can import db_manager on Streamlit Cloud
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from db_manager import (
    get_questions, 
    approve_question, 
    reject_question, 
    count_by_status, 
    init_db,
    delete_question,
    update_question,
    DEPARTMENTS,
    QUESTION_TYPES
)

init_db()
load_dotenv(override=True)

# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="Admin Panel", page_icon="🔒", layout="centered")

# ── Admin credentials from .env ─────────────────────────────────────────────

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ── Session state for auth ──────────────────────────────────────────────────

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# ── Header ──────────────────────────────────────────────────────────────────

st.title("Admin Panel")
st.caption("Review pending uploads and manage approved questions.")

# ═════════════════════════════════════════════════════════════════════════════
# LOGIN GATE
# ═════════════════════════════════════════════════════════════════════════════

if not st.session_state.admin_authenticated:
    st.divider()
    st.subheader("Login")

    with st.form("admin_login_form"):
        username = st.text_input("Username", placeholder="Enter admin username")
        password = st.text_input("Password", type="password", placeholder="Enter admin password")
        login_btn = st.form_submit_button("Login", use_container_width=True)

    if login_btn:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password. Please try again.")

    st.stop()  # Stop here — don't render the admin panel

# ═════════════════════════════════════════════════════════════════════════════
# ADMIN PANEL (only shown after successful login)
# ═════════════════════════════════════════════════════════════════════════════

# ── Logout button in sidebar ────────────────────────────────────────────────

st.sidebar.markdown("### 👤 Admin Session")
st.sidebar.markdown(f"Logged in as **{ADMIN_USERNAME}**")
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.admin_authenticated = False
    st.rerun()

# ── Edit Dialog ─────────────────────────────────────────────────────────────

@st.dialog("Edit Question Details")
def edit_question_dialog(q):
    st.image(q["image_url"], use_container_width=True)
    
    with st.form(f"edit_form_{q['id']}"):
        col1, col2 = st.columns(2)
        with col1:
            dept_idx = DEPARTMENTS.index(q["department"]) if q["department"] in DEPARTMENTS else 0
            new_dept = st.selectbox("Department", options=DEPARTMENTS, index=dept_idx)
            new_course = st.text_input("Course Code", value=q["course_code"])
        with col2:
            type_idx = QUESTION_TYPES.index(q["question_type"]) if q["question_type"] in QUESTION_TYPES else 0
            new_type = st.selectbox("Question Type", options=QUESTION_TYPES, index=type_idx)
            new_faculty = st.text_input("Faculty Initial", value=q["faculty_initial"])
            
        submitted = st.form_submit_button("Save Changes", use_container_width=True)
        
        if submitted:
            if not new_course.strip() or not new_faculty.strip():
                st.error("Course Code and Faculty Initial cannot be empty.")
            else:
                update_question(q["id"], new_dept, new_course.strip().upper(), new_faculty.strip().upper(), new_type)
                st.success("Question updated successfully!")
                st.rerun()

# ── Tabs ────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["Pending Review", "Manage Questions"])

# ── Tab 1: Pending Queue ────────────────────────────────────────────────────

with tab1:
    pending_count = count_by_status("Pending")
    st.subheader(f"Pending Review ({pending_count})")

    pending = get_questions(status="Pending")

    if not pending:
        st.info("🎉 All clear! There are no pending questions to review.")
    else:
        for q in pending:
            with st.container(border=True):
                st.image(q["image_url"], use_container_width=True)
                st.markdown(f"**{q['course_code']}** · {q['question_type']}")
                st.caption(f"{q['department']} Dept · Faculty: {q['faculty_initial']} · Uploaded {str(q['uploaded_at'])[:10]}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve", key=f"approve_{q['id']}", use_container_width=True):
                        approve_question(q["id"])
                        st.success("Approved!")
                        st.rerun()
                with col2:
                    if st.button("❌ Reject", key=f"reject_{q['id']}", use_container_width=True):
                        reject_question(q["id"])
                        st.warning("Rejected and removed.")
                        st.rerun()

# ── Tab 2: Manage Approved Questions ────────────────────────────────────────

with tab2:
    approved = get_questions(status="Approved")
    st.subheader(f"Approved Questions ({len(approved)})")
    
    if not approved:
        st.info("No approved questions yet.")
    else:
        for q in approved:
            with st.container(border=True):
                col_img, col_info, col_actions = st.columns([1, 2, 1])
                
                with col_img:
                    st.image(q["image_url"], use_container_width=True)
                
                with col_info:
                    st.markdown(f"**{q['course_code']}** · {q['question_type']}")
                    st.caption(f"{q['department']} Dept · Faculty: {q['faculty_initial']}")
                    st.caption(f"Uploaded {str(q['uploaded_at'])[:10]}")
                    
                with col_actions:
                    if st.button("✏️ Edit", key=f"edit_btn_{q['id']}", use_container_width=True):
                        edit_question_dialog(q)
                    
                    if st.button("🗑️ Delete", key=f"delete_btn_{q['id']}", type="primary", use_container_width=True):
                        delete_question(q["id"])
                        st.success("Question deleted.")
                        st.rerun()

