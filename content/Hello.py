import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
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

conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM Streamlit;', ttl="10m")

# Print results.
for row in df.itertuples():
    st.write(row)



#from shillelagh.backends.apsw.db import connect
#sheets_url='https://docs.google.com/spreadsheets/d/1m2SZgMap_UpqFDc9anr1Ac6hXPc9u65KZRLTHWZhZtk/edit#gid=0'
#csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
#result1 = pd.read_csv(csv_url)
#conn = connect(sheets_url)
#result2 = conn.execute("""
#    SELECT
#        *
#    FROM
#        "https://docs.google.com/spreadsheets/d/1m2SZgMap_UpqFDc9anr1Ac6hXPc9u65KZRLTHWZhZtk/edit?usp=sharing"
#""", headers=1)
#for  in pd.DataFrame(result1):
#    st.write(row + '1')
#for row in result2:
#    print(row + '2')
