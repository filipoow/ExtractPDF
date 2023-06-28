# Importando as bibliotecas
import pandas as pd
import numpy as np
import PyPDF2
import os
import re

#Importando bases do Excel para apoio
veiculos = pd.read_excel(r'CONFIG\PLACAS.xlsx')
regiao = pd.read_excel(r'CONFIG\UF_REGIAO.xlsx')
base_sm = pd.read_excel(r'SMs.xlsx')

def extrair_informacoes(texto):
    informacoes = {}

    data_solicitacao = re.search(r"SOLICITACAO DE MONITORAMENTO\n(\d{2}/\d{2}/\d{4})", texto)
    if data_solicitacao:
        informacoes['DATA'] = data_solicitacao.group(1)

    horario_solicitacao  = re.search(r"SOLICITACAO DE MONITORAMENTO\n\d{2}/\d{2}/\d{4} (\d{2}:\d{2}:\d{2})", texto)
    if horario_solicitacao :
        informacoes['HORA'] = horario_solicitacao.group(1)

    num_solicitacao = re.search(r"SM: #(\d+)", texto)
    if num_solicitacao:
        informacoes['SM'] = num_solicitacao.group(1)

    origem = re.search(r"ORIGEM\nLOCAL: (.+)", texto)
    if origem:
        informacoes['ORIGEM.LOCAL'] = origem.group(1)

    origem_cidade = re.search(r"ORIGEM.*?CIDADE/UF:\s+(.+?)\s+CEP:", texto, re.IGNORECASE | re.DOTALL)
    if origem_cidade:
        informacoes['ORIGEM'] = origem_cidade.group(1)

    destinos = re.findall(r"DESTINO \d+\nLOCAL: ([^\n]+) PREVISAO:", texto)
    if destinos:
        informacoes['DESTINO.INCLUÍDO.LOCAL'] = destinos

    destinos_cidades = re.findall(r"DESTINO.*?CIDADE/UF:\s+(.+?)\s+CEP:", texto, re.IGNORECASE | re.DOTALL)
    if destinos_cidades:
        informacoes['DESTINO INCLUÍDO'] = destinos_cidades

    destino_final = re.search(r"DESTINO FINAL\nLOCAL: ([^\n]+) PREVISAO:", texto)
    if destino_final:
        informacoes['DESTINO.LOCAL'] = destino_final.group(1)

    destino_final_cidade = re.search(r"DESTINO FINAL.*?CIDADE/UF:\s+(.+?)\s+CEP:", texto, re.IGNORECASE | re.DOTALL)
    if destino_final_cidade:
        informacoes['DESTINO'] = destino_final_cidade.group(1)

    rota = re.search(r"ROTA\n(.+)", texto)
    if rota:
        informacoes['ROTA'] = rota.group(1)

    cavalo = re.search(r"CAVALO:\s+(.*?)\s+CIDADE/UF:", texto, re.IGNORECASE)
    if cavalo:
        informacoes['PLACA_CAV'] = cavalo.group(1)

    carreta = re.search(r"CARRETA:\s+(.*?)\s+CIDADE/UF:", texto, re.IGNORECASE)
    if carreta:
        informacoes['PLACA_CARRETA'] = carreta.group(1)

    motorista = re.search(r"MOTORISTA / AJUDANTE\nCPF MOTORISTA: (\d+) NOME:(.+) FONE:(.+)", texto)
    if motorista:
        informacoes['CPF'] = motorista.group(1)
        informacoes['MOTORISTA'] = motorista.group(2)
        informacoes['TELEFONE'] = motorista.group(3)

    ajudante = re.search(r"CPF AJUDANTE: (\d+) NOME:(.+) FONE:(.+)", texto)
    if ajudante:
        informacoes['CPF_2'] = ajudante.group(1)
        informacoes['MOTORISTA_2'] = ajudante.group(2)
        informacoes['TELEFONE_2'] = ajudante.group(3)

    # isca = re.search(r"ISCA: (\d+)", texto)
    # if isca:
    #     informacoes['ISCA'] = isca.group(1)

    # # Extrair manifesto a partir da sessão de observações até a palavra "manifesto" em maiúsculo
    # observacoes = re.search(r"OBSERVACOES\n([\s\S]+?)(?=\nMANIFESTO)", texto, re.IGNORECASE)
    # if observacoes:
    #     manifestos = re.findall(r"Manifesto ([^\n]+)", observacoes.group(1))
    #     if manifestos:
    #         informacoes['MANIFESTO'] = manifestos

    # Extrair manifesto a partir da sessão "MANIFESTO" até a sessão "DADOS COMPLEMENTARES"
    manifesto_complementares = re.findall(r"MANIFESTO([\s\S]+?)DADOS COMPLEMENTARES", texto, re.DOTALL)
    if manifesto_complementares:
        informacoes['MANIFESTO'] = manifesto_complementares[0].split('\n')
                            
    observacoes = re.findall(r"OBSERVACOES\n(.+?)(?=MANIFESTO\s)", texto, re.DOTALL)
    if observacoes:
        informacoes['OBSERVAÇÃO'] = observacoes[0].split('\n')

    valor_viagem = re.search(r"VALOR DA VIAGEM:\s*(.*?)\s*INCLUSAO:", texto, re.IGNORECASE | re.DOTALL)
    if valor_viagem:
        informacoes['VALOR R$'] = valor_viagem.group(1)

    return informacoes


