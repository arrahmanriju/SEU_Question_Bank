"""
🎲 Exam Luck Today — a one-tap fun page. No thinking required.
"""

import sys
import os

# Ensure the root directory is in sys.path so we can import luck on Streamlit Cloud
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st

from luck import exam_luck_game

st.set_page_config(page_title="Exam Luck Today", page_icon="🎲", layout="centered", initial_sidebar_state="expanded")

st.title("🎲 Exam Luck Today")
st.caption("One tap. No thinking. Let's see how lucky you are!")

exam_luck_game()
