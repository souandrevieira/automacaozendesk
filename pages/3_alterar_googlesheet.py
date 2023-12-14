import streamlit as st
# Documentação - https://github.com/streamlit/gsheets-connection
from streamlit_gsheets import GSheetsConnection
# pip install streamlit-extras
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import csv
import json
import requests
from datetime import datetime
import zendesklib as zl

st.set_page_config(page_title="Busca Campos", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style,
            unsafe_allow_html=True)  # Remove as mancações do Streamlit e o menu


url = "https://docs.google.com/spreadsheets/d/1JDy9md2VZPz4JbYtRPJLs81_3jUK47nx6GYQjgU8qNY/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

data = conn.read(spreadsheet=url, usecols=[0, 1], worksheet=1585633377)
st.dataframe(data)
