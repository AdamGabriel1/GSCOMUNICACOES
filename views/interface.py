import streamlit as st
# Importando as telas desmembradas
from views.screens.admin_screen import exibir_painel_admin
from views.screens.general_panel import exibir_painel_geral
from views.screens.stats_screen import exibir_estatisticas
from views.screens.forms_screen import exibir_novo_lead

def renderizar_sidebar():
    """Mantemos aqui por ser o controlador de navegação"""
    u = st.session_state.user_data
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=50)
    st.sidebar.title("GS COMUNICAÇÕES")
    st.sidebar.markdown(f"👤 **{u['nome']}**")
    st.sidebar.caption(f"🏢 Empresa: {u['empresa_id'].upper()}")
    
    st.sidebar.divider()
    menu = ["📊 Painel Geral", "➕ Novo Lead", "📈 Estatísticas"]
    if u['nivel'] in ['super', 'admin']:
        menu.append("👑 Administração")
        
    aba = st.sidebar.radio("Navegação", menu)
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.user_data = None
        st.rerun()
    return aba