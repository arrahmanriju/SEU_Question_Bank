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
from db_manager import add_question, DEPARTMENTS, QUESTION_TYPES, init_db, semester_options, normalize_course_code

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

# ── Tips ────────────────────────────────────────────────────────────────────

with st.expander("📝 Tips for a good upload"):
    st.markdown(
        """
- Make sure the **whole page** is visible, well lit and readable.
- A paper with several pages? Select **all pages at once**.
- Pick the correct **semester** — it helps others find the right paper.
- Don't include personal information (names, student IDs).
"""
    )

# ── Upload form ─────────────────────────────────────────────────────────────

with st.form("upload_form", clear_on_submit=True):
    st.subheader("Question Details")

    col1, col2 = st.columns(2)
    with col1:
        department = st.selectbox("Department", options=DEPARTMENTS)
        course_code = st.text_input("Course Code (e.g., CSE101)")
        semester = st.selectbox("Semester", options=semester_options())
    with col2:
        question_type = st.selectbox("Question Type", options=QUESTION_TYPES)
        faculty_initial = st.text_input("Faculty Initial (e.g., ABC)")

    st.subheader("Question File(s)")
    uploaded_files = st.file_uploader(
        "Upload clear photos or PDFs of the question paper",
        type=["jpg", "jpeg", "png", "pdf"],
        accept_multiple_files=True,
        help=f"Accepted formats: JPG, JPEG, PNG, PDF (max {MAX_FILE_MB} MB each). Select several files to upload multiple pages.",
    )

    submitted = st.form_submit_button("Submit", use_container_width=True)

if submitted:
    # ── Validate ────────────────────────────────────────────────────────
    code = normalize_course_code(course_code)
    faculty = faculty_initial.strip().upper()
    if not code or not faculty:
        st.warning("Please fill in both Course Code and Faculty Initial.")
        st.stop()
    if not uploaded_files:
        st.warning("Please upload at least one image or PDF before submitting.")
        st.stop()
    too_big = [f.name for f in uploaded_files if f.size > MAX_FILE_MB * 1024 * 1024]
    if too_big:
        st.warning(f"These files are over {MAX_FILE_MB} MB: {', '.join(too_big)}")
        st.stop()

    # ── Upload to Cloudinary + save ─────────────────────────────────────
    saved = 0
    for f in uploaded_files:
        file_type = "pdf" if f.name.lower().endswith(".pdf") else "image"
        with loading(f"Uploading {f.name}…"):
            try:
                # PDFs are stored as 'image' resources so Cloudinary can render page previews.
                result = cloudinary.uploader.upload(f, folder="question_bank", resource_type="image")
            except Exception as e:
                st.error(f"Upload of {f.name} failed: {e}")
                continue
            add_question(department, code, faculty, question_type, result["secure_url"], file_type, semester)
            saved += 1

    if saved:
        st.success(f"✅ {saved} file(s) submitted for {code} ({semester}). They are now pending admin review. Thank you for contributing!")
        st.balloons()
        st.info("Want to add another paper? Just fill the form again.")
    else:
        st.error("Nothing was uploaded. Please try again.")
