import streamlit as st
from login import login
from dashboard import dashboard

st.set_page_config(
    page_title="Dashboard",  # Título da aba do navegador
    page_icon="🟠",  # Favicon, você pode usar um emoji ou um caminho para um arquivo .ico
    layout="wide",  
    initial_sidebar_state="expanded"  # Barra lateral sempre expandida# Layout da página, pode ser "wide" ou "centered"]bac
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # Tema padrão

# Verifica se o usuário está logado
if 'logado' not in st.session_state:
    st.session_state.logado = False

# Se não estiver logado, mostra o formulário de login
if not st.session_state.logado:
    if login():
        st.rerun()  # Reinicia a aplicação para carregar a dashboard
else:
    # Se estiver logado, mostra a dashboard
    dashboard()
