"""
luck.py — the "Exam Luck" one-tap game, shared by the Home and Exam Luck pages.
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
    "You'll guess every MCQ right and have no idea why 🎯",
    "The teacher gives a 'hint' that is literally the answer 🤫",
    "You studied one chapter and the whole paper is from it 🙏",
    "You'll finish early and still get full marks. Suspicious 🤨",
    "Your handwriting is finally readable. The teacher gives you extra marks 🖋️",
    "The invigilator is asleep. Nobody is judging today 😴",
]
OKAY = [
    "Half the paper is easy, half is a mystery 🤔",
    "You will remember the answer right after the exam 😅",
    "A pen will run out of ink, but you'll have a spare 🖊️",
    "Average luck. Revise one more chapter 📖",
    "You'll know exactly 2 answers, and both will be the wrong question 🫠",
    "Half the paper is easy, the other half is written in alien language 👽",
    "You'll finish early, then spend 20 minutes regretting every answer 🕰️",
    "Your friend sitting next to you knows nothing either. No help today 🤝",
    "The easy questions are worth 2 marks. The hard ones are worth your soul 😮‍💨",
    "You'll write 6 pages of confidence. The teacher will give 6 marks of pity 📝",
    "Pass mark? Close. Dignity? Missing 🚶",
    "You'll solve it perfectly... right after you leave the hall 🚪",
    "You'll answer with 100% confidence and 40% accuracy 😎",
    "The paper is fair. Your preparation is not 🫥",
    "You'll pass, then lie to everyone about how hard it was 🎭",
    "Three questions you know, three you fake, one you pray for 🙏",
]
BAD = [
    "The hardest chapter is the one you skipped. Enjoy failing it 💀",
    "You studied everything except what's coming. Congrats 😬",
    "Your calculator dies mid-exam, and so does your CGPA 🔋",
    "The question you ignored for 3 months is Question 1 🪦",
    "Everyone around you knows the answers. You know the room number 😶",
    "Surprise quiz today. Your 'I'll study tomorrow' era is over ☠️",
    "You'll stare at Question 1 so long it starts staring back 👁️",
    "Your brain goes blank, and so does the answer sheet 📄",
    "The teacher's mercy ended last semester 🪦",
    "You'll write 'Sir, I know this' in the answer sheet. Sir does not care 😭",
    "Everything you memorized last night is gone. Only the stress remains 🧠",
    "The paper is easy. You still won't make it 🫡",
    "Retake season is calling your name 📞",
]


def _mood(luck: int) -> tuple[str, str, str]:
    """(css color, streamlit color name, face) — red and sad below 50%."""
    if luck < 50:
        return "#e5484d", "red", "😭"
    if luck < 67:
        return "#f5a524", "orange", "😐"
    return "#30a46c", "green", "😄"


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
    color, name, face = _mood(luck)
    st.markdown(
        f"<div style='text-align:center'>"
        f"<div style='opacity:.6;font-size:.85rem'>Luck of your next exam</div>"
        f"<div style='font-size:3.2rem;font-weight:700;color:{color};line-height:1.1'>{face} {luck}%</div>"
        f"<div style='height:12px;border-radius:6px;background:rgba(128,128,128,.25);margin:.6rem 0 1rem'>"
        f"<div style='height:100%;width:{luck}%;border-radius:6px;background:{color}'></div></div></div>",
        unsafe_allow_html=True,
    )
    st.subheader(f":{name}[{st.session_state.luck_msg}]")
    if rolled and luck >= 67:
        st.balloons()
    elif rolled and luck < 34:
        st.snow()
    st.caption("Screenshot it and share with your friends 📸")
    if show_study_link:
        st.page_link("pages/1_Question_Bank.py", label="Study with past papers", icon="📚", use_container_width=True)
