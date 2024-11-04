import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd

# Função para carregar as anotações do diário de bordo do usuário a partir de um arquivo .txt
def load_diario(usuario):
    file_path = f'diario_bordo_{usuario}.txt'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            anotacoes = file.readlines()
    else:
        anotacoes = []
    return anotacoes

# Função para salvar uma nova anotação no arquivo .txt do usuário
def save_anotacao(usuario, anotacao):
    file_path = f'diario_bordo_{usuario}.txt'
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - {anotacao}\n")

# Função para salvar o tempo de indisponibilidade
def save_indisponibilidade(usuario, inicio, fim, duracao):
    file_path = f'indisponibilidade_{usuario}.txt'
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"{inicio} - {fim} | Duração: {duracao}\n")

# Função para exibir e adicionar anotações no diário de bordo
def diario():
    usuario_logado = st.session_state.usuario_logado  # Obtém o usuário logado

    st.header("Diário de Bordo")
    

    # Carregar anotações anteriores
    anotacoes = load_diario(usuario_logado)

    # Área para adicionar uma nova anotação
    st.subheader("Nova Anotação")
    nova_anotacao = st.text_area("Escreva sua anotação aqui...")

    if st.button("Salvar Anotação"):
        if nova_anotacao.strip():
            save_anotacao(usuario_logado, nova_anotacao)
            st.success("Anotação salva com sucesso!")
            st.rerun()  # Recarrega a página para exibir a nova anotação
        else:
            st.error("A anotação não pode estar vazia!")

    # Exibir anotações anteriores
    if anotacoes:
        st.subheader("Anotações anteriores")
        col1, col2, col3 = st.columns(3)
        for i, anotacao in enumerate(anotacoes):
            if i % 3 == 0:
                col1.info(anotacao.strip())
            elif i % 3 == 1:
                col2.info(anotacao.strip())
            else:
                col3.info(anotacao.strip())
    else:
        st.info("Nenhuma anotação encontrada.")

    
    # Área para registrar tempo de indisponibilidade com timer
    st.subheader("Registrar Indisponibilidade do Sistema (com timer)")
    
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    
    if st.button("Iniciar Timer"):
        st.session_state.start_time = datetime.now()
    
    if st.session_state.start_time:
        tempo_passado = datetime.now() - st.session_state.start_time
        st.metric("Tempo passado", f"{tempo_passado.total_seconds() / 3600:.2f} horas")
        if st.button("Parar Timer"):
            save_indisponibilidade(usuario_logado, st.session_state.start_time.strftime('%H:%M'), datetime.now().strftime('%H:%M'), str(tempo_passado))
            st.success("Tempo de indisponibilidade salvo com sucesso!")
            st.session_state.start_time = None

    # # Área para registrar tempo de indisponibilidade
    # st.subheader("Registrar Indisponibilidade do Sistema")
    
    # inicio = st.time_input("Hora de Início da Indisponibilidade:")
    # fim = st.time_input("Hora de Fim da Indisponibilidade:")

    # if st.button("Salvar Indisponibilidade"):
    #     if inicio and fim:
    #         # Converte os horários para objetos datetime
    #         now = datetime.now()
    #         inicio_dt = datetime.combine(now.date(), inicio)
    #         fim_dt = datetime.combine(now.date(), fim)
            
    #         # Verifica se o fim é após o início
    #         if fim_dt > inicio_dt:
    #             duracao = fim_dt - inicio_dt
    #             save_indisponibilidade(usuario_logado, inicio_dt.strftime('%H:%M'), fim_dt.strftime('%H:%M'), str(duracao))
    #             st.success("Indisponibilidade salva com sucesso!")
    #             st.rerun()  # Recarrega a página para atualizar a informação
    #         else:
    #             st.error("A hora de fim deve ser após a hora de início.")
    #     else:
    #         st.error("Ambos os campos de hora devem ser preenchidos.")

    # # Calcular e exibir o total de horas de indisponibilidade
    # total_indisponibilidade = timedelta()  # Inicializa o total
    # registros = []  # Lista para armazenar os registros

    # file_path = f'indisponibilidade_{usuario_logado}.txt'
    # if os.path.exists(file_path):
    #     with open(file_path, 'r', encoding='utf-8') as file:
    #         for line in file:
    #             parts = line.strip().split('| Duração: ')
    #             if len(parts) == 2:
    #                 duracao_str = parts[1].strip()  # Obtém a duração
    #                 # A duração já está no formato de timedelta, então usamos isso diretamente
    #                 try:
    #                     # Extraindo a duração como timedelta
    #                     h, m, s = map(int, duracao_str.split(':'))
    #                     total_indisponibilidade += timedelta(hours=h, minutes=m, seconds=s)

    #                     # Adiciona o registro à lista
    #                     registros.append({
    #                         'Início': parts[0].strip(),
    #                         'Duração': duracao_str
    #                     })
    #                 except ValueError:
    #                     st.warning(f"Formato de duração inválido na linha: {line.strip()}")  # Informa se o formato estiver incorreto

    # st.subheader("Total de Indisponibilidade")
    # if total_indisponibilidade.total_seconds() > 0:  # Verifica se o total é maior que zero
    #     st.write(f"Total de Indisponibilidade: {total_indisponibilidade}")
    # else:
    #     st.write("Nenhuma indisponibilidade registrada.")

    # # Exibir registros em formato de tabela
    # if registros:
    #     st.subheader("Registros de Indisponibilidade")
    #     df_registros = pd.DataFrame(registros)
    #     st.table(df_registros)
    # else:
    #     st.info("Nenhum registro de indisponibilidade encontrado.")

