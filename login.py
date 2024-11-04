import streamlit as st

# Dicionário com usuários e senhas
usuarios = {"usuario1": "senha1", "usuario2": "senha2", "viviane@bv": "f1nch"}

# Função para autenticar usuário
def autenticar(usuario, senha):
    return usuario in usuarios and usuarios[usuario] == senha

def login():
    st.logo("https://finchsolucoes.com.br/img/eb28739f-bef7-4366-9a17-6d629cf5e0d9.png")
    st.sidebar.header("Login")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")

    st.sidebar.info("Para acessar a Dashbord faça Login com Usuário e Senha.")   

    if st.sidebar.button("Entrar"):
        if autenticar(usuario, senha):
            st.session_state.logado = True
            st.session_state.usuario_logado = usuario  # Armazena o usuário logado
            st.sidebar.success("Login bem-sucedido!")
            return True  # Login bem-sucedido
        else:
            st.sidebar.error("Usuário ou senha incorretos.")
    return False  # Login falhou
    
