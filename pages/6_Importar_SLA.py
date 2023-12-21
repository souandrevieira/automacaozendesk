import streamlit as st
# pip install streamlit-extras
from streamlit_option_menu import option_menu
# from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import csv
import json
import requests
from datetime import datetime
import zendesklib as zl
from streamlit_gsheets import GSheetsConnection


st.set_page_config(page_title="Importar SLA", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style,
            unsafe_allow_html=True)  # Remove as mancações do Streamlit e o menu

#### Funções###

# Função para aplicar a lógica de mapeamento


def mapear_tipo(row):  # Traduz os tipos de campos de ticket para uma versão user friendly
    if row['type'] == 'tagger':
        return 'Lista Suspensa'
    elif row['type'] == 'text':
        return 'Texto'
    elif row['type'] == 'textarea':
        return 'Texto Multilinha'
    elif row['type'] == 'checkbox':
        return 'Caixa de Seleção'
    elif row['type'] == 'date':
        return 'Data'
    elif row['type'] == 'integer':
        return 'Numero Inteiro'
    elif row['type'] == 'decimal':
        return 'Numero decimal'
    elif row['type'] == 'regexp':
        return 'Expressão Regular'
    elif row['type'] == 'partialcreditcard':
        return 'Cartão de Credito'
    elif row['type'] == 'multiselect':
        return 'Multi Seleção'
    elif row['type'] == 'lookup':
        return 'Campo de Relacionamento'
    elif row['type'] == 'tickettype':
        return 'Tipo de Ticket'
    else:
        return ''


def extract_names(options):
    if isinstance(options, list) and len(options) > 0:
        return ', '.join(option['name'] for option in options)
    return None


def extract_value(options):
    if isinstance(options, list) and len(options) > 0:
        return ', '.join(option['value'] for option in options)
    return None


def importa_google_sheet(url):
    conn = st.connection("gsheets", type=GSheetsConnection)

    df_gsheet = conn.read(spreadsheet=url, ttl=0)
    df_gsheet['linha'] = df_gsheet.index+2

    return df_gsheet

def create_json(row,filtro):
    if filtro == 'all':
        return {'field': row['value'], 'operator': row['operador_all'], 'value': row['value_all']}
    elif filtro == 'any':
        return {'field': row['value'], 'operator': row['operador_any'], 'value': row['value_any']}
    elif filtro == 'metric':
        return {
                'priority': row['priority_value'],
                'metric': row['metrics_value'],
                'target': row['metrics_target'],
                'business_hours': row['metrics_business_hours']
                }


############### Declaração de Variaveis padrão ################
check_campos = False
check_operadores = False
check_valores = False


menu = option_menu(None, ["Autenticação", "Planilha de SLA",
                   "Importação"], default_index=0, orientation="horizontal")

if menu == 'Autenticação':
    if 'login' not in st.session_state:
        st.session_state.login = "ps@aktienow.com"

    if 'instancia' not in st.session_state:
        st.session_state.instancia = "https://con-aktienow.zendesk.com"

    if 'senha' not in st.session_state:
        st.session_state.senha = "#ps@2020"

    st.session_state['instancia'] = st.text_input(
        'Instancia', value=st.session_state['instancia'] if 'instancia' in st.session_state else '')
    st.session_state['login'] = st.text_input(
        'Login', value=st.session_state['login'] if 'login' in st.session_state else '', help='Para conectar usando o Token, não esqueca de adicionar **/token** depois do e-mail')
    st.session_state['senha'] = st.text_input('senha', type="password", help="Insira a senha ou token de acesso",
                                              label_visibility='visible', value=st.session_state['senha'] if 'senha' in st.session_state else '')
    if st.button('Testar dados de Autenticação'):
        if 'instancia' in st.session_state:
            end_point = st.session_state['instancia'] + \
                '/api/v2/account/settings'
            response = requests.get(
                end_point, auth=(st.session_state['login'], st.session_state['senha']))
            if response.status_code == 200:
                # st.write(response.json())
                st.success('Autenticação Validada',)
            else:
                erro_autenticacao = dict(response.json())
                st.error(
                    'Autenticação falhou, verifique os dados de instancia, login e senha'+'\n\n'+'Erro '+str(response.status_code)+': ' + str(erro_autenticacao['error']))
        else:
            st.error('Instancia não informada')

