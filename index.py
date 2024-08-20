import requests
import pandas as pd
import sqlite3
import streamlit as st
import matplotlib.pyplot as plt

# Dados Ibge
def get_ibge_data():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/4301602"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        population_url = f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2023/variaveis/9324?localidades=N6[{data['id']}]"
        pop_response = requests.get(population_url)
        if pop_response.status_code == 200:
            pop_data = pop_response.json()
            return pop_data
    return None

# Buscando dados do Sindicato
def get_sindicato_data():
    url = "https://localhost:3001/comparacao"
    response = requests.get(url, verify=False)  # Disabling SSL verification for localhost
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    return None

# Persistindo os dados
def save_to_sqlite(df, db_name='comparacao.db'):
    conn = sqlite3.connect(db_name)
    df.to_sql('comparacao', conn, if_exists='replace', index=False)
    conn.close()

# gráficos e comparações
def plot_comparison(df, selected_disease):
    filtered_df = df[df['Doença'] == selected_disease]
    if not filtered_df.empty:
        st.write(f"Comparação para {selected_disease}:")
        st.bar_chart(filtered_df[['Casos', 'Acidentes de Trabalho']].set_index(df['Doença']))
    else:
        st.write("Doença não encontrada.")

# Imprimir os dados selecionados
def print_selected_data(df, selected_disease):
    filtered_df = df[df['Doença'] == selected_disease]
    if not filtered_df.empty:
        st.write(f"Dados selecionados para {selected_disease}:")
        st.dataframe(filtered_df)
    else:
        st.write("Doença não encontrada.")

st.title('Análise de Dados de Saúde e Trabalho')

ibge_data = get_ibge_data()
sindicato_data = get_sindicato_data()

if ibge_data:
    population = ibge_data[0]['resultados'][0]['series'][0]['serie']['2023']
    st.write(f"População de Bagé (2023): {population}")

if sindicato_data is not None:
    st.write("Dados do sindicato:")
    st.dataframe(sindicato_data)
    save_to_sqlite(sindicato_data)  # Salva os dados em SQLite

    option = st.sidebar.selectbox('Selecione a visualização:', ['Doenças', 'Acidentes de Trabalho', 'Atestados'])

    if option == 'Doenças':
        selected_disease = st.selectbox('Selecione a Doença:', sindicato_data['Doença'])
        plot_comparison(sindicato_data, selected_disease)
        print_selected_data(sindicato_data, selected_disease)

    elif option == 'Acidentes de Trabalho':
        st.write("Dados de Acidentes de Trabalho:")
        st.bar_chart(sindicato_data[['Doença', 'Acidentes de Trabalho']].set_index('Doença'))

    elif option == 'Atestados':
        st.write("Dados de Atestados:")
        st.bar_chart(sindicato_data[['Doença', 'Atestados']].set_index('Doença'))

else:
    st.write("Não foi possível obter os dados do sindicato.")
