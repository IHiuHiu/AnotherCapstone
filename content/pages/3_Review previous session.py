import re
import pandas as pd
import pyttsx3
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier,_tree
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
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
