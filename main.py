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
if "messages" not in st.session_state: # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Tell me about your problems"}
    ]
if "user_input" not in st.session_state:
    st.session_state.user_input = "None"
if "new_mess" not in st.session_state:
    st.session_state.new_mess = 0
if "stage" not in st.session_state:
    st.session_state.stage = 0
    
def get_response():
    st.session_state.user_input = prompt
    st.session_state.new_mess = 1

if prompt := st.chat_input(placeholder = "Your question", on_submit = get_response):
    st.session_state.messages.append({"role": "user", "content": prompt})

def write_response(out):
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            st.write(out)
            message = {"role": "assistant", "content": out}
            st.session_state.messages.append(message)

def reset_response():
    st.session_state.user_input = "None"
    st.session_state.new_mess = 0

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

importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
features = cols

def readn(nstr):
    engine = pyttsx3.init()

    engine.setProperty('voice', "english+f5")
    engine.setProperty('rate', 130)

    engine.say(nstr)
    engine.runAndWait()
    engine.stop()


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
        write_response("You should take the consultation from doctor. ")
    else:
        write_response("It might not be that bad but you should take precautions.")

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

@st.cache_data
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
@st.cache_data
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
    symptoms_present = []

    while st.session_state.stage == 0:
        write_response("Enter the symptom you are experiencing")
        while st.session_state.new_mess == 0:
            counter=0
        disease_input = st.session_state.user_input
        reset_response()
        conf,cnf_dis=check_pattern(chk_dis,disease_input)
        if conf==1:
            write_response("searches related to input: ")
            message = ''
            for num,it in enumerate(cnf_dis):
                message = message + num + ")" + it
            write_response(message)
            if num!=0:
                message = "Select the one you meant (0 - " + num +"): "
                write_response(message)
                conf_inp = int(st.session_state.user_input)
                reset_response()
            else:
                conf_inp=0
            disease_input=cnf_dis[conf_inp]
            break
            # print("Did you mean: ",cnf_dis,"?(yes/no) :",end="")
            # conf_inp = input("")
            # if(conf_inp=="yes"):
            #     break
        else:
            write_response("Enter valid symptom.")

    while True:
        try:
            write_response("Okay. From how many days? :")
            while new_mess ==0:
                counter =0
            num_days=int(user_input)
            reset_response()
        except:
            write_response("Enter valid input.")
    def recurse(node, depth):
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]

            if name == disease_input:
                val = 1
            else:
                val = 0
            if  val <= threshold:
                recurse(tree_.children_left[node], depth + 1)
            else:
                symptoms_present.append(name)
                recurse(tree_.children_right[node], depth + 1)
        else:
            present_disease = print_disease(tree_.value[node])
            # print( "You may have " +  present_disease )
            red_cols = reduced_data.columns
            symptoms_given = red_cols[reduced_data.loc[present_disease].values[0].nonzero()]
            # dis_list=list(symptoms_present)
            # if len(dis_list)!=0:
            #     print("symptoms present  " + str(list(symptoms_present)))
            # print("symptoms given "  +  str(list(symptoms_given)) )
            write_response("Are you experiencing any ")
            symptoms_exp=[]
            for syms in list(symptoms_given):
                inp=""
                output = {syms + "? : "}
                write_response(output)
                while True:
                    while new_mess==0:
                        counter=0
                    inp = user_input
                    reset_response()
                    if(inp=="yes" or inp=="no"):
                        break
                    else:
                        write_response("Provide proper answers i.e. (yes/no) : ")
                if(inp=="yes"):
                    symptoms_exp.append(syms)

            second_prediction=sec_predict(symptoms_exp)
            # print(second_prediction)
            calc_condition(symptoms_exp,num_days)
            if(present_disease[0]==second_prediction[0]):
                output = {"You may have " + present_disease[0]}
                write_response(output)
                write_response(description_list[present_disease[0]])

                # readn(f"You may have {present_disease[0]}")
                # readn(f"{description_list[present_disease[0]]}")

            else:
                write_response("You may have ", present_disease[0], "or ", second_prediction[0])
                write_response(description_list[present_disease[0]])
                write_response(description_list[second_prediction[0]])

            # print(description_list[present_disease[0]])
            precution_list=precautionDictionary[present_disease[0]]
            write_response("Take following measures : ")
            for  i,j in enumerate(precution_list):
                write_response(i+1,")",j)

            # confidence_level = (1.0*len(symptoms_present))/len(symptoms_given)
            # print("confidence level is " + str(confidence_level))

    recurse(0, 1)

getSeverityDict()
getDescription()
getprecautionDict()

    

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        st.spinner("Thinking...") # Add response to message history
            
tree_to_code(clf,cols)
