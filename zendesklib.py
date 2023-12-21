############   Biblioteca de funções para o Zendesk
###  VERSÃO 1.03

# v 1.02
#adicionado função busca_macros_por_nome

# v 1.03
#atualizada função busca_macros para fazer busca utilizando cursor
#atualizada função busca_gatilhos para fazer busca utilizando cursor

# v 1.04
#adicionada funções com Sqlite3

# v 1.04.1
#adicionada função busca_ip_server para conseguir rodar no google colab em instancia com restrição de ip

import json
import requests
import sqlite3
import socket

###### FUNÇÕES #####
def busca_ip_server():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f'O IP do servidor é: {ip_address}')
#   return ip_address
    

#Trata o retorno da API
def trata_resposta_api(response):
    if response.status_code == 400:
        print('Solicitação inválida.')
    elif response.status_code == 401:
        print('Não autorizado.')
    elif response.status_code == 403:
        print('Acesso proibido.')
    elif response.status_code == 404:
        print('Não encontrado.')
    elif response.status_code == 500:
        print('Erro interno do servidor.')
        
## Importa dados de uma planilha CSV para um dicionario, a primeira linha são as chaves e as linhas abaixo são os valores
def importar_csv(caminho_arquivo):    
    import csv
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv, delimiter=',', quotechar='"')
        dados = [linha for linha in leitor_csv]
    chaves = dados[0] # assume que a primeira linha contém as chaves
    valores = dados[1:] # assume que o restante das linhas contém os valores
    resultado = [dict(zip(chaves, linha)) for linha in valores]
    return resultado

# Mesma coisa mas sem utf-8
def importar_csv_excel(caminho_arquivo):    
    import csv
    with open(caminho_arquivo, 'r') as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv, delimiter=';', quotechar='"')
        dados = [linha for linha in leitor_csv]
    chaves = dados[0] # assume que a primeira linha contém as chaves
    valores = dados[1:] # assume que o restante das linhas contém os valores
    resultado = [dict(zip(chaves, linha)) for linha in valores]
    return resultado

##################################  Buscas informações da API do Zendesk ##############

def busca_macros(instancia,login,senha,active=True):
    #Função que busca macros na instancia utilizando busca com cursor
    if active == True:
        url_macro = instancia + '/api/v2/macros.json?active=true&page[size]=100'
        mensagem = 'buscando somente macros ativas'
    else:
        url_macro = instancia + '/api/v2/macros.json?page[size]=100'
        mensagem = 'buscando macros ativas e inativas'
    
    response = requests.get(url_macro, auth=(login,senha))
    trata_resposta_api(response)
    macros_temp = response.json()
    print(mensagem)
    macros_zendesk = macros_temp['macros']        
    contador = 1
    while macros_temp['meta']['has_more'] is True:
        contador = contador+1
        print(f"buscando mais macros - Pagina {str(contador)}")
        response = requests.get(macros_temp['links']['next'], auth=(login,senha))
        trata_resposta_api(response)
        macros_temp = response.json()
        for macro_for_temp in macros_temp['macros']:
            macros_zendesk.append(macro_for_temp)
    return macros_zendesk

def busca_macros_por_nome(instancia,login,senha,nome):
    url_macro = instancia + '/api/v2/macros/search?query="'+ nome +'"'
#     print('buscando')
    try:
        response = requests.get(url_macro, auth=(login,senha))
        trata_resposta_api(response)
        macros_zendesk = response.json()
        return macros_zendesk
    except:
        print (f'macro com o nome {nome} retornou erro')
        pass
    

### busca por todos os grupos da instancia
def busca_grupos(instancia,login,senha):
    url_grupo = instancia + "/api/v2/groups"
#     print("buscando grupos")
    response = requests.get(url_grupo, auth=(login,senha))
    trata_resposta_api(response)
    grupos_temp = response.json()
    grupos_zendesk = grupos_temp['groups']
    while grupos_temp['next_page'] is not None:
#         print("buscando mais grupos")
        response = requests.get(grupos_temp['next_page'], auth=(login,senha))
        trata_resposta_api(response)
        grupos_temp = response.json()
        for grupo_for_temp in grupos_temp['groups']:
            grupos_zendesk.append(grupo_for_temp)
#     print(f"{len(grupos_zendesk)} grupos foram encontrados")
    return grupos_zendesk

### busca todos os formularios da instancia
def busca_formularios(instancia,login,senha):
    url_form = instancia + "/api/v2/ticket_forms"
    response_api = requests.get(url_form, auth=(login,senha))
    trata_resposta_api(response_api)
    form_temp = response_api.json()
    form_zendesk = form_temp['ticket_forms']
    while form_temp['next_page'] is not None:
        response = requests.get(form_temp['next_page'], auth=(login,senha))
        trata_resposta_api(response)
        form_temp = response.json()
        for form_for_temp in form_temp['ticket_forms']:
            form_zendesk.append(form_for_temp)
    return form_zendesk

