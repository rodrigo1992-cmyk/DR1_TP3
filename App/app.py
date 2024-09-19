
import pandas as pd
import streamlit as st
import regex as re
import time
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px


def barra_lateral():
    st.sidebar.header('Filtros')
    #Adicionando o Color Picker
    cor_fundo = st.sidebar.color_picker("Cor de fundo", "#FFFFFF")
    cor_fonte = st.sidebar.color_picker("Cor da fonte", "#000000")  

    #Alterando o estilo da classe stApp
    st.markdown(f"<style> .stApp {{background-color: {cor_fundo}; color:{cor_fonte};}}   </style>", unsafe_allow_html=True)

def upload():
    files = st.file_uploader('Upload', type='csv', accept_multiple_files=True)
    return files

@st.cache_data
def tratamento(files):
    
    df = pd.DataFrame()
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

            #Convertendo o campo Qtd para número
            data['Qtd'] = data['Qtd'].str.replace(' ', '')
            data['Qtd'] = pd.to_numeric(data['Qtd'], errors='coerce')
            
            #Concateno em um dataframe, pois assim permito que o usuário faça a importação de diversos CSVs, um para cada ano
            df = pd.concat([df, data])

            #Converto para CSV
            csv = df.to_csv().encode("utf-8")

        return df, csv

def filtra_df(df):
    if df is not None:
        
        #Inicializo o session_state
        if 'filter_cont' not in st.session_state:
            st.session_state.filter_cont = 'Todos'
        if 'list_colunas' not in st.session_state:
            st.session_state.list_colunas = df.columns.tolist()

        #Crio a lista de continentes
        list_cont = df['Continente'].drop_duplicates().tolist()
        list_cont.append('Todos')

        #Crio o filtro de continentes
        st.session_state.filter_cont = st.sidebar.selectbox('Filtrar Continentes', list_cont, index=list_cont.index(st.session_state.filter_cont))

        #Aplico a condição para só filtrar se houver seleção
        if st.session_state.filter_cont != 'Todos':
            df = df.loc[df['Continente'] == st.session_state.filter_cont]

        df_filt = df.copy()
        #Crio o filtro de colunas
        st.session_state.list_colunas = st.sidebar.multiselect('Selecione as colunas', df.columns, st.session_state.list_colunas)

        #Aplico o filtro
        df_filt_tab = df[st.session_state.list_colunas]

        #Adicionando a barra de progresso
        my_bar = st.progress(0, text="Carregando a Visualização...")
        for percent_complete in range(100):
            time.sleep(0.001)
            my_bar.progress(percent_complete + 1, text="Carregando a Visualização...")
        time.sleep(0.5)
        my_bar.empty()
    
        return df_filt, df_filt_tab

def exibe_tabelas(df):
    st.write('## Tabela Comum')
    st.dataframe(df)

    st.write('## Tabela Interativa')
    if df is not None:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=False, groupable=True)
        gb.configure_selection('multiple', use_checkbox=True)
        gridOptions = gb.build()

        AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True)

def graficos(df):
    # Criando o gráfico de pizza
    fig = px.pie(
        df,
        values='Qtd',
        names='Continente',
        title='Quantidade de Turistas por Continente',
        labels={'Qtd Tutistas': 'Qtd'},
        hole=False
    )

    fig.update_traces(textinfo='label+percent', textfont_size=10)

    st.plotly_chart(fig)

    #Criando Gráfico de Barras
    fig = px.bar(
        df,
        x='Pais',
        y='Qtd',
        title='Quantidade de Turistas por Pais',
        labels={'Qtd Tutistas': 'Qtd'}
    )

    st.plotly_chart(fig)

    #Criando histrograma
    fig = px.histogram(
        df,
        x='Qtd',
        title='Distribuição da Qtd de Turistas',
        labels={'Qtd': 'Quantidade de Turistas'},
        nbins=20
    )

    st.plotly_chart(fig)

def metricas(df):
    #Qtd linhas
    qtd_linhas = df.shape[0]
    
    #Média de passageiros
    media_psg = round(df['Qtd'].mean(),0)

    #Total de passageiros
    total_psg = df['Qtd'].sum()

    # Exibindo as métricas
    a,b,c = st.columns(3)

    with a:
        st.metric(label="Qtd Registros", value=qtd_linhas)
    with b:
        st.metric(label="Média Passageiros por Registro", value=media_psg)
    with c:
        st.metric(label="Total de Passageiros", value=total_psg)

################### INICIANDO O APP ######################

barra_lateral()
files = upload()

start = time.time()

st.write('# Rodrigo_Mesquita_DR1_TP3')
st.write('## Desenvolvimento Front-End com Python (com Streamlit) [24E3_1]')
st.write('Notebook disponível em: https://github.com/rodrigo1992-cmyk/DR1_TP3')
st.write('Para testar o aplicativo, realizar upload dos arquivos disponíveis em: https://github.com/rodrigo1992-cmyk/DR1_TP3/tree/main/Data')


if files:
    df, csv = tratamento(files)
    df_filt, df_filt_tab = filtra_df(df)
    metricas(df_filt)
    graficos(df_filt)
    exibe_tabelas(df_filt_tab)
    st.download_button(label="Baixar Dados", data=csv, file_name="base.csv", mime="text/csv")
end = time.time()

st.write(f'Tempo de execução: {end - start:.2f} segundos')