if menu == 'Planilha de SLA':

    container_importa_planilha = st.container()
    container_validacoes = st.container()

    with container_importa_planilha:

        url = st.text_input(
            'Url da planilha', value=st.session_state['url'] if 'url' in st.session_state else '')
        st.session_state['url'] = url

        if st.button('Verificar', key='check'):

            # puxando dados da planilha
            df_sla_gsheet = importa_google_sheet(url)
            df_sla_gsheet['position'].ffill(inplace=True)
            df_sla_gsheet['title'].ffill(inplace=True)

            # Separa os Filtro ALL
            df_filter_all = df_sla_gsheet[[
                'linha', 'title', 'filter_all_field', 'filter_all_operator', 'filter_all_value']]
            df_filter_all.dropna(subset=['filter_all_field'], inplace=True)
            # st.write(df_filter_all)

            # Separa os Filtro ANY
            df_filter_any = df_sla_gsheet[[
                'linha', 'title', 'filter_any_field', 'filter_any_operator', 'filter_any_value']]
            df_filter_any.dropna(subset=['filter_any_field'], inplace=True)
            # st.write(df_filter_any)

            # Separa mas metricas
            df_metrics = df_sla_gsheet[[
                'linha', 'title', 'metrics', 'metrics_priority', 'metrics_target', 'metrics_business_hours']]
            df_metrics.dropna(subset=['metrics'], inplace=True)
            # st.write(df_metrics)

            st.dataframe(df_sla_gsheet, use_container_width=True, hide_index=True, column_order=['linha', 'title', 'position', 'filter_all_field', 'filter_all_operator',
                         'filter_all_value', 'filter_any_field', 'filter_any_operator', 'filter_any_value', 'metrics', 'metrics_priority', 'metrics_target', 'metrics_business_hours'])
            st.session_state['df_sla_gsheet'] = df_sla_gsheet

    with container_validacoes:
        if 'df_sla_gsheet' in st.session_state:
            # Começa a validação dos dados importados

            # Bucando campos com filtros.
            st.subheader('Validando campos')
            sla_filter_zd = zl.busca_sla_filters(
                st.session_state['instancia'], st.session_state['login'], st.session_state['senha'])
            df_sla_filter_zd = pd.DataFrame(sla_filter_zd)

            # Tratando operadores
            df_sla_filter_zd['operadores'] = ''

            for index, linha in df_sla_filter_zd.iterrows():
                lt_operadores = list()
                for operador in linha['operators']:
                    lt_operadores.append(operador['title'])
                df_sla_filter_zd['operadores'][index] = lt_operadores


            # tratando opções de lista
            df_sla_filter_zd['valores'] = ''

            for index, linha in df_sla_filter_zd.iterrows():
                lt_values = list()
                if linha['values']['type'] == 'list':
                    for opcao in linha['values']['list']:
                        lt_values.append(opcao['title'])
                        # st.write('opção')
                df_sla_filter_zd['valores'][index] = lt_values
            # st.write(df_sla_filter_zd)

            # separando campos que que estão errados
            df_campos_errados_all = df_filter_all[~(
                df_filter_all['filter_all_field'].str.lower().isin(df_sla_filter_zd['title'].str.lower()))]
            df_campos_errados_all['campo'] = df_campos_errados_all['filter_all_field']

            df_campos_errados_any = df_filter_any[~(
                df_filter_any['filter_any_field'].str.lower().isin(df_sla_filter_zd['title'].str.lower()))]
            df_campos_errados_any['campo'] = df_campos_errados_any['filter_any_field']

            df_campos_errados = pd.concat(
                [df_campos_errados_all, df_campos_errados_any])

            if not df_campos_errados.empty:

                st.error(
                    'Os seguintes campos não existem na instancia ou não podem ser usados como filtro. Por favor verifique e insira uma opção valida.')
                st.dataframe(df_campos_errados, use_container_width=False, hide_index=True, column_order=['linha', 'title', 'campo'], column_config={
                    "linha": st.column_config.Column("Linha", help="A linha desse registro no Google Sheet", width='small'),
                    "title": st.column_config.Column("Titulo", help="**Titulo** da SLA"),
                    "campo": st.column_config.Column("Campo")})
                check_campos = False
            else:
                check_campos = True
                st.success('Campos validados')

            # Validando operadores
            st.subheader('Validando operadores')

            # Validando as opção de filtros ALL
            operadores_errados_all = []
            for indexf, linhaf in df_filter_all.iterrows():

                for indexs, linhas in df_sla_filter_zd.iterrows():
                    if linhaf['filter_all_field'].lower() == linhas['title'].lower():
                        if linhaf['filter_all_operator'] not in linhas['operadores']:
                            linhaf['operadores'] = linhas['operadores']
                            operadores_errados_all.append(linhaf)

            df_operadores_errados_all = pd.DataFrame(operadores_errados_all)
            if not df_operadores_errados_all.empty:
                df_operadores_errados_all['campo'] = df_operadores_errados_all['filter_all_field']
                df_operadores_errados_all['operador'] = df_operadores_errados_all['filter_all_operator']

            # Validando as opção de filtros ANY
            operadores_errados_any = []
            for indexf, linhaf in df_filter_any.iterrows():
                # st.write(f'indexf - {indexf}')
                # st.write(linhaf)
                for indexs, linhas in df_sla_filter_zd.iterrows():
                    if linhaf['filter_any_field'].lower() == linhas['title'].lower():
                        if linhaf['filter_any_operator'] not in linhas['operadores']:
                            linhaf['operadores'] = linhas['operadores']
                            operadores_errados_any.append(linhaf)

            df_operadores_errados_any = pd.DataFrame(operadores_errados_any)
            if not df_operadores_errados_any.empty:
                df_operadores_errados_any['campo'] = df_operadores_errados_any['filter_any_field']
                df_operadores_errados_any['operador'] = df_operadores_errados_any['filter_any_operator']

            df_operadores_errados = pd.concat(
                [df_operadores_errados_all, df_operadores_errados_any])

            if not df_operadores_errados.empty:

                st.error(
                    'Os seguintes operadores não são compativeis com os seus respectivos campos. Por favor verifique e insira uma opção valida.')
                st.dataframe(df_operadores_errados, use_container_width=False, hide_index=True, column_order=['linha', 'title', 'campo', 'operador', 'operadores'], column_config={
                    "linha": st.column_config.Column("Linha", help="A linha desse registro no Google Sheet", width='small'),
                    "title": st.column_config.Column("Titulo", help="**Titulo** da SLA"),
                    "campo": st.column_config.Column("Campo"),
                    "operador": st.column_config.Column("Operador"),
                    "operadores": st.column_config.Column("Operadores validos para esse filtro")})
                check_operadores = False
            else:
                check_operadores = True
                st.success('Operadores validados')

            # Validar opções de lista suspensa.
            st.subheader('Validando valores dos filtros')

            valores_errados_all = []
            valores_errados_any = []

            for indexf, linhaf in df_filter_all.iterrows():
                # st.write(f'indexf - {indexf}')
                # st.write(linhaf)
                for indexs, linhas in df_sla_filter_zd.iterrows():
                    if linhaf['filter_all_field'].lower() == linhas['title'].lower():
                        if str(linhaf['filter_all_value']).lower() not in map(str.lower, linhas['valores']):
                            linhaf['valores'] = linhas['valores']
                            valores_errados_all.append(linhaf)
            # st.write(valores_errados_all)
            df_valores_errados_all = pd.DataFrame(valores_errados_all)
            if not df_valores_errados_all.empty:
                df_valores_errados_all['campo'] = df_valores_errados_all['filter_all_field']
                df_valores_errados_all['valor'] = df_valores_errados_all['filter_all_value']

            # st.write(df_valores_errados_all)

            for indexf, linhaf in df_filter_any.iterrows():
                # st.write(f'indexf - {indexf}')
                # st.write(linhaf)
                for indexs, linhas in df_sla_filter_zd.iterrows():
                    if linhaf['filter_any_field'].lower() == linhas['title'].lower():
                        if str(linhaf['filter_any_value']).lower() not in map(str.lower, linhas['valores']):
                            linhaf['valores'] = linhas['valores']
                            valores_errados_any.append(linhaf)
            # st.write(valores_errados_any)
            df_valores_errados_any = pd.DataFrame(valores_errados_any)
            if not df_valores_errados_any.empty:
                df_valores_errados_any['campo'] = df_valores_errados_any['filter_any_field']
                df_valores_errados_any['valor'] = df_valores_errados_any['filter_any_value']

            # st.write(df_valores_errados_any)

            df_valores_errados = pd.concat(
                [df_valores_errados_all, df_valores_errados_any])

            if not df_valores_errados.empty:

                st.error(
                    'Os seguintes valores não são valores validos de seus respectivos campos. Por favor, insira uma opção valida. Você pode verificar a tabela completa de campos, operadores e valores disponiveis [AQUI](#valores-validos)')
                st.dataframe(df_valores_errados, use_container_width=True, hide_index=True, column_order=['linha', 'title', 'campo', 'valor', 'valores'], column_config={
                    "linha": st.column_config.Column("Linha", help="A linha desse registro no Google Sheet", width='small'),
                    "title": st.column_config.Column("Titulo", help="**Titulo** da SLA"),
                    "campo": st.column_config.Column("Campo"),
                    "valor": st.column_config.Column("Valor"),
                    "valores": st.column_config.Column("Valores validos", help="Valores validos. Selecione um desses")
                })
                check_valores = False
            else:
                check_valores = True
                st.success('valores dos filtros validados')
            

            if check_campos == False or check_operadores == False or check_valores == False:
                # st.write("check out this [link](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")
                st.subheader('Valores validos')
                st.dataframe(df_sla_filter_zd, use_container_width=True, hide_index=True, column_order=['title','title_for_field','operadores','valores'], column_config={
                    "title"             : st.column_config.Column("Campo"),
                    "title_for_field"   : st.column_config.Column("Titulo do campo no filtro"),
                    "operadores"        : st.column_config.Column("Operadores Validos"),
                    "valores"           : st.column_config.Column("Valores validos", help="Valores validos. Selecione um desses")
                })

