import streamlit as st
# pip install streamlit-extras
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import csv
import json
import requests
from datetime import datetime
import zendesklib as zl

st.set_page_config(page_title="Busca Campos", layout="wide")

# st.title("Buscar campos pela API")
# st.subheader("segundo texto para um subtitulo")
# st.write("Testando um link [Link para o Google](http://www.google.com)")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style,
            unsafe_allow_html=True)  # Remove as mancações do Streamlit e o menu


if 'login' not in st.session_state:
    st.session_state.login = "ps@aktienow.com"

if 'instancia' not in st.session_state:
    st.session_state.instancia = "https://con-aktienow.zendesk.com"

if 'senha' not in st.session_state:
    st.session_state.senha = "#ps@2020"

st.session_state['instancia'] = st.text_input(
    'Instancia', value=st.session_state['instancia'] if 'instancia' in st.session_state else '')
st.session_state['login'] = st.text_input(
    'Login', value=st.session_state['login'] if 'login' in st.session_state else '')
st.session_state['senha'] = st.text_input('senha', type="password", help="Insira a senha",
                                          label_visibility='visible', value=st.session_state['senha'] if 'senha' in st.session_state else '')

if st.button('Buscar'):
    campos_zd = zl.busca_campos(
        st.session_state['instancia'], st.session_state['login'], st.session_state['senha'])
    df_campos_zd = pd.DataFrame(campos_zd)
    if 'campos_zd' in st.session_state:
        del st.session_state['campos_zd']
    st.session_state['campos_zd'] = df_campos_zd

tabela_campos = st.container()

with tabela_campos:
    if 'campos_zd' in st.session_state:
        st.data_editor(st.session_state['campos_zd'], column_order=(
            "id", "title", "title_in_portal", "type", 'required', "custom_field_options"), use_container_width=True, column_config={
            "title": st.column_config.Column("Titulo", help=" **Titulo** do campo"),
            "title_in_portal": st.column_config.Column("Titulo na HC")
        })
