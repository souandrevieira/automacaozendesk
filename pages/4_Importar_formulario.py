import streamlit as st
# pip install streamlit-extras
from streamlit_option_menu import option_menu
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import csv
import json
import requests
from datetime import datetime
import zendesklib as zl
from streamlit_gsheets import GSheetsConnection


st.set_page_config(page_title="Importar Formulário", layout="wide")

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


def botao_clicado(var):
    st.session_state[var] = True

############### Fim das Funções ################


menu = option_menu(None, ["Autenticação", "Formulário", "Condicionais",
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
        end_point = st.session_state['instancia'] + '/api/v2/account/settings'
        response = requests.get(
            end_point, auth=(st.session_state['login'], st.session_state['senha']))
        if response.status_code == 200:
            # st.write(response.json())
            st.success('Autenticação Validada',)
        else:
            erro_autenticacao = dict(response.json())
            st.error(
                'Autenticação falhou, verifique os dados de instancia, login e senha'+'\n\n'+str(erro_autenticacao['error']))

if menu == 'Formulário':
    form_zd = zl.busca_formularios(
        st.session_state['instancia'], st.session_state['login'], st.session_state['senha'])
    df_form_zd = pd.DataFrame(form_zd)
    df_form_zd['id'] = df_form_zd['id'].astype(str)
    formulario_selecionado = st.selectbox(
        'Selecione o Formulário', df_form_zd['id'] + " - " + df_form_zd['name'], help='O formulário precisa ser criado previamente no Zendesk', placeholder='-')
    str_form_selecionado = formulario_selecionado.split(' - ')
    # st.write(str_form_selecionado[1])
    df_form_selecionado = df_form_zd[(
        df_form_zd['id'] == str_form_selecionado[0])].reset_index()

    # st.data_editor(df_form_selecionado)
    # st.dataframe(df_form_selecionado,
    #              column_order=('id','name','active', 'end_user_visible', 'in_all_brands'),
    #              column_config={
    #                  "id": st.column_config.Column("ID", help="ID do formulário no Zendesk", width='medium'),
    #                  "name": st.column_config.Column("Nome"),
    #                  "active": st.column_config.Column("Ativo", help="O formulario está ativo ou desativado?"),
    #                  "end_user_visible": st.column_config.Column("Visivel para o usuario final", help="Esse formulário aparece para o usuario final na HC?"),
    #                  "in_all_brands": st.column_config.Column("Visivel para todas as marcas", help="Esse formulário é visivel para todas as marcas?")
    #             }, use_container_width=True,hide_index=True)

    st.session_state['formulario'] = df_form_selecionado

# if menu == 'Campos':
    if 'formulario' in st.session_state:
        campos_zd = zl.busca_campos(
            st.session_state['instancia'], st.session_state['login'], st.session_state['senha'])
        df_campos_zd = pd.DataFrame(campos_zd)
        # st.write(st.session_state['formulario']['ticket_field_ids'])
        ids_campos_form = st.session_state['formulario']['ticket_field_ids'][0]
        ids_campos_form = pd.Series(ids_campos_form)
        df_campos_no_form = df_campos_zd[(
            df_campos_zd['id'].isin(ids_campos_form))]
        df_campos_no_form = df_campos_no_form[~(df_campos_no_form['type'].isin(
            ['status', 'subject', 'description', 'priority', 'group', 'assignee', 'custom_status']))]
        df_campos_no_form['id'] = df_campos_no_form['id'].astype(str)
        # df_campos_no_form[]

        # st.session_state['campos_zd'] = df_campos_zd
        st.session_state['df_campos_no_form'] = df_campos_no_form.reset_index()

        container_campos = st.container()

        with container_campos:
            st.write(
                f"O formulario: **{st.session_state['formulario']['name'][0]}** tem {len(ids_campos_form)-6} campos.")
            if 'df_campos_no_form' in st.session_state:
                st.session_state['df_campos_no_form']['opcoes'] = st.session_state['df_campos_no_form']['custom_field_options'].apply(
                    extract_names)
                checkbox_condition = st.session_state['df_campos_no_form']['type'] == 'checkbox'
                st.session_state['df_campos_no_form'].loc[checkbox_condition,
                                                          'opcoes'] = 'verdadeiro, falso'
                st.session_state['df_campos_no_form']['tipo'] = st.session_state['df_campos_no_form'].apply(
                    mapear_tipo, axis=1)

                st.data_editor(st.session_state['df_campos_no_form'],
                               column_order=('id', "title", "tipo",
                                             "opcoes"),
                               column_config={
                    "id": st.column_config.Column("ID do Campo", help="**ID** do campo"),
                    "title": st.column_config.Column("Titulo", help="**Titulo** do campo"),
                    "opcoes": st.column_config.Column("Opções de lista suspensa", width="large"),
                },
                    hide_index=True,
                    use_container_width=True,
                    disabled=True)

if menu == 'Condicionais':
    if 'df_campos_no_form' in st.session_state:
        df_campos_condicionais = st.session_state['df_campos_no_form'][(
            st.session_state['df_campos_no_form']['type'].isin(['tagger', 'checkbox']))]
        df_campos_condicionais['tipo'] = df_campos_condicionais.apply(
            mapear_tipo, axis=1)
        # df_campos_condicionais['opcoes'] = df_campos_condicionais['custom_field_options'].apply(extract_names)

    container_camposform = st.container()
    container_importa_planilha = st.container()

    with container_camposform:
        st.write(
            f"Esses são os campos que podem ser usados para as condicionais do formulário **{st.session_state['formulario']['name'][0]}**. Para a importação funcionar, você deve usar **APENAS** esses campos e suas respectivas opções.")
        st.data_editor(df_campos_condicionais,
                       column_order=('id', "title", 'tipo', 'opcoes'),
                       column_config={
                           "title": st.column_config.Column("Titulo", help="**Titulo** do campo")
                       },
                       hide_index=True,
                       use_container_width=True)

    with container_importa_planilha:
        col1, col2 = container_importa_planilha.columns(2)
        col1.write(
            'Você pode importar as condicionais de uma planilha padrão do google Sheets')
        tipo_condicional = col2.selectbox(
            'Tipo de Condicional', ['Agente', 'Usuario Final'],)

        url = st.text_input(
            'Url da planilha', value=st.session_state['url'] if 'url' in st.session_state else '')
        st.session_state['url'] = url
        # url = "https://docs.google.com/spreadsheets/d/1JDy9md2VZPz4JbYtRPJLs81_3jUK47nx6GYQjgU8qNY/edit?usp=sharing"

        if st.button('Verificar', key='check'):
            st.write(st.session_state['verify'])
            df_condicionais_gsheet = importa_google_sheet(url)
            st.dataframe(df_condicionais_gsheet, use_container_width=True, hide_index=True, column_order=[
                         "linha", "Campo", "Opção", "Exibe o campo", "Obrigatoriedade"])

            # Começa a validação dos dados importados

            # #Validação dos campos se estão no formulário.
            st.subheader('Validando campos')

            # separando campos que não estão no formulario ou não estão disponiveis para condicionais
            df_campos_errados = df_condicionais_gsheet[~(
                df_condicionais_gsheet['Campo'].isin(st.session_state['df_campos_no_form']['title']))]

            if not df_campos_errados.empty:
                st.error('Os seguintes campos não estão presentes no formulário. Por favor adicione apenas campos na lista acima ou adicione o campo no formulário primeiro.')
                st.dataframe(df_campos_errados, use_container_width=True, hide_index=True, column_order=[
                    "linha", "Campo", "Opção", "Exibe o campo", "Obrigatoriedade"])
                check_campos = False
            else:
                check_campos = True
                st.success('Campos validados')

            # validando as opções dos campos
            st.subheader('Validando opções de lista suspensa')
            df_opcao_erro = pd.DataFrame()
            # st.write(df_condicionais_gsheet['Opção'])
            # st.write(st.session_state['df_campos_no_form']['opcoes'])

            for indexf, campof in st.session_state['df_campos_no_form'].iterrows():
                for indexg, campog in df_condicionais_gsheet.iterrows():
                    if campof['title'] == campog['Campo']:
                        if str(campog['Opção']) not in campof['opcoes']:
                            df_opcao_erro = pd.concat(
                                [df_opcao_erro, df_condicionais_gsheet.iloc[[indexg], :]], ignore_index=True)

            if not df_opcao_erro.empty:
                st.error(
                    'As seguintes linhas tem opções invalidas. Verifique as opções corretas (cheque espaços em branco, letras MAIUSCULAS e minusculas, etc)')
                st.dataframe(df_opcao_erro, use_container_width=True, hide_index=True, column_order=[
                    "linha", "Campo", "Opção", "Exibe o campo", "Obrigatoriedade"])
                check_opcoes = False
            else:
                check_opcoes = True
                st.success('Opções validadas')

            # Validando ações das condicionais
            st.subheader('Validando ações das condicionais')
            # separando campos que não estão no formulario e por isso não podem ser adicionados a condicionais
            df_condicional_errada = df_condicionais_gsheet[~(
                df_condicionais_gsheet['Exibe o campo'].isin(st.session_state['df_campos_no_form']['title']))]

            if not df_condicional_errada.empty:
                st.error('As seguintes condicionais estão incorretas. Verifique na coluna "Exibe o campo" e o nome está correto e se o campo está inserido no formulário.')
                st.dataframe(df_condicional_errada, use_container_width=True, hide_index=True, column_order=[
                    "linha", "Campo", "Opção", "Exibe o campo", "Obrigatoriedade"])
                check_condicionais = False
            else:
                check_condicionais = True
                st.success('Condicionais validadas')

######## Validações Concluídas #######
            if check_campos == True and check_opcoes == True and check_condicionais == True:

                # df_condicionais_agente = pd.merge(st.session_state['df_campos_no_form'], df_condicionais_gsheet, left_on='title', right_on='Campo', how='inner')
                df_condicionais_campo = pd.merge(
                    st.session_state['df_campos_no_form'], df_condicionais_gsheet, left_on='title', right_on='Campo', how='inner')
                df_condicionais_opcao = pd.merge(
                    st.session_state['df_campos_no_form'], df_condicionais_gsheet, left_on='title', right_on='Exibe o campo', how='inner')
                df_condicionais_sujo = pd.concat(
                    [df_condicionais_campo, df_condicionais_opcao])
                df_condicionais = df_condicionais_sujo.drop_duplicates(
                    subset=['Campo', 'Opção', 'Exibe o campo'])

                st.write(f'criando condicionais de {tipo_condicional}')
                agent_conditions = pd.DataFrame()
                agent_conditions_sujo = pd.DataFrame()
                dic_agent_conditions = list()
                dic_user_conditions = list()

                for index, condition in df_condicionais_gsheet.iterrows():  # Para cada linha do Excel
                    # st.write('loop maior')
                    agent_conditions_sujo = agent_conditions_sujo.append(df_condicionais[(
                        condition['Campo'] == df_condicionais['title'])], ignore_index=True)
                    agent_conditions_sujo['parent_field_id'] = agent_conditions_sujo['id']
                    agent_conditions_sujo['parent_field_type'] = agent_conditions_sujo['type']
                    agent_conditions_sujo['value'] = ''
                    agent_conditions_sujo['id_exibe'] = ''
                    df_child_fields = pd.DataFrame()

                    # Verifica opções das condicionais e retorna valores usaveis no Json
                    for index, linha in agent_conditions_sujo.iterrows():
                        # st.write(f'loop indice: {index} - Para cada linha do excel')
                        if linha['type'] == 'tagger':
                            for opcoes in linha['custom_field_options']:
                                if opcoes['name'] == agent_conditions_sujo['Opção'][index]:
                                    agent_conditions_sujo['value'][index] = opcoes['value']

                        elif linha['type'] == 'checkbox':
                            if agent_conditions_sujo['Opção'][index] == 'verdadeiro':
                                agent_conditions_sujo['value'][index] = True
                            elif agent_conditions_sujo['Opção'][index] == 'falso':
                                agent_conditions_sujo['value'][index] = False

                        # pegando o id do campo que vai exibir
                        df_child_fields_temp = st.session_state['df_campos_no_form'][(
                            st.session_state['df_campos_no_form']['title'] == linha['Exibe o campo'])].reset_index()
                        agent_conditions_sujo['id_exibe'][index] = df_child_fields_temp['id'][0]

                    # agent_conditions['value'] = df_condicionais['custom_field_options'].apply(extract_value)
                    agent_conditions = agent_conditions_sujo.drop_duplicates(
                        subset=['Campo', 'Opção', 'Exibe o campo'])
                st.write(agent_conditions)
                for index, linha in agent_conditions.iterrows():

                    if linha['Obrigatoriedade'] == 'Sempre':
                        required = True
                        status_required = 'ALL_STATUSES'
                        statuses = ''
                    elif linha['Obrigatoriedade'] == 'Nunca':
                        required = False
                        status_required = 'NO_STATUSES'
                        statuses = ''
                    elif linha['Obrigatoriedade'] == 'Novo':
                        required = False
                        status_required = 'SOME_STATUSES'
                        statuses = 'new'
                    elif linha['Obrigatoriedade'] == 'Aberto':
                        required = False
                        status_required = 'SOME_STATUSES'
                        statuses = 'open'
                    elif linha['Obrigatoriedade'] == 'Pendente':
                        required = False
                        status_required = 'SOME_STATUSES'
                        statuses = 'pending'
                    elif linha['Obrigatoriedade'] == 'Em Espera':
                        required = False
                        status_required = 'SOME_STATUSES'
                        statuses = 'hold'
                    elif linha['Obrigatoriedade'] == 'Resolvido':
                        required = False
                        status_required = 'SOME_STATUSES'
                        statuses = 'solved'
                    else:
                        required = False
                        status_required = 'NO_STATUSES'
                        statuses = ''

                    if tipo_condicional == 'Agente':
                        dic_agent_conditions.append(
                            {
                                "parent_field_id": linha['parent_field_id'],
                                "parent_field_type": linha['parent_field_type'],
                                "value": linha['value'],
                                "child_fields": [
                                    {
                                        "id": linha['id_exibe'],
                                        "is_required": required,
                                        "required_on_statuses": {
                                            "type": status_required,
                                            "statuses": [statuses]
                                        }
                                    }
                                ]
                            }
                        )

                    else:
                        dic_user_conditions.append(
                            {
                                "parent_field_id": linha['parent_field_id'],
                                "parent_field_type": linha['parent_field_type'],
                                "value": linha['value'],
                                "child_fields": [
                                    {
                                        "id": linha['id_exibe'],
                                        "is_required": required
                                    }
                                ]
                            }
                        )

                dic_full_form = st.session_state['formulario'].to_dict(
                    orient='records')

                if tipo_condicional == 'Agente':
                    dic_full_form[0]['agent_conditions'] = dic_agent_conditions
                else:
                    dic_full_form[0]['end_user_conditions'] = dic_user_conditions

                # esse codigo exclui a chave custom_statuses das condicionais de agentes, para casos onde tem status customizado, pois isso parece conflitar quando enviamos o forma pela API
                for condicao in dic_full_form[0]['agent_conditions']:
                    for status in condicao['child_fields']:
                        if 'custom_statuses' in status.get('required_on_statuses', {}):
                            del status['required_on_statuses']['custom_statuses']

                # Exclui a chave index que eu nem sei porque tá aqui. :)
                del dic_full_form[0]['index']
                st.session_state['dic_full_form'] = dic_full_form[0]
                st.write(st.session_state['dic_full_form'])

if menu == 'Importação':  # Fim do tratamento do Dicionario começo da importação para o Zendesk

    if 'dic_full_form' not in st.session_state:
        st.header('Defina as condicionais nas etapas anteriores primeiro')
    else:
        st.write('Esse é o Json que será importado. Verifique antes de importar. Uma vez que clicar em importar **NÃO TEM MAIS VOLTA**.')
        st.write(st.session_state['dic_full_form'])

        if st.button('Importar (Enviar para o Zendesk)', key='import', type='secondary'):
            # importar pro Zendesk via Request
            instancia_prod = st.session_state['instancia']
            login_prod = st.session_state['login']
            senha_prod = st.session_state['senha']
            full_form = st.session_state['dic_full_form']

            # montando a requisição para api
            # refine qual objeto está sendo importado
            objeto_upload = {'ticket_form': []}
            objeto_upload['ticket_form'] = full_form

            json_data = json.dumps(objeto_upload)

            # st.write(json_data)
            url_endpoint = st.session_state['formulario']['url'][0]

            response = requests.put(url_endpoint, json_data, headers={
                                    "Content-Type": "application/json"}, auth=(login_prod, senha_prod))
            json_resultado = response.json()
            resposta_codigo = response.status_code
            if resposta_codigo == 200:
                st.success('Importação concluída com sucesso')
            else:
                pass
            st.write(json_resultado)
