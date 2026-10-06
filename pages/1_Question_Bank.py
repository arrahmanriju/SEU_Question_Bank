"""
📚 Question Bank — Browse approved exam questions via folder drill-down.

Navigation hierarchy:  Department → Course → Faculty → Questions
"""

import streamlit as st
import sys
import os

# Ensure the root directory is in sys.path so we can import db_manager on Streamlit Cloud
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from db_manager import (
    get_departments,
    get_courses,
    get_faculty,
    get_questions,
    search_questions,
    get_semesters,
    normalize_course_code,
    QUESTION_TYPES,
    init_db,
)
from loader import loading
from ui_helpers import show_paper, type_label, page_limit, load_more_button

init_db()

# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="Question Bank", page_icon="📚", layout="centered", initial_sidebar_state="expanded")

# ── Session state defaults ──────────────────────────────────────────────────

if "qb_level" not in st.session_state:
    st.session_state.qb_level = 1          # 1=dept, 2=course, 3=faculty, 4=questions
if "qb_department" not in st.session_state:
    st.session_state.qb_department = None
if "qb_course" not in st.session_state:
    st.session_state.qb_course = None
if "qb_faculty" not in st.session_state:
    st.session_state.qb_faculty = None

# ── Navigation helpers ──────────────────────────────────────────────────────

def go_to_departments():
    st.session_state.qb_level = 1
    st.session_state.qb_department = None
    st.session_state.qb_course = None
    st.session_state.qb_faculty = None

def go_to_courses(dept: str):
    st.session_state.qb_level = 2
    st.session_state.qb_department = dept
    st.session_state.qb_course = None
    st.session_state.qb_faculty = None

def go_to_faculty(course: str):
    st.session_state.qb_level = 3
    st.session_state.qb_course = course
    st.session_state.qb_faculty = None

def go_to_questions(faculty: str):
    st.session_state.qb_level = 4
    st.session_state.qb_faculty = faculty

@st.dialog("🔍 Zoomed Question", width="large")
def zoom_question(q):
    show_paper(q, width=1600)

# ── Header ──────────────────────────────────────────────────────────────────

st.title("Question Bank")
st.caption("Browse approved exam question papers. Navigate through folders or use the search below.")

# ── Search Bar ──────────────────────────────────────────────────────────────

col_s1, col_s2 = st.columns(2)
with col_s1:
    search_course = st.text_input("Search Course Code", placeholder="e.g. CSE101", key="search_course")
with col_s2:
    search_faculty = st.text_input("Search Faculty Initial", placeholder="e.g. ABC", key="search_faculty")

search_type = st.pills(
    "Question Type",
    options=QUESTION_TYPES,
    selection_mode="single",
    key="search_type",
    help="Pick a type to filter. Leave empty to show all types.",
)

semesters = get_semesters()
search_semester = None
if semesters:
    search_semester = st.selectbox("Semester", options=semesters, index=None, placeholder="All semesters", key="search_semester")

is_searching = bool(search_course.strip() or search_faculty.strip() or search_type or search_semester)

if is_searching:
    st.divider()
    with loading("Searching papers…"):
        results = search_questions(normalize_course_code(search_course), search_faculty.strip(), search_type, search_semester)
    st.subheader(f"Search Results ({len(results)})")
    
    if not results:
        st.info("No questions found matching your search. Have one? Help others by uploading it!")
        st.page_link("pages/2_Upload.py", label="📤 Upload a question paper")
    else:
        search_key = f"limit_search_{search_course.strip()}_{search_faculty.strip()}_{search_type}_{search_semester}"
        for q in results[:page_limit(search_key)]:
            with st.container(border=True):
                show_paper(q)
                st.markdown(f"**{q['course_code']}** · {type_label(q)}")
                st.caption(f"{q['department']} Dept · Faculty: {q['faculty_initial']}{' · ' + q['semester'] if q.get('semester') else ''} · Uploaded {str(q['uploaded_at'])[:10]}")
                if st.button("🔍 Zoom Question", key=f"zoom_search_{q['id']}"):
                    zoom_question(q)
        load_more_button(search_key, len(results))

    st.stop()  # Stop rendering the rest of the page (hide drill-down)

# ── Breadcrumb ──────────────────────────────────────────────────────────────