######## Montagem do Json para importação #######
    if check_campos == True and check_operadores == True and check_valores == True:
        
        #Tratando filtros ALL
        
                
        df_filter_all['filter_all_field_lower'] = df_filter_all['filter_all_field'].str.lower()
        df_sla_filter_zd['title_lower'] = df_sla_filter_zd['title'].str.lower()
        
        df_filter_all_merged = pd.merge(df_filter_all, df_sla_filter_zd, left_on='filter_all_field_lower', right_on='title_lower', how='inner')
        
        df_filter_all_merged['operador_all'] = '' #vai receber o operador do filtro ALL
        df_filter_all_merged['value_all'] = '' #vai receber o valor do filtro All
        
        for index, linha in enumerate(df_filter_all_merged['operators']): #pegar o value do operador do filtro
            for op in linha:
                if op['title'] == df_filter_all_merged.loc[index,'filter_all_operator']:
                    df_filter_all_merged['operador_all'][index] = op['value']

        
        for index, linha in enumerate(df_filter_all_merged['values']):
            for op in linha['list']:
                if op["title"] == df_filter_all_merged.loc[index,'filter_all_value']:
                    df_filter_all_merged['value_all'][index] = op['value']
       
        df_filter_all_merged['json_filter_all'] = df_filter_all_merged.apply(create_json, axis=1,filtro='all')

        #Tratando filtros ANY

        df_filter_any['filter_any_field_lower'] = df_filter_any['filter_any_field'].str.lower()
        df_filter_any_merged = pd.merge(df_filter_any, df_sla_filter_zd, left_on='filter_any_field_lower', right_on='title_lower', how='inner')

        df_filter_any_merged['operador_any'] = '' #vai receber o operador do filtro ALL
        df_filter_any_merged['value_any'] = '' #vai receber o valor do filtro All

        # pegar o value do operador do filtro
        for index, linha in enumerate(df_filter_any_merged['operators']):
            for op in linha:
                if op['title'] == df_filter_any_merged.loc[index, 'filter_any_operator']:
                    df_filter_any_merged['operador_any'][index] = op['value']

        for index, linha in enumerate(df_filter_any_merged['values']):
            for op in linha['list']:
                if op["title"].lower() == df_filter_any_merged.loc[index,'filter_any_value'].lower():
                    df_filter_any_merged['value_any'][index] = op['value']

        df_filter_any_merged['json_filter_any'] = df_filter_any_merged.apply(create_json, axis=1, filtro='any')


        # st.dataframe(df_filter_any_merged)

        ####################### tratando matrics ######################

        df_metrics['metrics_value'] = ''
        df_metrics['priority_value'] = ''
        
        for index, linha in df_metrics.iterrows():
            if linha['metrics'] == 'Tempo da primeira resposta':
                df_metrics['metrics_value'][index] = 'first_reply_time'
            
            elif linha['metrics'] == 'Tempo de espera do solicitante':
                df_metrics['metrics_value'][index] = 'requester_wait_time'
            
            elif linha['metrics'] == 'Tempo de trabalho do agente':
                df_metrics['metrics_value'][index] = 'agent_work_time'

            elif linha['metrics'] == 'Tempo da próxima resposta':
                df_metrics['metrics_value'][index] = 'next_reply_time'

            elif linha['metrics'] == 'Atualização periódica':
                df_metrics['metrics_value'][index] = 'periodic_update_time'
            
            elif linha['metrics'] == 'Atualização com pausa':
                df_metrics['metrics_value'][index] = 'pausable_update_time'
            
            elif linha['metrics'] == 'Atualização com pausa':
                df_metrics['metrics_value'][index] = 'pausable_update_time'
           
            elif linha['metrics'] == 'Tempo total de resolução':
                df_metrics['metrics_value'][index] = 'total_resolution_time'
            
            if linha['metrics_priority'] == 'Urgente':
                df_metrics['priority_value'][index] = 'urgent'

            elif linha['metrics_priority'] == 'Alta':
                df_metrics['priority_value'][index] = 'high'

            elif linha['metrics_priority'] == 'Normal':
                df_metrics['priority_value'][index] = 'normal'
            
            elif linha['metrics_priority'] == 'Baixa':
                df_metrics['priority_value'][index] = 'low'

            # st.write(linha)
        df_metrics['json_metrics'] = df_metrics.apply(create_json, axis=1, filtro='metric')

        ############# Montando o Json inteiro pra enviar.

        sla_names_unique = df_sla_gsheet['title'].unique() # separa as politicas de SLA em nomes unicos. 
        dic_full_sla = []
        
        for sla in sla_names_unique:
            sla_json = {"title": sla,
            }
            dic_full_sla.append(sla_json) #Criar uma chave unica no dicionario para cada politica

        for sla in dic_full_sla:
            list_metrics = []
            list_filter_all = []
            list_filter_any = []
            sla['position'] = 0
            sla['filter'] = {}
            sla['filter']['all'] = []
            sla['filter']['any'] = []
            for indexg,linha in df_sla_gsheet.iterrows():
                if linha['title'] == sla['title']:
                    sla['position'] = int(df_sla_gsheet['position'][indexg]) #para cada politica, adiciona a posição informada no google Sheet

            for index, linha in df_filter_all_merged.iterrows():
                if linha['title_x'] == sla['title']:
                    list_filter_all.append(linha['json_filter_all'])
            sla['filter']['all'] = list_filter_all    

            for index, linha in df_filter_any_merged.iterrows():
                if linha['title_x'] == sla['title']:
                    list_filter_any.append(linha['json_filter_any'])
            sla['filter']['any'] = list_filter_any

            for index,linha in df_metrics.iterrows():
                if linha['title'] == sla['title']:
                    list_metrics.append(linha['json_metrics'])
            sla['policy_metrics'] = list_metrics

        st.session_state['dic_full_sla'] = dic_full_sla


        





