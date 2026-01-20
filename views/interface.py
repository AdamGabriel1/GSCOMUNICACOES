import streamlit as st
# Importando as telas das subpastas para que o Agrupador funcione
from views.screens.admin_screen import exibir_painel_admin
from views.screens.general_panel import exibir_painel_geral
from views.screens.stats_screen import exibir_estatisticas
from views.screens.forms_screen import exibir_novo_lead

def renderizar_sidebar():
    """
    Renderiza a barra lateral, controla o estado da sessão 
    e retorna a aba selecionada para o roteamento.
    """
    u = st.session_state.user_data
    
    # --- CABEÇALHO DA SIDEBAR ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=50)
    st.sidebar.title("GS COMUNICAÇÕES")
    
    # Informações do Usuário
    st.sidebar.markdown(f"👤 **{u['nome']}**")
    st.sidebar.caption(f"🏢 Empresa: {u['empresa_id'].upper()}")
    st.sidebar.caption(f"🛡️ Nível: {u['nivel'].capitalize()}")
    
    st.sidebar.divider()
    
    # --- MENU DE NAVEGAÇÃO ---
    menu = ["📊 Painel Geral", "➕ Novo Lead", "📈 Estatísticas"]
    
    # Lógica de Permissão (Nível de Acesso)
    if u['nivel'] in ['super', 'admin']:
        menu.append("👑 Administração")
        
    aba = st.sidebar.radio("Navegação", menu)
    
    # --- RODAPÉ E LOGOUT ---
    st.sidebar.divider()
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        # Limpa o estado da sessão
        st.session_state.autenticado = False
        st.session_state.user_data = None
        st.session_state.tela = "login" # Garante que volte para o login
        st.rerun()
        
    return aba