level = st.session_state.qb_level
dept = st.session_state.qb_department
course = st.session_state.qb_course
faculty = st.session_state.qb_faculty

breadcrumb_parts = ["Home"]
if level >= 2 and dept:
    breadcrumb_parts.append(dept)
if level >= 3 and course:
    breadcrumb_parts.append(course)
if level >= 4 and faculty:
    breadcrumb_parts.append(faculty)

st.markdown(" / ".join(f"**{p}**" for p in breadcrumb_parts))

# Breadcrumb navigation buttons (only show when we can go back)
if level > 1:
    cols = st.columns(4)
    with cols[0]:
        st.button("← Home", key="bc_home", on_click=go_to_departments)
    if level > 2 and dept:
        with cols[1]:
            st.button(f"← {dept}", key="bc_dept", on_click=go_to_courses, args=(dept,))
    if level > 3 and course:
        with cols[2]:
            st.button(f"← {course}", key="bc_course", on_click=go_to_faculty, args=(course,))

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# LEVEL 1 — Departments
# ═════════════════════════════════════════════════════════════════════════════

if level == 1:
    with loading("Loading departments…"):
        departments = get_departments()

    if not departments:
        st.info("No papers yet. Be the first to upload one!")
        st.page_link("pages/2_Upload.py", label="📤 Upload a question paper")
    else:
        st.subheader(f"{len(departments)} department(s)")

        cols = st.columns(3)
        for idx, d in enumerate(departments):
            with cols[idx % 3]:
                st.button(
                    f"📁 {d['department']}  ({d['count']})",
                    key=f"dept_{d['department']}",
                    use_container_width=True,
                    on_click=go_to_courses,
                    args=(d["department"],)
                )

# ═════════════════════════════════════════════════════════════════════════════
# LEVEL 2 — Courses
# ═════════════════════════════════════════════════════════════════════════════

elif level == 2:
    with loading("Loading courses…"):
        courses = get_courses(dept)

    if not courses:
        st.info("No courses found for this department yet.")
    else:
        st.subheader(f"Courses in {dept}")

        cols = st.columns(3)
        for idx, c in enumerate(courses):
            with cols[idx % 3]:
                st.button(
                    f"📂 {c['course_code']}  ({c['count']})",
                    key=f"course_{c['course_code']}",
                    use_container_width=True,
                    on_click=go_to_faculty,
                    args=(c["course_code"],)
                )

# ═════════════════════════════════════════════════════════════════════════════
# LEVEL 3 — Faculty
# ═════════════════════════════════════════════════════════════════════════════

elif level == 3:
    with loading("Loading faculty…"):
        faculty_list = get_faculty(dept, course)

    if not faculty_list:
        st.info("No faculty found for this course yet.")
    else:
        st.subheader(f"Faculty for {course}")

        cols = st.columns(3)
        for idx, f in enumerate(faculty_list):
            with cols[idx % 3]:
                st.button(
                    f"👤 {f['faculty_initial']}  ({f['count']})",
                    key=f"faculty_{f['faculty_initial']}",
                    use_container_width=True,
                    on_click=go_to_questions,
                    args=(f["faculty_initial"],)
                )

# ═════════════════════════════════════════════════════════════════════════════
# LEVEL 4 — Questions
# ═════════════════════════════════════════════════════════════════════════════

elif level == 4:
    with loading("Loading question papers…"):
        questions = get_questions(
            status="Approved",
            department=dept,
            course_code=course,
            faculty_initial=faculty,
        )

    if not questions:
        st.info("No approved questions from this faculty yet.")
    else:
        st.subheader(f"{len(questions)} question(s) — {course} · {faculty}")

        questions_key = f"limit_q_{dept}_{course}_{faculty}"
        for q in questions[:page_limit(questions_key)]:
            with st.container(border=True):
                show_paper(q)
                st.markdown(f"**{q['course_code']}** · {type_label(q)}")
                st.caption(f"{q['department']} Dept · Faculty: {q['faculty_initial']}{' · ' + q['semester'] if q.get('semester') else ''} · Uploaded {str(q['uploaded_at'])[:10]}")
                if st.button("🔍 Zoom Question", key=f"zoom_q_{q['id']}"):
                    zoom_question(q)
        load_more_button(questions_key, len(questions))
