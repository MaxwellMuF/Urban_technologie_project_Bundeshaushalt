import json
import streamlit as st



def load_json(path="DataBase_user_changes.json"):
    """Load json to python dict. Use encoding='utf-8' to handle german letters like 'ä' or 'ß' """
    with open(path, "r", encoding='utf-8') as file:
        dict_loaded = json.load(file)
    return dict_loaded


def calculator():
    st.subheader("Quick Calculator")
    c1, c2, c3, c4, c5 = st.columns([3,3,3,1,3])

    with c1:
        value_1 = st.text_input("First Number", placeholder="5")
    with c3:
        value_2 = st.text_input("Second Number", placeholder="10")
    with c2:
        operator = st.selectbox("Operator", options=["+", "-", "*", "/"], placeholder="+")
    with c4:
        st.text_input("is",value="=")
    with c5:
        try:
            if operator == "+":
                result = float(value_1)+float(value_2)
            elif operator == "-":
                result = float(value_1)-float(value_2)
            elif operator == "*":
                result = float(value_1)*float(value_2)
            elif operator == "/":
                result = float(value_1)/float(value_2)
            else:
                result = 15
        except:
            result = "15"
        st.text_input("Result",value=str(result), placeholder="15")