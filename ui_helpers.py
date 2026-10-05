"""
ui_helpers.py — Shared Streamlit rendering for question papers (image or PDF).
"""

import streamlit as st

from db_manager import is_pdf, get_preview_url


def show_paper(q: dict, width: int = 800) -> None:
    """Render a question's image, or page 1 of a PDF with an 'Open PDF' link."""
    st.image(get_preview_url(q, width), use_container_width=True)
    if is_pdf(q):
        st.link_button("📄 Open full PDF", q["image_url"], use_container_width=True)


def type_label(q: dict) -> str:
    return f"{q['question_type']} · PDF" if is_pdf(q) else q["question_type"]
