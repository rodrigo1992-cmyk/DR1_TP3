
import pandas as pd
import streamlit as st
import regex as re
import time

#Adicionando o Color Picker
col1, col2 = st.columns(2)

with col1:
    cor_fundo = st.color_picker("Escolha a cor de fundo", "#FFFFFF")  

with col2:
    cor_fonte = st.color_picker("Escolha a cor da fonte", "#000000")  

#Alterando o estilo da classe stApp
st.markdown(f"<style> .stApp {{background-color: {cor_fundo}; color:{cor_fonte};}}   </style>", unsafe_allow_html=True)


df = pd.DataFrame()
files = st.file_uploader('Upload', type='csv', accept_multiple_files=True)

list_continentes = ['África','América Central','América do Norte', 'América do Sul', 'Ásia', 'Europa', 'Oriente Médio', 'Oceania']


if files != []:
    #Adicionando o Spinner
    with st.spinner('Upload em andamento...'):
        time.sleep(2)
        st.success("Upload concluído!")

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

    #Adicionando a barra de progresso
    my_bar = st.progress(0, text="Carregando a Visualização...")
    for percent_complete in range(100):
        time.sleep(0.005)
        my_bar.progress(percent_complete + 1, text="Carregando a Visualização...")
    time.sleep(0.5)
    my_bar.empty()

    #Mostro a tabela filtrada
    st.write(df) 

    #Converto para CSV
    csv = df.to_csv().encode("utf-8")

    #Crio botão para baixar o arquivo csv
    st.download_button(
        label="Baixar Dados",
        data=csv,
        file_name="base.csv",
        mime="text/csv",
    )


    
