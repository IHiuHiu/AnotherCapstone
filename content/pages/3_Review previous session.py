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

@st.cache_data
def getSeverityDict():
    severityDictionary = dict()
    with open('./MasterData/Symptom_severity.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        try:
            for row in csv_reader:
                _diction={row[0]:int(row[1])}
                severityDictionary.update(_diction)
        except:
            pass
    return severityDictionary

with st.spinner("Retrieving records from DB..."):
  severityDictionary = getSeverityDictionary()
  
  conn = st.connection("postgresql", type="sql")
  user = st.session_state["current_user"]
  db = conn.query(f"SELECT * FROM sessionact WHERE username = '{user}';")
  
  for x in range(db.shape[0]):
    st.markdown(f"Date: {db.loc[x]['time']}")
    st.markdown("Symptoms experienced:")
    symptom_list = list(severityDictionary.keys())
    symptom_name = []
    index=0
    for i in db.loc[x]['symptoms']:
        if i == 1:
            symptom_name.append(symptom_list[index])
        index++
    for i in range(symptom_name):
        st.write(f"{i+1}/ {symptom_name[i]}")
    st.markdown(f"Prediction: ")
    prediction = db.loc[x]['prediction'].split('/')
    if prediction[0] = prediction[1]:
      st.write(f"{prediction[0]}")
    else:
      st.write(f"{prediction[0]} or {prediction[1]}")
    st.markdown()
          
