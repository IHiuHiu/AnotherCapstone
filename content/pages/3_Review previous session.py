import re
import pandas as pd
import numpy as np
import csv
import warnings
import streamlit as st
import streamlit_authenticator as stauth
import datetime
import psycopg2
from sqlalchemy import create_engine

st.set_page_config(page_title="Review previous record", page_icon="🔍")
st.header("----------Previous records----------")

st.sidebar.header("Review records")
st.sidebar.subheader(f'Welcome {st.session_state["current_user"]}')

conn = st.connection("postgresql", type="sql")

db = conn.query(f"SELECT * FROM sessionact WHERE username = '{st.session_state["current_user"]}';")

for x in range(db.shape[0]):
  st.markdown(f"Date: {db.loc[x]['time']}")
  st.markdown("Symptoms experienced:"
  st.write(
