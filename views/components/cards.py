import streamlit as st
import pandas as pd
import urllib.parse
from services.database import atualizar_status_rest, eliminar_documento

def renderizar_card_lead(lead, status_opcoes):
    # Definição de Cores
    cor_classe = {
        "Urgente": "status-urgente",
        "Em Negociação": "status-negociacao",
        "Finalizado": "status-finalizado"
    }.get(lead['status'], "status-pendente")
    
    icone = "🔥" if lead['status'] == "Urgente" else "👤"

    # Renderização visual
    st.markdown(f"""
        <div class="lead-card {cor_classe}">
            <div style="font-size: 1.2rem; font-weight: bold;">{icone} {lead['nome']}</div>
            <div style="font-size: 0.85rem; text-transform: uppercase; font-weight: 600; opacity: 0.8;">
                {lead['status']} | Responsável: {lead.get('vendedor_id', 'N/A')}
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("Ver Detalhes e Ações"):
        col1, col2, col3 = st.columns([2, 1.5, 1])
        
        with col1:
            st.write(f"**WhatsApp:** {lead['telefone']}")
            st.write(f"**Notas:** {lead.get('obs', 'Sem observações')}")
            try:
                dt = pd.to_datetime(lead['data_criacao']).strftime('%d/%m/%Y %H:%M')
                st.caption(f"📅 Registrado em: {dt}")
            except: pass

        with col2:
            novo_st = st.selectbox("Atualizar Status", status_opcoes, 
                                 index=status_opcoes.index(lead['status']),
                                 key=f"st_{lead['id']}")
            if novo_st != lead['status']:
                if atualizar_status_rest(lead['id'], novo_st):
                    st.rerun()

        with col3:
            msg = f"Olá {lead['nome']}, aqui é da GS COMUNICAÇÕES!"
            link_zap = f"https://wa.me/{lead['telefone']}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-zap">WHATSAPP</a>', unsafe_allow_html=True)
            
            if st.button("🗑️ Excluir", key=f"del_{lead['id']}", use_container_width=True):
                if eliminar_documento("leads", lead['id']):
                    st.rerun()