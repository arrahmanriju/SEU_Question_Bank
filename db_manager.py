"""
database.py — SQLite and PostgreSQL helper functions for the Question Bank system.

Manages the 'questions' table with CRUD operations for uploading,
querying, and approving question papers.
"""

import sqlite3
import os
from datetime import datetime
import streamlit as st

try:
    import psycopg2
    from psycopg2.extras import DictCursor
except ImportError:
    psycopg2 = None

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "question_bank.db")
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_optimized_image_url(url: str, width: int = 800) -> str:
    """Insert Cloudinary transformations for auto-format, auto-quality, and resizing."""
    if "res.cloudinary.com" in url and "/upload/" in url:
        parts = url.split("/upload/")
        return f"{parts[0]}/upload/w_{width},q_auto,f_auto/{parts[1]}"
    return url



# ── Predefined lists ───────────

DEPARTMENTS = [
    "CSE",
    "English",
    "BBA",
    "EEE",
    "Textile Engineering",
    "Architecture",
    "Economics",
    "Bangla Language and Literature",
    "Law",
    "Pharmacy",
]

QUESTION_TYPES = ["CT", "Mid", "Final", "Others"]


# ── Database helpers ────────────────────────────────────────────────────────

def _is_postgres() -> bool:
    return DATABASE_URL is not None and DATABASE_URL.startswith("postgres") and psycopg2 is not None


@st.cache_resource(ttl=3600)
def _get_pg_pool():
    from psycopg2 import pool
    return pool.SimpleConnectionPool(1, 10, DATABASE_URL)

def _get_connection():
    """Return a database connection (Postgres from pool, or new SQLite)."""
    if _is_postgres():
        pool = _get_pg_pool()
        return pool.getconn()
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def _release_connection(conn):
    """Release or close the database connection."""
    if _is_postgres():
        pool = _get_pg_pool()
        pool.putconn(conn)
    else:
        conn.close()


def _execute(query: str, params: tuple = (), fetchall=False, fetchone=False, commit=False):
    """
    Execute a query. Automatically translates '?' to '%s' if Postgres.
    """
    conn = _get_connection()
    try:
        if _is_postgres():
            query = query.replace('?', '%s')
            cursor = conn.cursor(cursor_factory=DictCursor)
        else:
            cursor = conn.cursor()

        cursor.execute(query, params)

        result = None
        if fetchall:
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        elif fetchone:
            row = cursor.fetchone()
            if row:
                # If row is dictionary-like, we can turn it into dict, else it's a single value tuple
                if hasattr(row, 'keys'):
                    result = dict(row)
                else:
                    result = row[0] if len(row) == 1 else tuple(row)
            else:
                result = None

        if commit:
            conn.commit()

        return result
    finally:
        _release_connection(conn)


