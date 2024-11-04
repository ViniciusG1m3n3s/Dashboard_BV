import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from diario import diario  # Importa o diário de bordo

# Função para carregar os dados do Excel do usuário logado
def load_data(usuario):
    excel_file = f'dados_acumulados_{usuario}.xlsx'  # Nome do arquivo específico do usuário
    if os.path.exists(excel_file):
        df_total = pd.read_excel(excel_file, engine='openpyxl')
    else:
        df_total = pd.DataFrame(columns=['NÚMERO DO PROTOCOLO', 'USUÁRIO QUE CONCLUIU A TAREFA', 'SITUAÇÃO DA TAREFA', 'TEMPO MÉDIO OPERACIONAL', 'DATA CRIAÇÃO DA TAREFA'])
    return df_total

# Função para salvar os dados no Excel do usuário logado
def save_data(df, usuario):
    excel_file = f'dados_acumulados_{usuario}.xlsx'  # Nome do arquivo específico do usuário
    df['TEMPO MÉDIO OPERACIONAL'] = df['TEMPO MÉDIO OPERACIONAL'].astype(str)
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, index=False)

# Função para garantir que a coluna 'TEMPO MÉDIO OPERACIONAL' esteja no formato timedelta para cálculos
def convert_to_timedelta_for_calculations(df):
    df['TEMPO MÉDIO OPERACIONAL'] = pd.to_timedelta(df['TEMPO MÉDIO OPERACIONAL'], errors='coerce')
    return df

