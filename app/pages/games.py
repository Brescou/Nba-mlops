import streamlit as st

from db.DB import DB

st.title("NBA Games")

db_instance = DB()
db_instance.connect()



with st.container():
    pass