"""
📤 Upload — Let any user submit a question paper image for review.
"""

import streamlit as st
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import sys
import os

# Ensure the root directory is in sys.path so we can import db_manager on Streamlit Cloud
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from loader import loading
from db_manager import add_question, DEPARTMENTS, QUESTION_TYPES, init_db

init_db()
load_dotenv(override=True)

MAX_FILE_MB = 10

# ── Cloudinary configuration ────────────────────────────────────────────────

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="Upload Question", page_icon="📤", layout="centered", initial_sidebar_state="expanded")

# ── Header ──────────────────────────────────────────────────────────────────

st.title("Upload a Question Paper")
st.caption("Share previous exam questions with the university community. All uploads are reviewed before publication.")

# ── Check Cloudinary config ─────────────────────────────────────────────────

if not os.getenv("CLOUDINARY_CLOUD_NAME"):
    st.error(
        "⚠️ Cloudinary credentials are not configured. "
        "Please create a `.env` file from `.env.example` and fill in your Cloudinary details."
    )
    st.stop()

# ── Upload form ─────────────────────────────────────────────────────────────

with st.form("upload_form", clear_on_submit=True):
    st.subheader("Question Details")

    col1, col2 = st.columns(2)
    with col1:
        department = st.selectbox("Department", options=DEPARTMENTS)
        course_code = st.text_input("Course Code (e.g., CSE101)")
    with col2:
        question_type = st.selectbox("Question Type", options=QUESTION_TYPES)
        faculty_initial = st.text_input("Faculty Initial (e.g., ABC)")

    st.subheader("Question File")
    uploaded_file = st.file_uploader(
        "Upload a clear photo or PDF of the question paper",
        type=["jpg", "jpeg", "png", "pdf"],
        help=f"Accepted formats: JPG, JPEG, PNG, PDF (max {MAX_FILE_MB} MB)",
    )

    submitted = st.form_submit_button("Submit", use_container_width=True)

if submitted:
    # ── Validate ────────────────────────────────────────────────────────
    if not course_code.strip() or not faculty_initial.strip():
        st.warning("Please fill in both Course Code and Faculty Initial.")
        st.stop()
    if not uploaded_file:
        st.warning("Please upload an image or PDF before submitting.")
        st.stop()
    if uploaded_file.size > MAX_FILE_MB * 1024 * 1024:
        st.warning(f"File is too large. Maximum size is {MAX_FILE_MB} MB.")
        st.stop()

    file_type = "pdf" if uploaded_file.name.lower().endswith(".pdf") else "image"

    # ── Upload to Cloudinary ────────────────────────────────────────────
    with loading(f"Uploading your {file_type}…"):
        try:
            # PDFs are stored as 'image' resources so Cloudinary can render page previews.
            result = cloudinary.uploader.upload(
                uploaded_file,
                folder="question_bank",
                resource_type="image",
            )
            image_url = result["secure_url"]
        except Exception as e:
            st.error(f"Upload failed: {e}")
            st.stop()

    # ── Save to database ────────────────────────────────────────────────
    with loading("Saving…"):
        add_question(department, course_code.strip().upper(), faculty_initial.strip().upper(), question_type, image_url, file_type)

    st.success("✅ Upload successful! Your question has been submitted and is now pending admin review.")
    st.balloons()