@st.cache_resource(show_spinner=False)
def init_db() -> None:
    """Create the questions table if it does not already exist."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        if _is_postgres():
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id              SERIAL PRIMARY KEY,
                    department      TEXT     NOT NULL,
                    course_code     TEXT     NOT NULL,
                    faculty_initial TEXT     NOT NULL,
                    question_type   TEXT     NOT NULL,
                    image_url       TEXT     NOT NULL,
                    status          TEXT     NOT NULL DEFAULT 'Pending',
                    uploaded_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id              INTEGER  PRIMARY KEY AUTOINCREMENT,
                    department      TEXT     NOT NULL,
                    course_code     TEXT     NOT NULL,
                    faculty_initial TEXT     NOT NULL,
                    question_type   TEXT     NOT NULL,
                    image_url       TEXT     NOT NULL,
                    status          TEXT     NOT NULL DEFAULT 'Pending',
                    uploaded_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        conn.commit()
    finally:
        _release_connection(conn)


def add_question(department: str, course_code: str, faculty_initial: str, question_type: str, image_url: str) -> int:
    """
    Insert a new question with status 'Pending'.
    Returns the new row id.
    """
    conn = _get_connection()
    try:
        if _is_postgres():
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO questions (department, course_code, faculty_initial, question_type, image_url, status, uploaded_at)
                VALUES (%s, %s, %s, %s, %s, 'Pending', %s) RETURNING id;
                """,
                (department, course_code, faculty_initial, question_type, image_url, datetime.now().isoformat())
            )
            row_id = cursor.fetchone()[0]
            conn.commit()
            st.cache_data.clear()
            return row_id
        else:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO questions (department, course_code, faculty_initial, question_type, image_url, status, uploaded_at)
                VALUES (?, ?, ?, ?, ?, 'Pending', ?);
                """,
                (department, course_code, faculty_initial, question_type, image_url, datetime.now().isoformat())
            )
            conn.commit()
            st.cache_data.clear()
            return cursor.lastrowid
    finally:
        _release_connection(conn)


@st.cache_data(ttl=60, show_spinner=False)
def get_questions(
    status: str | None = None,
    department: str | None = None,
    question_type: str | None = None,
    course_code: str | None = None,
    faculty_initial: str | None = None,
) -> list[dict]:
    """
    Fetch questions with optional filters.
    Returns a list of dicts.
    """
    query = "SELECT * FROM questions WHERE 1=1"
    params: list = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if department:
        query += " AND department = ?"
        params.append(department)
    if question_type:
        query += " AND question_type = ?"
        params.append(question_type)
    if course_code:
        query += " AND course_code = ?"
        params.append(course_code)
    if faculty_initial:
        query += " AND faculty_initial = ?"
        params.append(faculty_initial)

    query += " ORDER BY uploaded_at DESC"
    return _execute(query, tuple(params), fetchall=True)


@st.cache_data(ttl=60, show_spinner=False)
def search_questions(course_query: str, faculty_query: str) -> list[dict]:
    """Search approved questions by partial course code or faculty initial."""
    query = "SELECT * FROM questions WHERE status = 'Approved'"
    params = []
    
    op = "ILIKE" if _is_postgres() else "LIKE"
    
    if course_query:
        query += f" AND course_code {op} ?"
        params.append(f"%{course_query}%")
    if faculty_query:
        query += f" AND faculty_initial {op} ?"
        params.append(f"%{faculty_query}%")
        
    query += " ORDER BY uploaded_at DESC"
    return _execute(query, tuple(params), fetchall=True)


@st.cache_data(ttl=60, show_spinner=False)
def get_departments() -> list[dict]:
    """
    Return distinct departments that have at least one approved question,
    along with the count of approved questions per department.
    """
    query = """
        SELECT department, COUNT(*) as count
        FROM questions
        WHERE status = 'Approved'
        GROUP BY department
        ORDER BY department;
    """
    return _execute(query, fetchall=True)


@st.cache_data(ttl=60, show_spinner=False)
def get_courses(department: str) -> list[dict]:
    """
    Return distinct course codes for a given department (approved only),
    along with the count of approved questions per course.
    """
    query = """
        SELECT course_code, COUNT(*) as count
        FROM questions
        WHERE status = 'Approved' AND department = ?
        GROUP BY course_code
        ORDER BY course_code;
    """
    return _execute(query, (department,), fetchall=True)


@st.cache_data(ttl=60, show_spinner=False)
def get_faculty(department: str, course_code: str) -> list[dict]:
    """
    Return distinct faculty initials for a given department + course combo
    (approved only), along with the count of approved questions per faculty.
    """
    query = """
        SELECT faculty_initial, COUNT(*) as count
        FROM questions
        WHERE status = 'Approved' AND department = ? AND course_code = ?
        GROUP BY faculty_initial
        ORDER BY faculty_initial;
    """
    return _execute(query, (department, course_code), fetchall=True)


def approve_question(question_id: int) -> None:
    """Set a question's status to 'Approved'."""
    _execute("UPDATE questions SET status = 'Approved' WHERE id = ?;", (question_id,), commit=True)
    st.cache_data.clear()


def reject_question(question_id: int) -> None:
    """Delete a pending question from the database."""
    _execute("DELETE FROM questions WHERE id = ?;", (question_id,), commit=True)
    st.cache_data.clear()


def delete_question(question_id: int) -> None:
    """Delete any question from the database."""
    _execute("DELETE FROM questions WHERE id = ?;", (question_id,), commit=True)
    st.cache_data.clear()


def update_question(question_id: int, department: str, course_code: str, faculty_initial: str, question_type: str) -> None:
    """Update details of an existing question."""
    query = """
        UPDATE questions 
        SET department = ?, course_code = ?, faculty_initial = ?, question_type = ?
        WHERE id = ?;
    """
    _execute(query, (department, course_code, faculty_initial, question_type, question_id), commit=True)
    st.cache_data.clear()

@st.cache_data(ttl=60)
def count_by_status(status: str) -> int:
    """Return the count of questions with the given status."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        if _is_postgres():
            cursor.execute("SELECT COUNT(*) FROM questions WHERE status = %s;", (status,))
        else:
            cursor.execute("SELECT COUNT(*) FROM questions WHERE status = ?;", (status,))
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        _release_connection(conn)
