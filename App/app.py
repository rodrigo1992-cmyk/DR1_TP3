
import pandas as pd
import streamlit as st
import regex as re

df = pd.DataFrame()
files = st.file_uploader('Upload', type='csv', accept_multiple_files=True)

list_continentes = ['África','América Central','América do Norte', 'América do Sul', 'Ásia', 'Europa', 'Oriente Médio', 'Oceania']


if files != []:
    for file in files:
        data = pd.read_csv(file)
        #Primeiro obtive a identificação do ano, que está dentro de uma frase na terceira linha
        line = data.iloc[1][0]
        #Utilizo Regex para extrair o ano
        Ano = re.findall(r'\b(20[0-9][0-9])\b', line)[0]   
        #Depois trato o restante do arquivo para ficar no formato desejado    
        data = data.iloc[4:]
        data.iloc[0][0] = 'Pais'
        data.columns = data.iloc[0]
        data = data.drop(data.index[0])
        data = data.dropna()
        #Retiro a coluna e a linha de total
        data = data[data['Pais'] != 'Total']
        data = data.drop(columns='Total')
        data['Ano'] = Ano

        #Utilizei IA para criar a função que identifica o continente (Ps: Estou com muita dificuldade para criar funções lambda)
        data['Continente'] = data['Pais'].apply(
            lambda line: next((pais for pais in list_continentes if pais in line), None)
        )
        data['Continente'] = data['Continente'].fillna(method='ffill')

        #Por fim, retiro as linhas que contém o total de cada continente, deixando apenas os países
        data = data[~data['Pais'].isin(list_continentes)]

        data = data.melt(id_vars=['Continente', 'Pais', 'Ano'], var_name='Mes', value_name='Qtd')

        #Concateno em um dataframe, pois assim permito que o usuário faça a importação de diversos CSVs, um para cada ano
        df = pd.concat([df, data])

    #Crio a lista de continentes
    list_cont = df['Continente'].drop_duplicates().tolist()
    list_cont.append('Todos')

    #Pego o id da opção "Todos"
    default_cont = list_cont.index('Todos')

    #Crio o filtro de continentes
    filter_cont = st.selectbox('Filtrar Continentes', list_cont, index=default_cont)

    #Aplico a condição para só filtrar se houver seleção
    if filter_cont != 'Todos':
        df = df.loc[df['Continente'] == filter_cont]

    #Crio o filtro de colunas
    list_colunas = st.multiselect('Selecione as colunas', df.columns, df.columns)
    #Aplico o filtro
    df = df[list_colunas]

    st.write(df)

    
    
