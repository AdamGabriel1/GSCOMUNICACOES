import streamlit as st
import urllib.parse
import pandas as pd
from services.database import atualizar_status_rest, eliminar_documento

def renderizar_card_lead(lead, status_opcoes):
    """
    Componente reutilizável para exibir um lead.
    Encapsula toda a lógica de cores, botões e expansores.
    """
    
    # 1. Lógica de Cores e Estilo
    cor_classe = {
        "Urgente": "status-urgente",
        "Em Negociação": "status-negociacao",
        "Finalizado": "status-finalizado"
    }.get(lead['status'], "status-pendente")
    
    icone = "🔥" if lead['status'] == "Urgente" else "👤"

    # 2. Renderização do HTML do Card (Estilo definido no main.py)
    st.markdown(f"""
        <div class="lead-card {cor_classe}">
            <div style="font-size: 1.2rem; font-weight: bold;">{icone} {lead['nome']}</div>
            <div style="font-size: 0.85rem; text-transform: uppercase; font-weight: 600; opacity: 0.8;">
                {lead['status']} | Vendedor: {lead.get('vendedor_id', 'N/A')}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3. Expander com Detalhes e Ações Rápidas
    with st.expander(f"Gerenciar {lead['nome']}"):
        col1, col2, col3 = st.columns([2, 1.5, 1])
        
        with col1:
            st.write(f"**WhatsApp:** {lead['telefone']}")
            st.write(f"**Notas:** {lead.get('obs', 'Sem observações')}")
            try:
                dt = pd.to_datetime(lead['data_criacao']).strftime('%d/%m/%Y %H:%M')
                st.caption(f"📅 Criado em: {dt}")
            except:
                pass

        with col2:
            # Seleção de Status (Atualiza instantaneamente)
            novo_st = st.selectbox(
                "Mudar Status", 
                status_opcoes, 
                index=status_opcoes.index(lead['status']),
                key=f"st_{lead['id']}"
            )
            if novo_st != lead['status']:
                if atualizar_status_rest(lead['id'], novo_st):
                    st.toast(f"Status de {lead['nome']} atualizado!")
                    st.rerun()

        with col3:
            # Botão WhatsApp
            msg = f"Olá {lead['nome']}, aqui é da GS COMUNICAÇÕES!"
            link_zap = f"https://wa.me/{lead['telefone']}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-zap">WHATSAPP</a>', unsafe_allow_html=True)
            
            st.write("") # Espaçamento
            
            # Botão Excluir
            if st.button("🗑️ Excluir", key=f"del_{lead['id']}", use_container_width=True):
                if eliminar_documento("leads", lead['id']):
                    st.rerun()