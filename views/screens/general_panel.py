import streamlit as st
import urllib.parse
from services.database import buscar_leads_filtrados, atualizar_status_rest, eliminar_documento
import pandas as pd

def exibir_painel_geral():
    st.header("📋 Gestão de Atendimentos")
    u = st.session_state.user_data
    leads = buscar_leads_filtrados(u)
    
    if not leads:
        st.info("Nenhum lead encontrado.")
        return

    # Filtros
    c_f1, c_f2 = st.columns([2, 1])
    with c_f1:
        busca = st.text_input("🔍 Buscar por nome...")
    with c_f2:
        status_opcoes = ["Pendente", "Em Negociação", "Urgente", "Finalizado"]
        filtro_status = st.multiselect("Status", status_opcoes, default=["Pendente", "Em Negociação", "Urgente"])

    st.divider()

    for lead in leads:
        if lead['status'] in filtro_status and (busca.lower() in lead['nome'].lower()):
            renderizar_card_lead(lead, status_opcoes)

def renderizar_card_lead(lead, status_opcoes):
    """Função interna ou importada de components/cards.py"""
    cor_classe = {"Urgente": "status-urgente", "Em Negociação": "status-negociacao", "Finalizado": "status-finalizado"}.get(lead['status'], "status-pendente")
    icone = "🔥" if lead['status'] == "Urgente" else "👤"

    st.markdown(f"""
        <div class="lead-card {cor_classe}">
            <div style="font-size: 1.2rem; font-weight: bold;">{icone} {lead['nome']}</div>
            <div style="font-size: 0.85rem; opacity: 0.8;">{lead['status']} | {lead.get('vendedor_id', 'N/A')}</div>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("Ações"):
        col1, col2, col3 = st.columns([2, 1.5, 1])
        with col1:
            st.write(f"**WhatsApp:** {lead['telefone']}")
        with col2:
            novo_st = st.selectbox("Status", status_opcoes, index=status_opcoes.index(lead['status']), key=f"st_{lead['id']}")
            if novo_st != lead['status']:
                if atualizar_status_rest(lead['id'], novo_st): st.rerun()
        with col3:
            link_zap = f"https://wa.me/{lead['telefone']}?text=Olá"
            st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-zap">WHATSAPP</a>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{lead['id']}"):
                if eliminar_documento("leads", lead['id']): st.rerun()