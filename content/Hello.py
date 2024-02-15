import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
)

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

st.write("# Welcome to the Healthcare Application 👋")

st.sidebar.success("What do you want to do?")

st.markdown(
    """
    Introduction stuff blablabla
"""
)

df = conn.read()

# Print results.
for row in df.itertuples():
    st.write(f"{row.name} has a :{row.pet}:")