if menu == 'Importação':  # Fim do tratamento do Dicionario começo da importação para o Zendesk

    if 'dic_full_sla' not in st.session_state:
        st.header('Defina as condicionais nas etapas anteriores primeiro')
    else:
        st.write('Esse é o Json que será importado. Verifique antes de importar. Uma vez que clicar em importar **NÃO TEM MAIS VOLTA**.')
        st.write(st.session_state['dic_full_sla'])

        if st.button('Importar (Enviar para o Zendesk)', key='import', type='secondary'):
            # importar pro Zendesk via Request
            instancia_prod = st.session_state['instancia']
            login_prod = st.session_state['login']
            senha_prod = st.session_state['senha']
            full_data = st.session_state['dic_full_sla']
            objeto_type = 'sla_policy'
            url_endpoint = st.session_state['instancia'] + '/api/v2/slas/policies'

            # montando a requisição para api
            objeto_upload = {objeto_type: []}
            for objeto in full_data:

                objeto_upload[objeto_type] = objeto

                json_data = json.dumps(objeto_upload)

                # st.write(json_data)

                response = requests.post(url_endpoint, json_data, headers={
                                        "Content-Type": "application/json"}, auth=(login_prod, senha_prod))
                json_resultado = response.json()
                dic_json_resultado = dict(json_resultado[objeto_type])
                resposta_codigo = response.status_code
                if resposta_codigo == 201:
                    st.success(f"Sla {dic_json_resultado['title']} - Importação concluída com sucesso. Codigo:{dic_json_resultado['id']} \n asd")
                else:
                    st.error(f'Erro: {resposta_codigo} - {json_resultado}')
                # st.write(json_resultado)
