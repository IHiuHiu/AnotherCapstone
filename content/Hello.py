import streamlit as st

st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
)

st.write("# Welcome to the Healthcare Application 👋")

st.sidebar.success("What do you want to do?")

st.markdown(
    """
    Introduction stuff blablabla
"""
)
from shillelagh.backends.apsw.db import connect
conn = connect('https://docs.google.com/spreadsheets/d/1m2SZgMap_UpqFDc9anr1Ac6hXPc9u65KZRLTHWZhZtk/edit?usp=sharing')
result = conn.execute("""
    SELECT
        *
    FROM
        "https://docs.google.com/spreadsheets/d/1m2SZgMap_UpqFDc9anr1Ac6hXPc9u65KZRLTHWZhZtk/edit?usp=sharing"
""", headers=1)
for row in result:
    print(row)