def extrair_informacoes_pdf(caminho_pdf):
    informacoes = {}

    with open(caminho_pdf, 'rb') as arquivo_pdf:
        reader = PyPDF2.PdfReader(arquivo_pdf)

        texto_completo = ""
        for pagina in reader.pages:
            texto_completo += pagina.extract_text()

        informacoes = extrair_informacoes(texto_completo)

    return informacoes

def determinar_tipo_rota(origem, destino,rota):
    origem_lower = origem.lower()
    destino_lower = destino.lower()
    rota_lower = rota.lower()

    if 'matriz' in origem_lower and 'matriz' in destino_lower:
        return 'COLETA'
    elif rota_lower=='sim' and origem_lower==destino_lower:
        return 'COLETA'
    elif 'matriz' in origem_lower or 'matriz' in destino_lower:
        return 'PRIMARIA'
    else:
        return 'SECUNDARIA'

def determinar_rota_unificada(tam):
    if tam > 1:
        return 'NÃO'
    elif tam == 0:
        return 'NÃO'
    else:
        return 'SIM'

def determinar_trecho(origem, destino):
    origem_lower = origem.lower()
    destino_lower = destino.lower()

    if 'matriz' in origem_lower and 'matriz' in destino_lower:
        return 'IN'
    elif 'matriz' in destino_lower:
        return 'OUT'
    else:
        return 'IN'
    
def separar_lista(coluna):
    resultado_formatado = ' / '.join(coluna)
    return resultado_formatado

def ajustar_erros(texto):
    padrao = r'^(.*?)RODOBENS GERENCIAMENTO DE RISCO'
    resultado = re.search(padrao, texto)
    if resultado:
        return resultado.group(1).strip()
    else:
        return texto
    
def ajustar_erros_paginacao(texto):
    padrao = r'^(.*?)SOLICITACAO DE MONITORAMENTOSM:'
    resultado = re.search(padrao, texto)
    if resultado:
        return resultado.group(1).strip()
    else:
        return texto

def transformar_valor(valor):
    valor_numerico = float(valor.replace('.','').replace(',','.'))  
    return valor_numerico

def excluir_arquivos_pasta(pasta):
    for arquivo in os.listdir(pasta):
        caminho_arquivo = os.path.join(pasta,arquivo)
        if os.path.isfile(caminho_arquivo):
            os.remove(caminho_arquivo)

def obter_primeiro_valor(lista):
    if lista:
        return lista[0]
    else:
        return ''

# Configurações iniciais
caminho_pdf = r'C:\Users\karina.teotonio\Desktop\Karina Cristina\SMs Script\SM'
lista_pdf = os.listdir(caminho_pdf)
pdfVazio = pd.DataFrame()

