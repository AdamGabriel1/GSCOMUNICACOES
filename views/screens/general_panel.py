import streamlit as st
from services.database import buscar_leads_filtrados
from views.components.cards import renderizar_card_lead

def exibir_painel_geral():
    st.header("📋 Gestão de Atendimentos")
    u = st.session_state.user_data
    leads = buscar_leads_filtrados(u)
    
    if not leads:
        st.info("Nenhum lead encontrado para o seu acesso.")
        return

    # Filtros Superiores
    c_f1, c_f2 = st.columns([2, 1])
    with c_f1:
        busca = st.text_input("🔍 Buscar por nome...", placeholder="Digite para filtrar...")
    with c_f2:
        status_opcoes = ["Pendente", "Em Negociação", "Urgente", "Finalizado"]
        filtro_status = st.multiselect("Filtrar Status", status_opcoes, default=["Pendente", "Em Negociação", "Urgente"])

    st.divider()

    for lead in leads:
        if lead['status'] in filtro_status and (busca.lower() in lead['nome'].lower()):
            # Aqui chamamos o componente isolado
            renderizar_card_lead(lead, status_opcoes)