"""
ui_helpers.py — Shared Streamlit rendering for question papers (image or PDF).
"""

import streamlit as st

from db_manager import is_pdf, get_preview_url, get_download_url


def show_paper(q: dict, width: int = 800) -> None:
    """Render a question's image (or page 1 of a PDF) with download / open-PDF buttons."""
    st.image(get_preview_url(q, width), use_container_width=True)
    if is_pdf(q):
        col_open, col_dl = st.columns(2)
        col_open.link_button("📄 Open PDF", q["image_url"], use_container_width=True)
        col_dl.link_button("⬇️ Download", get_download_url(q), use_container_width=True)
    else:
        st.link_button("⬇️ Download", get_download_url(q), use_container_width=True)


def type_label(q: dict) -> str:
    return f"{q['question_type']} · PDF" if is_pdf(q) else q["question_type"]