for file in lista_pdf:
    informacoes_pdf = extrair_informacoes_pdf(fr'{caminho_pdf}/{file}')

    chaves = informacoes_pdf.keys()
    if 'OBSERVAÇÃO' in chaves:      
        # Listagem de itens do manifesto
        itens_manifestos = []

        # Para cada item no manifesto adiciona na lista
        for item in informacoes_pdf['MANIFESTO']:
            itens_manifestos.append(item)

        # Removendo os itens dos manifestos
        informacoes_pdf['MANIFESTO'] = [item for item in informacoes_pdf['MANIFESTO'] if item not in itens_manifestos]

        # Adicionando os manifestos de OBSERVAÇÃO para a coluna MANIFESTOS
        informacoes_pdf['MANIFESTO'] += [item for item in informacoes_pdf['OBSERVAÇÃO'] if 'manifesto' in item.lower()]

        # Removendo os manifestos da coluna de OBSERVAÇÃO
        informacoes_pdf['OBSERVAÇÃO'] = [item for item in informacoes_pdf['OBSERVAÇÃO'] if 'manifesto' not in item.lower()]

        # Adicionando os itens antigos
        informacoes_pdf['MANIFESTO'] += [item for item in itens_manifestos]

        # Remoção de itens vazios da lista "OBSERVAÇÃO"
        informacoes_pdf['OBSERVAÇÃO'] = [item for item in informacoes_pdf['OBSERVAÇÃO'] if item.strip()]

        # Atualização das iscas no campo correto
        if 'ISCA' not in chaves:
            informacoes_pdf['ISCA'] = ['']
    
        # Adicionando as iscas de OBSERVAÇÃO para a coluna ISCA
        informacoes_pdf['ISCA'] += [item for item in informacoes_pdf['OBSERVAÇÃO'] if 'isca' in item.lower()]

        # Removendo as iscas da coluna de OBSERVAÇÃO
        informacoes_pdf['OBSERVAÇÃO'] = [item for item in informacoes_pdf['OBSERVAÇÃO'] if 'isca' not in item.lower()]

        # Remoção de itens vazios da lista "ISCA"
        informacoes_pdf['ISCA'] = [item for item in informacoes_pdf['ISCA'] if item.strip()]

    # Remoção de itens vazios da lista "MANIFESTO"
    informacoes_pdf['MANIFESTO'] = [item for item in informacoes_pdf['MANIFESTO'] if item.strip()]

    #Transformando em DF
    pdfExcel = pd.json_normalize(informacoes_pdf)

    #Removendo colunas desnecessárias
    pdfExcel = pdfExcel.drop(columns=['TELEFONE'])

    # Descobrindo o tamanho do DESTINO.INCLUÍDO.LOCAL
    if 'DESTINO.INCLUÍDO.LOCAL' not in pdfExcel.columns.tolist():
        pdfExcel['TAM'] = 0
    else:
        pdfExcel['TAM'] = pdfExcel['DESTINO.INCLUÍDO.LOCAL'].apply(len)

    # Determinando se a ROTA é UNIFICADA
    pdfExcel['ROTA UNIFICADA?'] = pdfExcel.apply(lambda row: determinar_rota_unificada(row['TAM']), axis=1)
    
    # Determinando o tipo de ROTA
    pdfExcel['TIPO_ROTA'] = pdfExcel.apply(lambda row: determinar_tipo_rota(row['ORIGEM.LOCAL'], row['DESTINO.LOCAL'],row['ROTA UNIFICADA?']), axis=1)

    # Adicionando a região
    pdfExcel['UF'] = pdfExcel['DESTINO'].str[-2:]
    pdfExcel = pdfExcel.merge(right=regiao, on='UF').drop(columns=['UF'])

    # Adicionando a empresa
    pdfExcel = pdfExcel.merge(right=veiculos, on='PLACA_CAV')

    # Trazendo o valor do DESTINO INCLUÍDO
    if 'DESTINO.INCLUÍDO.LOCAL' in pdfExcel.columns.tolist():
        pdfExcel['DESTINO INCLUÍDO'] = np.where(pdfExcel['ROTA UNIFICADA?']=='NÃO','',pdfExcel['DESTINO INCLUÍDO'][0][0])
        #pdfExcel['TIPO_OPERACIONAL'] = np.where(pdfExcel['ROTA UNIFICADA?']=='NÃO','',pdfExcel['DESTINO.INCLUÍDO.LOCAL'][0][0])
    else:
        pdfExcel['DESTINO INCLUÍDO'] = ''
    #pdfExcel['ORIGEM'] = np.where(pdfExcel['ROTA UNIFICADA?']=='NÃO',pdfExcel['ORIGEM'],pdfExcel['ORIGEM.LOCAL'])
    #pdfExcel['DESTINO'] = np.where(pdfExcel['ROTA UNIFICADA?']=='NÃO',pdfExcel['DESTINO'],pdfExcel['DESTINO.LOCAL'])

    # Definindo o TRECHO
    pdfExcel['TRECHO'] = pdfExcel.apply(lambda row: determinar_trecho(row['ORIGEM.LOCAL'], row['DESTINO.LOCAL']), axis=1)

    #Criando colunas para o DF
    verificacao_de_colunas = ['DATA','HORA','SM','VALOR R$','ORIGEM','ROTA UNIFICADA?','DESTINO INCLUIDO','DESTINO','ROTA','REGIAO','TIPO_ROTA','TIPO_OPERACIONAL','PLACA_CAV','PLACA_CARRETA','EMPRESA','MOTORISTA','CPF','MOTORISTA_2','CPF_2','ISCA','MANIFESTO','OBSERVAÇÃO','TRECHO','OCORRÊNCIA','LOCAL DA OCORRÊNCIA','UF do LOCAL DA OCORRÊNCIA','CATEGORIA','PRIORIDADE','IMAGEM','OCORRÊNCIA_2','LOCAL DA OCORRÊNCIA_2','UF do LOCAL DA OCORRÊNCIA_2','CATEGORIA_2','PRIORIDADE_2','IMAGEM_2']
    for i in verificacao_de_colunas:
        if i not in pdfExcel.columns.tolist():
            pdfExcel[i] = ''

    #Validação de colunas, para a criação
    if 'MOTORISTA_2' not in pdfExcel.columns.tolist():
        pdfExcel[['MOTORISTA_2','CPF_2']] = ''

    # Campo de ocorrências sendo preenchido
    pdfExcel['OCORRÊNCIA'] = 'NÃO'

    # Criando as separações de lista ou selecionando o primeiro item
    pdfExcel['MANIFESTO'] = pdfExcel['MANIFESTO'].apply(separar_lista)
    pdfExcel['OBSERVAÇÃO'] = pdfExcel['OBSERVAÇÃO'].apply(separar_lista)
    pdfExcel['ISCA'] = pdfExcel.apply(lambda row: obter_primeiro_valor(row['ISCA']), axis=1)

    # Transformações para outro tipo 
    pdfExcel['SM'] = pd.to_numeric(pdfExcel['SM'])
    pdfExcel['CPF'] = pd.to_numeric(pdfExcel['CPF'])
    pdfExcel['CPF_2'] = pd.to_numeric(pdfExcel['CPF_2'])
    pdfExcel['DATA'] = pd.to_datetime(pdfExcel['DATA'],dayfirst=True)
    pdfExcel['VALOR R$'] = pdfExcel['VALOR R$'].str.replace('R$','',regex=False)

    # Ajustando possíveis erros
    pdfExcel['MANIFESTO'] = pdfExcel['MANIFESTO'].apply(ajustar_erros)
    pdfExcel['OBSERVAÇÃO'] = pdfExcel['OBSERVAÇÃO'].apply(ajustar_erros)
    pdfExcel['ISCA'] = pdfExcel['ISCA'].apply(ajustar_erros)

    pdfExcel['MANIFESTO'] = pdfExcel['MANIFESTO'].apply(ajustar_erros_paginacao)
    pdfExcel['OBSERVAÇÃO'] = pdfExcel['OBSERVAÇÃO'].apply(ajustar_erros_paginacao)
    pdfExcel['ISCA'] = pdfExcel['ISCA'].apply(ajustar_erros_paginacao)

    # Transformando o tipo de VALOR
    pdfExcel['VALOR R$'] = pdfExcel.apply(lambda row: transformar_valor(row['VALOR R$']), axis=1)
    
    # Reordenando as colunas do DF
    pdfExcel = pdfExcel[['DATA','HORA','SM','VALOR R$','ORIGEM','ROTA UNIFICADA?','DESTINO INCLUÍDO','DESTINO','ROTA','REGIAO','TIPO_ROTA','TIPO_OPERACIONAL','PLACA_CAV','PLACA_CARRETA','EMPRESA','MOTORISTA','CPF','MOTORISTA_2','CPF_2','ISCA','MANIFESTO','OBSERVAÇÃO','TRECHO','OCORRÊNCIA','LOCAL DA OCORRÊNCIA','UF do LOCAL DA OCORRÊNCIA','CATEGORIA','PRIORIDADE','IMAGEM','OCORRÊNCIA_2','LOCAL DA OCORRÊNCIA_2','UF do LOCAL DA OCORRÊNCIA_2','CATEGORIA_2','PRIORIDADE_2','IMAGEM_2']]
    pdfVazio = pd.concat([pdfVazio,pdfExcel])
    pdfVazio = pdfVazio.sort_values(by='SM',ascending=True)
# Exportando o arquivo para Excel
pdfVazio.to_excel('SMs.xlsx',index=False)