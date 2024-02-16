import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import numpy as np
import re
import datetime
import psycopg2
from sqlalchemy import create_engine
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

if 'current_user' not in st.session_state:
    st.session_state['current_user'] = 0 #or whatever default
current_user = st.session_state['current_user']

conn = st.connection("postgresql", type="sql")
# Perform query.
#conn.query('\x on;')

# Print results.
def insert_user(username, email, password):
    with st.spinner("Please wait for DB connection..."):
        if st.session_state["create_user"]!=0:
            date_joined = datetime.datetime.now()
            date = str(date_joined.year) + '-0' + str(date_joined.month) + '-' + str(date_joined.day)
            conn2 = psycopg2.connect(
                host = "34.87.103.138",
                database = "New_Database",
                user = "streamlit",
                password = "123789",
                port = 5432)
            database_url = f'postgresql+psycopg2://streamlit:123789@34.87.103.138/New_Database'
            engine = create_engine(database_url)
            cursor = conn2.cursor()
            cursor.execute(f"INSERT INTO userinfo (username, email, password, datejoin) VALUES ('{username}','{email}','{password}','{date}') RETURNING *;")
            st.session_state["create_user"]=0
            conn2.commit()
            cursor.close()
            conn2.close()
    st.success('Account created successfully!! Please refresh the page to sign in!')


def get_user_emails():
    """
    Fetch User Emails
    :return List of user emails:
    """
    db = conn.query('SELECT * FROM userinfo;', ttl="10m")
    emails_check = []
    for user in range(db.shape[0]):
        emails_check.append(db.loc[user]['email'])
    return emails_check


def get_usernames():
    """
    Fetch Usernames
    :return List of user usernames:
    """
    db = conn.query('SELECT * FROM userinfo;', ttl="10m")
    usernames_check = []
    for user in range(db.shape[0]):
        usernames_check.append(db.loc[user]['username'])
    return usernames_check

def validate_email(email):
    """
    Check Email Validity
    :param email:
    :return True if email is valid else False:
    """
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$" #tesQQ12@gmail.com

    if re.match(pattern, email):
        return True
    return False


def validate_username(username):
    """
    Checks Validity of userName
    :param username:
    :return True if username is valid else False:
    """

    pattern = "^[a-zA-Z0-9]*$"
    if re.match(pattern, username):
        return True
    return False


def sign_up():
    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':green[Sign Up]')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password')
        password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password')

        if email:
            if validate_email(email):
                if email not in get_user_emails():
                    if validate_username(username):
                        if username not in get_usernames():
                            if len(username) >= 2:
                                if len(password1) >= 6:
                                    if password1 == password2:
                                        # Add User to DB
                                        if "create_user" not in st.session_state:
                                            st.session_state["create_user"]=1
                                        insert_user(username, email, password1)
                                    else:
                                        st.warning('Passwords Do Not Match')
                                else:
                                    st.warning('Password is too Short')
                            else:
                                st.warning('Username Too short')
                        else:
                            st.warning('Username Already Exists')

                    else:
                        st.warning('Invalid Username')
                else:
                    st.warning('Email Already exists!!')
            else:
                st.warning('Invalid Email')

        btn1, bt2, btn3, btn4, btn5 = st.columns(5)

        with btn3:
            st.form_submit_button('Sign Up')

#try:
db = conn.query('SELECT * FROM userinfo;', ttl="10m")
emails = []
usernames = []
passwords = []

for user in range(db.shape[0]):
    emails.append(db.loc[user]['email'])
    usernames.append(db.loc[user]['username'])
    passwords.append(db.loc[user]['password'])

credentials = {'usernames': {}}
for index in range(len(emails)):
    credentials['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}

Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', key='abcdef', cookie_expiry_days=4)

email, authentication_status, username = Authenticator.login() #':green[Login]', 'main'

info, info1 = st.columns(2)

if not authentication_status:
    sign_up()

if username:
    if username in usernames:
        if authentication_status:
            # let User see app
            st.sidebar.subheader(f'Welcome {username}')
            Authenticator.logout('Log Out', 'sidebar')

            st.subheader(f'Welcome, {username}')
            st.markdown(
                """
                ---
                Created with ❤️ by SnakeByte
                
                """
            )
            st.session_state['current_user'] = username
            c_user = username

        elif not authentication_status:
            with info:
                st.error('Incorrect Password or username')
        else:
            with info:
                st.warning('Please feed in your credentials')
    else:
        with info:
            st.warning('Username does not exist, Please Sign up')


#except:
#    st.success('Refresh Page')
