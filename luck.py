"""
luck.py — the "Exam Luck Today" one-tap game, shared by the Home and Exam Luck pages.
"""

import random

import streamlit as st

GOOD = [
    "Your Final will be super easy 🍀",
    "Teacher forgot to check attendance 🎉",
    "The exam is postponed! 🥳",
    "Every question comes from the past papers 📚",
    "Free marks on the first question 🎁",
    "The strict invigilator is on leave 😎",
]
OKAY = [
    "Half the paper is easy, half is a mystery 🤔",
    "You will remember the answer right after the exam 😅",
    "A pen will run out of ink, but you'll have a spare 🖊️",
    "Average luck. Revise one more chapter 📖",
]
BAD = [
    "Surprise quiz incoming 😬",
    "Teacher says: 'Open book? No.' 😶",
    "Your calculator battery dies mid-exam 🔋",
    "The hardest chapter is your weakest one 💀",
]


def _roll() -> None:
    luck = random.randint(1, 100)
    pool = GOOD if luck >= 67 else OKAY if luck >= 34 else BAD
    st.session_state.luck = luck
    st.session_state.luck_msg = random.choice(pool)


def exam_luck_game(show_study_link: bool = True) -> None:
    """Render the game: one button, a random luck %, and a funny message."""
    st.button("🎲 Check my luck", on_click=_roll, use_container_width=True, type="primary")

    if "luck" not in st.session_state:
        return

    luck = st.session_state.luck
    st.metric("Your luck today", f"{luck}%")
    st.progress(luck / 100)
    st.subheader(st.session_state.luck_msg)
    if luck >= 67:
        st.balloons()
    elif luck < 34:
        st.snow()
    st.caption("Screenshot it and share with your friends 📸")
    if show_study_link:
        st.page_link("pages/1_Question_Bank.py", label="Study with past papers", icon="📚", use_container_width=True)