# Função para garantir que a coluna 'DATA CRIAÇÃO DA TAREFA' esteja no formato de datetime
def convert_to_datetime_for_calculations(df):
    df['DATA CRIAÇÃO DA TAREFA'] = pd.to_datetime(df['DATA CRIAÇÃO DA TAREFA'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    return df

# Função para formatar timedelta no formato HH:MM:SS
def format_timedelta(td):
    if pd.isnull(td):
        return "0 min"
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes} min {seconds} sec"

# Função para calcular o TMO por dia
def calcular_tmo_por_dia(df):
    df['Dia'] = pd.to_datetime(df['DATA CRIAÇÃO DA TAREFA']).dt.date
    df_finalizados = df[df['SITUAÇÃO DA TAREFA'].isin(['Finalizada', 'Cancelado'])].copy()
    
    # Agrupando por dia
    df_tmo = df_finalizados.groupby('Dia').agg(
        Tempo_Total=('TEMPO MÉDIO OPERACIONAL', 'sum'),  # Soma total do tempo
        Total_Finalizados_Cancelados=('SITUAÇÃO DA TAREFA', 'count')  # Total de tarefas finalizadas ou canceladas
    ).reset_index()

    # Calcula o TMO (Tempo Médio Operacional)
    df_tmo['TMO'] = df_tmo['Tempo_Total'] / df_tmo['Total_Finalizados_Cancelados']
    
    # Formata o tempo médio no formato HH:MM:SS
    df_tmo['TMO'] = df_tmo['TMO'].apply(format_timedelta)
    return df_tmo[['Dia', 'TMO']]

# Função principal da dashboard
def dashboard():
    st.title("Dashboard de Produtividade")
    
    # Carregar dados acumulados do arquivo Excel do usuário logado
    usuario_logado = st.session_state.usuario_logado  # Obtém o usuário logado
    df_total = load_data(usuario_logado)  # Carrega dados específicos do usuário

    st.sidebar.image("https://finchsolucoes.com.br/img/eb28739f-bef7-4366-9a17-6d629cf5e0d9.png", width=100)
    st.sidebar.text('')

    # Sidebar para navegação
    st.sidebar.header("Navegação")
    opcao_selecionada = st.sidebar.selectbox("Escolha uma visão", ["Visão Geral", "Métricas Individuais", "Diário de Bordo"])

    # Upload de planilha na sidebar
    uploaded_file = st.sidebar.file_uploader("Carregar nova planilha", type=["xlsx"])

    if uploaded_file is not None:
        df_new = pd.read_excel(uploaded_file)
        df_total = pd.concat([df_total, df_new], ignore_index=True)
        save_data(df_total, usuario_logado)  # Atualiza a planilha específica do usuário
        st.sidebar.success(f'Arquivo "{uploaded_file.name}" carregado e processado com sucesso!')

    # Converte para timedelta e datetime apenas para operações temporárias
    df_total = convert_to_timedelta_for_calculations(df_total)
    df_total = convert_to_datetime_for_calculations(df_total)

    custom_colors = ['#ff571c', '#7f2b0e', '#4c1908']

    # Função para calcular TMO por dia
    df_tmo = calcular_tmo_por_dia(df_total)
    st.dataframe(df_tmo)

    # Verifica qual opção foi escolhida no dropdown
    if opcao_selecionada == "Visão Geral":
        st.header("Visão Geral")

        # Adiciona filtros de datas 
        min_date = df_total['DATA CRIAÇÃO DA TAREFA'].min().date() if not df_total.empty else datetime.today().date()
        max_date = df_total['DATA CRIAÇÃO DA TAREFA'].max().date() if not df_total.empty else datetime.today().date()

        col1, col2 = st.columns(2)
        with col1:
            data_inicial = st.date_input("Data Inicial", min_date)
        with col2:
            data_final = st.date_input("Data Final", max_date)

        if data_inicial > data_final:
            st.sidebar.error("A data inicial não pode ser posterior à data final!")

        df_total = df_total[(df_total['DATA CRIAÇÃO DA TAREFA'].dt.date >= data_inicial) & (df_total['DATA CRIAÇÃO DA TAREFA'].dt.date <= data_final)]

        total_finalizados = len(df_total[df_total['SITUAÇÃO DA TAREFA'] == 'Finalizada'])
        total_reclass = len(df_total[df_total['SITUAÇÃO DA TAREFA'] == 'Cancelado'])
        tempo_medio = (df_total[df_total['SITUAÇÃO DA TAREFA'] == 'Finalizada']['TEMPO MÉDIO OPERACIONAL'].sum() + df_total[df_total['SITUAÇÃO DA TAREFA'] == 'Cancelado']['TEMPO MÉDIO OPERACIONAL'].sum()) / (total_finalizados + total_reclass)

        # Verificar se há algum cadastro finalizado ou reclassificado para evitar divisão por zero
        if total_finalizados + total_reclass > 0:
            tempo_medio = (df_total[df_total['SITUAÇÃO DA TAREFA'] == 'Finalizada']['TEMPO MÉDIO OPERACIONAL'].sum() + 
                        df_total[df_total['SITUAÇÃO DA TAREFA'] == 'Cancelado']['TEMPO MÉDIO OPERACIONAL'].sum()) / (total_finalizados + total_reclass)
        else:
            tempo_medio = pd.Timedelta(seconds=0)  # Definir valor padrão para tempo médio como 0 segundos

        st.write(f"Total de Cadastros: {tempo_medio}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Cadastros", total_finalizados)
        col2.metric("Reclassificações", total_reclass)
        col3.metric("Tempo Médio por Cadastro", format_timedelta(tempo_medio))


        # Gráfico de pizza para o status
        st.subheader("Distribuição de Status")
        fig_status = px.pie(
            names=['Finalizada', 'Cancelado'],
            values=[total_finalizados, total_reclass],
            title='Distribuição de Status',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_status)

        # Gráfico de TMO por dia
        st.subheader("Tempo Médio de Operação (TMO) por Dia")
        df_tmo = calcular_tmo_por_dia(df_total)
        fig_tmo = px.bar(
            df_tmo,
            x='Dia',
            y='TMO',
            title='TMO por Dia (em minutos)',
            labels={'TMO': 'TMO (min)', 'Dia': 'Data'},
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_tmo)

        # Gráfico de ranking dinâmico
        st.subheader("Ranking Dinâmico")
        df_ranking = df_total.groupby('USUÁRIO QUE CONCLUIU A TAREFA').agg(
            Finalizado=('SITUAÇÃO DA TAREFA', lambda x: x[x == 'Finalizada'].count()),
            Cancelado=('SITUAÇÃO DA TAREFA', lambda x: x[x == 'Cancelado'].count())
        ).reset_index()
        df_ranking['Total'] = df_ranking['Finalizado'] + df_ranking['Cancelado']
        df_ranking = df_ranking.sort_values(by='Total', ascending=False).reset_index(drop=True)
        df_ranking.index += 1
        df_ranking.index.name = 'Posição'
        df_ranking = df_ranking.rename(columns={'USUÁRIO QUE CONCLUIU A TAREFA': 'Usuário', 'Finalizado': 'Finalizado', 'Cancelado': 'Cancelado'})
        st.dataframe(df_ranking.style.format({'Finalizado': '{:.0f}', 'Cancelado': '{:.0f}'}), width=1000)

    elif opcao_selecionada == "Diário de Bordo":
        diario()

    elif opcao_selecionada == "Métricas Individuais":
        st.header("Análise por Analista")
        # Adiciona filtros de datas 
        st.subheader("Filtro por Data")
        min_date = df_total['Próximo'].min().date() if not df_total.empty else datetime.today().date()
        max_date = df_total['Próximo'].max().date() if not df_total.empty else datetime.today().date()

        col1, col2 = st.columns(2)
        with col1:
            data_inicial = st.date_input("Data Inicial", min_date)
        with col2:
            data_final = st.date_input("Data Final", max_date)

        if data_inicial > data_final:
            st.error("A data inicial não pode ser posterior à data final!")

        df_total = df_total[(df_total['Próximo'].dt.date >= data_inicial) & (df_total['Próximo'].dt.date <= data_final)]
        analista_selecionado = st.selectbox('Selecione o analista', df_total['Usuário'].unique())
        df_analista = df_total[df_total['Usuário'] == analista_selecionado].copy()

        total_finalizados_analista = len(df_analista[df_analista['Status'] == 'FINALIZADO'])
        total_reclass_analista = len(df_analista[df_analista['Status'] == 'RECLASSIFICADO'])
        total_andamento_analista = len(df_analista[df_analista['Status'] == 'ANDAMENTO_PRE'])
        tempo_medio_analista = df_analista[df_analista['Status'] == 'FINALIZADO']['Tempo de Análise'].mean()

        tmo_equipe = df_total[df_total['Status'] == 'FINALIZADO']['Tempo de Análise'].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Cadastros", total_finalizados_analista)
        col2.metric("Reclassificações", total_reclass_analista)
        col3.metric("Andamentos", total_andamento_analista)
        if tempo_medio_analista is not None and tmo_equipe is not None:
            if tempo_medio_analista <= tmo_equipe:
                col4.metric(f"Tempo Médio por Cadastro", f"{format_timedelta(tempo_medio_analista)} {'🟢'}")
            else:
                col4.metric(f"Tempo Médio por Cadastro", f"{format_timedelta(tempo_medio_analista)} {'🔴'}")
        else:
            col4.metric(f"Tempo Médio por Cadastro", 'Nenhum dado encontrado')

        st.subheader(f"Carteiras Cadastradas por {analista_selecionado}")
        carteiras_analista = pd.DataFrame(df_analista['Carteira'].dropna().unique(), columns=['Carteiras'])
        st.write(carteiras_analista.to_html(index=False, justify='left', border=0), unsafe_allow_html=True)
        st.markdown("<style>table {width: 100%;}</style>", unsafe_allow_html=True)

        # Gráfico de pizza para o status do analista selecionado
        st.subheader(f"Distribuição de Status de {analista_selecionado}")
        fig_status_analista = px.pie(
            names=['Finalizado', 'Reclassificado', 'Andamento'],
            values=[total_finalizados_analista, total_reclass_analista, total_andamento_analista],
            title=f'Distribuição de Status - {analista_selecionado}',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_status_analista)

        # TMO por dia do analista
        st.subheader(f"Tempo Médio de Operacional (TMO) por Dia - {analista_selecionado}")
        df_tmo_analista = calcular_tmo_por_dia(df_analista)
        fig_tmo_analista = px.bar(
            df_tmo_analista,
            x='Dia',
            y='TMO',
            title=f'TMO por Dia de {analista_selecionado} (em minutos)',
            hover_name='Dia',
            hover_data=['TMO'],
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_tmo_analista)

        # Tabela de pontos de atenção
        st.subheader("Pontos de Atenção")
        pontos_de_atencao_analista = get_points_of_attention(df_analista)
        if not pontos_de_atencao_analista.empty:
            st.write(pontos_de_atencao_analista[['Protocolo', 'Tempo de Análise', 'Próximo']].assign(
                **{'Tempo de Análise': pontos_de_atencao_analista['Tempo de Análise'].apply(format_timedelta)}
            ).to_html(index=False, justify='left'), unsafe_allow_html=True)
        else:
            st.write("Nenhum ponto de atenção identificado para este analista.")    

    # # Botão para salvar a planilha atualizada
    # if st.sidebar.button("Salvar Dados"):
    #     save_data(df_total, usuario_logado)  # Salva dados específicos do usuário
    #     st.sidebar.success("Dados salvos com sucesso!")

    if st.sidebar.button("Logout"):
        st.session_state.logado = False
        st.session_state.usuario_logado = None
        st.sidebar.success("Desconectado com sucesso!")
        st.rerun()  # Volta para a tela de login

# Para que a função dashboard seja chamada no arquivo principal
if __name__ == "__main__":
    dashboard()