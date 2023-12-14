import streamlit as st
# pip install streamlit-extras
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import csv
import json
import requests
from datetime import datetime
import zendesklib as zl


st.set_page_config(page_title="Meu site 1", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;} 
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style,
            unsafe_allow_html=True)  # Remove as mancações do Streamlit e o menu


css_upload = '''
<style>
[data-testid="stFileUploadDropzone"] div div::before {content:"Clique para selecionar o arquivo ou arraste e solte aqui"}
[data-testid="stFileUploadDropzone"] div div span{display:none;}
[data-testid="stFileUploadDropzone"] div div::after {color:red; font-size: .8em; content:"Tamanho maximo de 200MB"}
[data-testid="stFileUploadDropzone"] div div small{display:none;}
</style>
'''

st.markdown(css_upload, unsafe_allow_html=True)

# st.sidebar.success('Sidebar ok')  # cria a barra lateral

st.title('Ferramentas de Automação para Zendesk')
st.header('Selecione uma das funções no Menu lateral e siga as instruções')
# st.title("Importar CSV")
# # st.subheader("segundo texto para um subtitulo")
# # st.write("Testando um link [Link para o Google](http://www.google.com)")

# # instancia = st.text_input('Instancia')
# # login = st.text_input('Login')
# # senha = st.text_input('senha')

# # st.session_state['instancia'] = instancia

# uploaded_file = st.file_uploader(label='Faça o upload do arquivo2', type='csv')
# if uploaded_file is not None:
#     dataframe = pd.read_csv(uploaded_file)
#     st.write(dataframe)
