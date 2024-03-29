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
warnings.filterwarnings("ignore", category=DeprecationWarning)

st.set_page_config(page_title="Heathcare Chatbot", page_icon="🤖")
st.header("----------HealthCare ChatBot----------")

st.sidebar.header("Healthcare Chatbot")
st.sidebar.subheader(f'Welcome {st.session_state["current_user"]}')

#def clear_cache():
#    keys = list(st.session_state.keys())
#    for key in keys:
 #       st.session_state.pop(key)

#st.button("Reset", key="clear", on_click=clear_cache)
st.markdown(f'Hello {st.session_state["current_user"]}, tell me your problem')    

if "symptom_list" not in st.session_state:
    st.session_state.symptom_list = []

@st.cache_data
def create_model():
    training = pd.read_csv('./Data/Training.csv')
    testing= pd.read_csv('./Data/Testing.csv')
    cols= training.columns
    cols= cols[:-1]
    x = training[cols]
    y = training['prognosis']
    y1= y
        
    reduced_data = training.groupby(training['prognosis']).max()

    #mapping strings to numbers
    le = preprocessing.LabelEncoder()
    le.fit(y)
    y = le.transform(y)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
    testx    = testing[cols]
    testy    = testing['prognosis']
    testy    = le.transform(testy)

    clf1  = DecisionTreeClassifier()
    clf = clf1.fit(x_train,y_train)
    print(clf.score(x_train,y_train))
    print ("cross result========")
    scores = cross_val_score(clf, x_test, y_test, cv=3)
    print (scores)
    print (scores.mean())

    model=SVC()
    model.fit(x_train,y_train)
    print("for svm: ")
    print(model.score(x_test,y_test))
    return model, clf, cols, x, reduced_data, le

model, clf, cols, x, reduced_data, le= create_model()
importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
features = cols

symptoms_dict = {}
for index, symptom in enumerate(x):
       symptoms_dict[symptom] = index

def calc_condition(exp,day):
    sum=0
    for item in exp:
         sum=sum+severityDictionary[item]
    if((sum*day)/(len(exp)+1)>13):
        st.markdown("You should take the consultation from doctor. ")
    else:
        st.markdown("It might not be that bad but you should take precautions.")

