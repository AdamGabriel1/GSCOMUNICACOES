import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime, timezone
from services.database import atualizar_status_rest, eliminar_documento, registrar_perda_lead

def calcular_temperatura(data_criacao_str):
    """Calcula a temperatura com base na idade do lead"""
    try:
        # Converte a string do Firebase para objeto datetime
        data_criacao = pd.to_datetime(data_criacao_str).tz_localize(None)
        agora = datetime.now()
        diferenca = agora - data_criacao
        horas = diferenca.total_seconds() / 3600

        if horas <= 24:
            return "🔥 Quente", "#ff4b4b" # Vermelho
        elif horas <= 72:
            return "🌤️ Morno", "#ffa500"  # Laranja
        else:
            return "❄️ Gelado", "#00f2ff" # Azul ciano
    except:
        return "⚪ Novo", "#ccc"

def renderizar_card_lead(lead, status_opcoes):
    # Calcula temperatura
    temp_label, temp_cor = calcular_temperatura(lead.get('data_criacao'))
    
    # Cores de status (Borda lateral)
    cor_classe = {
        "Urgente": "status-urgente",
        "Em Negociação": "status-negociacao",
        "Finalizado": "status-finalizado"
    }.get(lead['status'], "status-pendente")

    # Renderização visual com a temperatura
    st.markdown(f"""
        <div class="lead-card {cor_classe}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 1.2rem; font-weight: bold;">👤 {lead['nome']}</div>
                <div style="background: {temp_cor}22; color: {temp_cor}; padding: 2px 8px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; border: 1px solid {temp_cor};">
                    {temp_label}
                </div>
            </div>
            <div style="font-size: 0.85rem; text-transform: uppercase; font-weight: 600; opacity: 0.8; margin-top: 5px;">
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
            msg = f"Olá {lead['nome']}, aqui é da GS!"
            link_zap = f"https://wa.me/{lead['telefone']}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-zap">WHATSAPP</a>', unsafe_allow_html=True)
            
            st.divider()
            
            # Opção de Perda de Lead (Substituindo ou complementando a exclusão)
            with st.popover("❌ Perder", use_container_width=True):
                st.write("Por que perdeu este lead?")
                motivo_selecionado = st.selectbox(
                    "Selecione o motivo:", 
                    ["Preço Alto", "Não Atendeu", "Comprou Concorrente", "Sem Interesse", "Outros"],
                    key=f"sel_motivo_{lead['id']}"
                )
                
                if st.button("Confirmar Perda", key=f"btn_confirm_perda_{lead['id']}", type="primary", use_container_width=True):
                    with st.spinner("Salvando..."):
                        sucesso = registrar_perda_lead(lead['id'], motivo_selecionado)
                        if sucesso:
                            st.toast(f"Lead {lead['nome']} atualizado para Perdido!", icon="✅")
                            # Pequena pausa para o usuário ver o toast antes do rerun
                            import time
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Erro ao salvar no banco de dados.")