### busca todas as organizações da instancia
def busca_organizacao(instancia,login,senha):
    print('busca_org')
    url_form = instancia + "/api/v2/organizations"
    response_api = requests.get(url_form, auth=(login,senha))
    trata_resposta_api(response_api)
    org_temp = response_api.json()
    org_zendesk = org_temp['organizations']
    while org_temp['next_page'] is not None:
        print(org_temp['next_page'])
        response = requests.get(org_temp['next_page'], auth=(login,senha))
        trata_resposta_api(response)
        org_temp = response.json()
        for org_for_temp in org_temp['organizations']:
            org_zendesk.append(org_for_temp)
    return org_zendesk


### busca por todos os campos da instancia
def busca_campos(instancia,login,senha):
    url_campo = instancia + "/api/v2/ticket_fields"
    response_api = requests.get(url_campo, auth=(login,senha))
    trata_resposta_api(response_api)
    campo_zendesk = response_api.json()
    campo_zendesk = campo_zendesk['ticket_fields']
    return campo_zendesk

def busca_sla_filters(instancia,login,senha):
    url_sla_filter = instancia + "/api/v2/slas/policies/definitions"
    response_api = requests.get(url_sla_filter, auth=(login, senha))
    trata_resposta_api(response_api)
    sla_filter = response_api.json()
    sla_filter = sla_filter['definitions']['all']
    return sla_filter

def busca_gatilhos(instancia,login,senha,active=True):
    #Função que busca gatilhos na instancia utilizando busca com cursor
    if active == True:
        url_objeto = instancia + '/api/v2/triggers.json?active=true&page[size]=100'
        mensagem = 'buscando somente gatilhos ativos'
    else:
        url_objeto = instancia + '/api/v2/triggers.json?page[size]=100'
        mensagem = 'buscando gatilhos ativos e inativos'
    
    response = requests.get(url_objeto, auth=(login,senha))
    trata_resposta_api(response)
    objeto_temp = response.json()
    print(mensagem)
    objeto_zendesk = objeto_temp['triggers']        
    contador = 1
    while objeto_temp['meta']['has_more'] is True:
        contador = contador+1
        print(f"buscando mais gatilhos - Pagina {str(contador)}")
        response = requests.get(objeto_temp['links']['next'], auth=(login,senha))
        trata_resposta_api(response)
        objeto_temp = response.json()
        for objeto_for_temp in objeto_temp['triggers']:
            objeto_zendesk.append(objeto_for_temp)
    return objeto_zendesk

################ VERIFICAR DADOS VIA API

#verifica se um grupo existe no dicionario criado com a função busca_grupos
def verifica_grupo_existente(valor,dicionario_grupo):
    for grupo in dicionario_grupo:
        if grupo['name'] == valor:
            return True
    return False
   

#busca informações de um campo em especifico direto da API
def busca_campo_api (instancia,login,senha,id_campo):
    endpoint = instancia + '/api/v2/ticket_fields/' + id_campo
    response_api = requests.get(endpoint, auth=(login,senha))
    trata_resposta_api(response_api)
    campo_zendesk = response_api.json()
    campo_zendesk = campo_zendesk['ticket_field']
    return campo_zendesk

#busca o nome de um campos apartir do dicionario criado com a função busca_campos
def busca_campo_dicionario(dicionario,id_campo):
    count = 0
    for elemento in dicionario:
        if int(elemento['id']) == int(id_campo):
            count = count + 1
            return elemento
    if count == 0:
        print ('Campos não encontrado')


## Verifica se um form existe no dicionario criado com a função busca_formularios
def verifica_form_existente(valor,dicionario_form):
    for form in dicionario_form:
        if form.get('name').lower().replace(' ', '').replace('?', '').replace(':', '').replace('.', '').encode('ascii', 'ignore').decode() == valor.lower().replace(' ', '').replace('?', '').replace(':', '').replace('.', '').encode('ascii', 'ignore').decode():
            idform = form.get('id')
            return idform
    return False

#Se o form existe, busca o ID dos campos
def busca_id_campos_form(valor,dicionario_form):
    if verifica_form_existente(valor,dicionario_form) != False:
        for form in dicionario_form:
            if form.get('name').lower().replace(' ', '').replace('?', '').replace(':', '').replace('.', '').encode('ascii', 'ignore').decode() == valor.lower().replace(' ', '').replace('?', '').replace(':', '').replace('.', '').encode('ascii', 'ignore').decode():
                form_campos_ids = form.get('ticket_field_ids')
                return form_campos_ids
        return False
    
#com o Id dos campos, busca os nomes do campo na instancia original
def busca_nome_campos_form(form_campos_ids, dicionario_campos):
    campos_list = []
    for id in form_campos_ids:
        for campo in dicionario_campos:
            if campo.get('id') == id:
                if campo.get('title') not in ["Status", "Grupo", "Assunto", "Descrição", "Atribuído para","Ticket status"]:
                    campos_dict = campo
                    campos_list.append(campos_dict)
    return campos_list

####### FUNÇÕES USANDO O SQL ####

def cria_banco(nome_banco):
    banco = sqlite3.connect(nome_banco)
    print (F"Banco {nome_banco} criado com sucesso")
    










