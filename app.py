import streamlit as st

pg = st.navigation([
    st.Page("pages/home.py", title="Home", default=True),
    st.Page("pages/1_Question_Bank.py", title="Question Bank"),
    st.Page("pages/2_Upload.py", title="Upload"),
    st.Page("pages/3_Admin.py", title="Admin"),
])
pg.run()
