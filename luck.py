"""
luck.py — the "Exam Luck Today" one-tap game, shared by the Home and Exam Luck pages.
"""

import random
import time

import streamlit as st

from loader import loading

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
    "The hardest chapter is the one you skipped. Enjoy failing it 💀",
    "You studied everything except what's coming. Congrats 😬",
    "Your calculator dies mid-exam, and so does your CGPA 🔋",
    "The question you ignored for 3 months is Question 1 🪦",
    "Everyone around you knows the answers. You know the room number 😶",
    "Surprise quiz today. Your 'I'll study tomorrow' era is over ☠️",
]


def _roll() -> None:
    with loading("Reading your fate…"):
        time.sleep(2)
    luck = random.randint(1, 100)
    pool = GOOD if luck >= 67 else OKAY if luck >= 34 else BAD
    st.session_state.luck = luck
    st.session_state.luck_msg = random.choice(pool)


def exam_luck_game(show_study_link: bool = True) -> None:
    """Render the game: one button, a random luck %, and a funny message."""
    rolled = st.button("🎲 Check your luck", use_container_width=True, type="primary")
    if rolled:
        _roll()

    if "luck" not in st.session_state:
        return

    luck = st.session_state.luck
    st.metric("Your luck today", f"{luck}%")
    st.progress(luck / 100)
    st.subheader(st.session_state.luck_msg)
    if rolled and luck >= 67:
        st.balloons()
    elif rolled and luck < 34:
        st.snow()
    st.caption("Screenshot it and share with your friends 📸")
    if show_study_link:
        st.page_link("pages/1_Question_Bank.py", label="Study with past papers", icon="📚", use_container_width=True)
