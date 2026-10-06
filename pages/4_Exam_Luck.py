"""
🎲 Exam Luck Today — a one-tap fun page. No thinking required.
"""

import random

import streamlit as st

st.set_page_config(page_title="Exam Luck Today", page_icon="🎲", layout="centered", initial_sidebar_state="expanded")

# (message, luck range) — good results get balloons, bad ones get snow.
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

st.title("🎲 Exam Luck Today")
st.caption("One tap. No thinking. Let's see how lucky you are!")


def roll() -> None:
    luck = random.randint(1, 100)
    pool = GOOD if luck >= 67 else OKAY if luck >= 34 else BAD
    st.session_state.luck = luck
    st.session_state.luck_msg = random.choice(pool)


st.button("🎲 Check my luck", on_click=roll, use_container_width=True, type="primary")

if "luck" in st.session_state:
    luck = st.session_state.luck
    st.divider()
    st.metric("Your luck today", f"{luck}%")
    st.progress(luck / 100)
    st.subheader(st.session_state.luck_msg)
    if luck >= 67:
        st.balloons()
    elif luck < 34:
        st.snow()
    st.caption("Screenshot it and share with your friends 📸")
    st.page_link("pages/1_Question_Bank.py", label="Study with past papers", icon="📚", use_container_width=True)
