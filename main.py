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
warnings.filterwarnings("ignore", category=DeprecationWarning)

st.header("----------HealthCare ChatBot----------")

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

    st.write("Training model...")
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
    return model, clf, cols, x, reduced_data

model, clf, cols, x, reduced_data= create_model()
importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
features = cols

severityDictionary=dict()
description_list = dict()
precautionDictionary=dict()

symptoms_dict = {}


for index, symptom in enumerate(x):
       symptoms_dict[symptom] = index

def calc_condition(exp,days):
    sum=0
    for item in exp:
         sum=sum+severityDictionary[item]
    if((sum*days)/(len(exp)+1)>13):
        st.markdown("You should take the consultation from doctor. ")
    else:
        st.markdown("It might not be that bad but you should take precautions.")

@st.cache_data
def getDescription():
    global description_list
    with open('./MasterData/symptom_Description.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _description={row[0]:row[1]}
            description_list.update(_description)

@st.cache_data
def getSeverityDict():
    global severityDictionary
    with open('./MasterData/Symptom_severity.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        try:
            for row in csv_reader:
                _diction={row[0]:int(row[1])}
                severityDictionary.update(_diction)
        except:
            pass

@st.cache_data
def getprecautionDict():
    global precautionDictionary
    with open('./MasterData/symptom_precaution.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _prec={row[0]:[row[1],row[2],row[3],row[4]]}
            precautionDictionary.update(_prec)


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
    df = pd.read_csv('/content/healthcare-chatbot/Data/Training.csv')
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

def print_disease(node):
    node = node[0]
    val  = node.nonzero()
    disease = le.inverse_transform(val[0])
    return list(map(lambda x:x.strip(),list(disease)))

def tree_to_code(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

    chk_dis=",".join(feature_names).split(",")
    while True:
        if "initial_disease" not in st.session_state:
            st.session_state.initial_disease = "None"
        if st.session_state.initial_disease := st.text_input("Enter the symptom you are experiencing", key = "initial"): # get initial symptom
            disease_input = str(st.session_state.initial_disease)
            conf,cnf_dis=check_pattern(chk_dis,disease_input)
            if conf==1:
                poss_list = []
                for num,it in enumerate(cnf_dis):
                    poss_list.append(it)
                if num!=0:
                    if st.radio("I found some similar result, is there anything you have?", key="reselect_disease", options=poss_list):
                        st.session_state.initial_disease = st.session_state.reselect_disease)
                        break
                else:
                    st.session_state.initial_disease = poss_list[0]
                break
            else:
                print("Enter valid symptom.")
                st.session_state.initial_disease = "None"

    while True:
        if "num_days" not in st.session_state:
            st.session_state.num_days = "None"
        if st.session_state.num_days :=st.number_input('Okay, for how many days has it been?', value=None):
            break
    if "symptoms_exp" not in st.session_state:
        st.session_state.symptoms_exp = []
        st.session_state.symptoms_given = []
        st.session_state.present_disease = []
        st.session_state.second_prediction = []
    def recurse(node, depth):
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            if name == st.session_state.initial_disease:
                val = 1
            else:
                val = 0
            if  val <= threshold:
                recurse(tree_.children_left[node], depth + 1)
            else:
                recurse(tree_.children_right[node], depth + 1)
        else:
            st.session_state.present_disease = print_disease(tree_.value[node])
            red_cols = reduced_data.columns
            st.session_state.symptoms_given = red_cols[reduced_data.loc[present_disease].values[0].nonzero()]
            for syms in st.session_state.symptoms_given:
                question = "Are you experiencing any " + str(syms) + " ?"
                while True:
                    if ans:=st.text_input(question, key=syms):
                        if ans == "yes":
                            st.session_state.symptoms_exp.append(syms)
                        elif ans == "no":
                            break
                            
            st.session_state.second_prediction = sec_predict(st.session_state.symptoms_exp)

            calc_condition(st.session_state.symptoms_exp,st.session_state.num_days)
            if(st.session_state.present_disease[0] ==st.session_state.second_prediction[0]):
                st.markdown("You may have " + st.session_state.present_disease [0])
                st.markdown(description_list[st.session_state.present_disease[0]])

            else:
                print("You may have " + st.session_state.present_disease[0]+ " or " + st.session_state.second_prediction[0])
                print(description_list[st.session_state.present_disease[0]])
                print(description_list[st.session_state.second_prediction[0]])

            precution_list=precautionDictionary[st.session_state.present_disease[0]]
            print("Take following measures : ")
            for  i,j in enumerate(precution_list):
                st.markdown(str(i+1) + ") " + j)
    
    recurse(0, 1)


getSeverityDict()
getDescription()
getprecautionDict()
            
tree_to_code(clf,cols)
