import streamlit as st
from services.database import buscar_leads_filtrados
from views.components.cards import renderizar_card_lead, calcular_temperatura

def exibir_painel_geral():
    st.header("📋 Gestão de Atendimentos")
    u = st.session_state.user_data
    leads = buscar_leads_filtrados(u)
    
    if not leads:
        st.info("Nenhum lead encontrado para o seu acesso.")
        return

    # --- FILTROS INTELIGENTES ---
    with st.container():
        c_f1, c_f2, c_f3 = st.columns([2, 1, 1])
        
        with c_f1:
            busca = st.text_input("🔍 Buscar por nome...", placeholder="Digite para filtrar...")
        
        with c_f2:
            # Adicionado "Perdido" à lista de opções
            status_opcoes = ["Pendente", "Em Negociação", "Urgente", "Finalizado", "Perdido"]
            # O default continua sendo apenas os ativos para manter o foco
            filtro_status = st.multiselect("Status", status_opcoes, default=["Pendente", "Em Negociação", "Urgente"])
        
        with c_f3:
            temp_opcoes = ["Todos", "🔥 Quente", "🌤️ Morno", "❄️ Gelado"]
            filtro_temp = st.selectbox("Temperatura", temp_opcoes)
    
    st.divider()

    # --- MÉTRICAS RÁPIDAS (OPCIONAL) ---
    # Mostra quantos leads estão "Gelados" e precisam de atenção
    leads_gelados = [l for l in leads if "Gelado" in calcular_temperatura(l.get('data_criacao'))[0]]
    if leads_gelados and filtro_temp == "Todos":
        st.warning(f"⚠️ Você tem {len(leads_gelados)} leads **Gelados** precisando de atenção!")

    # --- LOOP DE RENDERIZAÇÃO ---
    for lead in leads:
        # 1. Lógica de Filtro de Status e Nome
        match_status = lead['status'] in filtro_status
        match_nome = busca.lower() in lead['nome'].lower()
        
        # 2. Lógica de Filtro de Temperatura
        label_temp, _ = calcular_temperatura(lead.get('data_criacao'))
        match_temp = (filtro_temp == "Todos") or (filtro_temp in label_temp)

        if match_status and match_nome and match_temp:
            renderizar_card_lead(lead, status_opcoes)