@st.cache_data
def getDescription():
    description_list = dict()
    with open('./MasterData/symptom_Description.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _description={row[0]:row[1]}
            description_list.update(_description)
    return description_list

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

@st.cache_data
def getprecautionDict():
    precautionDictionary = dict()
    with open('./MasterData/symptom_precaution.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _prec={row[0]:[row[1],row[2],row[3],row[4]]}
            precautionDictionary.update(_prec)
    return precautionDictionary

def check_pattern(dis_list,inp):
    pred_list=[]
    inp=inp.replace(' ','_')
    patt = f"{inp}"
    regexp = re.compile(patt)
    pred_list=[item for item in dis_list if regexp.search(item)]
    if(len(pred_list)>0):
        return 1,pred_list
    else:
        return 0,[]

def sec_predict(symptoms_exp):
    df = pd.read_csv('./Data/Training.csv')
    X = df.iloc[:, :-1]
    y = df['prognosis']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=20)
    rf_clf = DecisionTreeClassifier()
    rf_clf.fit(X_train, y_train)

    symptoms_dict = {symptom: index for index, symptom in enumerate(X)}
    input_vector = np.zeros(len(symptoms_dict))
    for item in symptoms_exp:
      input_vector[[symptoms_dict[item]]] = 1
    return rf_clf.predict([input_vector])

def save_session_activity(name, sym, pred):
    symptom_list = list(severityDictionary.keys())
    se = []
    for i in symptom_list:
        if i in sym:
            se.append('1')
        else:
            se.append('0')
    symptom_code = ''.join(str(e) for e in se)
    if isinstance(pred, list):
        dis = '/'.join(e for e in pred)
    else: 
        dis = pred
    date_session = datetime.datetime.now()
    date = str(date_session.year) + '-0' + str(date_session.month) + '-' + str(date_session.day)
    conn2 = psycopg2.connect(
        host = "34.87.103.138",
        database = "New_Database",
        user = "streamlit",
        password = "123789",
        port = 5432)
    database_url = f'postgresql+psycopg2://streamlit:123789@34.87.103.138/New_Database'
    engine = create_engine(database_url)
    cursor = conn2.cursor()
    cursor.execute(f"INSERT INTO sessionact (username, symptoms, prediction, time) VALUES ('{name}','{symptom_code}','{dis}','{date}') RETURNING *;")
    st.session_state["create_user"]=0
    conn2.commit()
    cursor.close()
    conn2.close()

def print_disease(node):
    node = node[0]
    val  = node.nonzero()
    disease = le.inverse_transform(val[0])
    return list(map(lambda x:x.strip(),list(disease)))

severityDictionary = getSeverityDict()
description_list = getDescription()
precautionDictionary = getprecautionDict()

#def input_first_symptom():
#    st.session_state

def submit():
    st.session_state.symptoms_exp.append(st.session_state.symptoms_given[st.session_state.count])
    st.session_state.count= int(st.session_state.count)+1
def submit_no():
    st.session_state.count= int(st.session_state.count)+1
if "getInitialSymp" not in st.session_state:
    st.session_state.getInitialSymp = 0
def tree_to_code(tree, feature_names):
    if "tree" not in st.session_state:
        st.session_state.tree = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in st.session_state.tree.feature
    ]

    chk_dis=",".join(feature_names).split(",")
    if "initial_disease" not in st.session_state:
        st.session_state.initial_disease = "None"
    if prompt0 := st.text_input("Enter the symptom you are experiencing", key = "first"): # get initial symptom
        if not st.session_state.first:
            st.stop()
        else:
            disease_input = str(prompt0)
            conf,cnf_dis=check_pattern(chk_dis,disease_input)
            if conf==1:
                poss_list = []
                for num,it in enumerate(cnf_dis):
                    poss_list.append(it)
                if num!=0:
                    if prompt2 := st.radio("I found some similar result, is there anything you have?", key="reselect_disease", options=poss_list, index = None):
                        st.session_state.initial_disease = prompt2
                        st.session_state.getInitialSymp = 1
                else:
                    st.session_state.initial_disease = poss_list[0]
                    st.session_state.getInitialSymp = 1
            else:
                st.warning('Enter valid symptom.')
                st.session_state.initial_disease = "None"
        
    if "symptoms_exp" not in st.session_state:
        st.session_state.symptoms_exp = []
        st.session_state.symptoms_given = []
        st.session_state.present_disease = []
        st.session_state.second_prediction = []
        st.session_state.count = 0
    def recurse(node, depth):
        if st.session_state.tree.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = st.session_state.tree.threshold[node]
            if name == st.session_state.initial_disease:
                val = 1
            else:
                val = 0
            if  val <= threshold:
                recurse(st.session_state.tree.children_left[node], depth + 1)
            else:
                recurse(st.session_state.tree.children_right[node], depth + 1)
        else:
            present_disease = print_disease(st.session_state.tree.value[node])
            red_cols = reduced_data.columns
            st.session_state.present_disease = present_disease
            st.session_state.symptoms_given = red_cols[reduced_data.loc[present_disease].values[0].nonzero()]
            
            if st.session_state.count < len(st.session_state.symptoms_given):
                question = "Are you experiencing any " + st.session_state.symptoms_given[int(st.session_state.count)] + " ?"
                new_key = "symptom num "+ str(st.session_state.count)
                st.markdown(question)
                st.button("Yes", key = "yesButton", on_click=submit)
                st.button("No", key = "noButton", on_click=submit_no)
                    
            if st.session_state.count >= len(st.session_state.symptoms_given):
                st.markdown(
                """
                ---
                Here is my prediction, take it with a grain of salt please
                
                """
                )
                st.session_state.second_prediction = sec_predict(st.session_state.symptoms_exp)

                calc_condition(st.session_state.symptoms_exp,st.session_state.num_days)
                if(st.session_state.present_disease[0] ==st.session_state.second_prediction[0]):
                    st.markdown("You may have " + st.session_state.present_disease [0])
                    st.markdown(description_list[st.session_state.present_disease[0]])

                else:
                    st.markdown("You may have " + st.session_state.present_disease[0]+ " or " + st.session_state.second_prediction[0])
                    st.markdown(description_list[st.session_state.present_disease[0]])
                    st.markdown(description_list[st.session_state.second_prediction[0]])

                precution_list=precautionDictionary[st.session_state.present_disease[0]]
                st.markdown(
                """
                ---
                Take following measures : 
                """)
                for  i,j in enumerate(precution_list):
                    st.markdown(str(i+1) + ") " + j)
                st.button("Save result", key = "saveButton", on_click=save_session_activity, args=(st.session_state["current_user"], st.session_state.symptoms_exp, [st.session_state.present_disease [0], st.session_state.second_prediction[0]]))
    if st.session_state.getInitialSymp != 0:
        if "num_days" not in st.session_state:
            st.session_state.num_days = "None"
        if prompt1 := st.number_input('Okay, for how many days has it been?', value=None, key='days'):
            st.session_state.num_days = prompt1
        recurse(0, 1)
            
tree_to_code(clf,cols)
