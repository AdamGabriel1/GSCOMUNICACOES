import streamlit as st
import pandas as pd
import urllib.parse
from database import buscar_leads_filtrados, eliminar_documento, salvar_no_firebase, atualizar_status_rest

def renderizar_sidebar():
    """Renderiza a barra lateral e retorna a aba selecionada"""
    u = st.session_state.user_data
    
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=50)
    st.sidebar.title("GS COMUNICAÇÕES")
    st.sidebar.markdown(f"👤 **{u['nome']}**")
    st.sidebar.caption(f"🏢 Empresa: {u['empresa_id'].upper()}")
    st.sidebar.caption(f"🛡️ Nível: {u['nivel'].capitalize()}")
    
    st.sidebar.divider()
    
    menu = ["📊 Painel Geral", "➕ Novo Lead", "📈 Estatísticas"]
    aba = st.sidebar.radio("Navegação", menu)
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.user_data = None
        st.rerun()
        
    return aba

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

    # Loop de Leads
    for lead in leads:
        # Lógica de Filtro em Memória
        if lead['status'] in filtro_status and (busca.lower() in lead['nome'].lower()):
            
            # Definição de Cores para o Card
            cor_classe = {
                "Urgente": "status-urgente",
                "Em Negociação": "status-negociacao",
                "Finalizado": "status-finalizado"
            }.get(lead['status'], "status-pendente")
            
            icone = "🔥" if lead['status'] == "Urgente" else "👤"

            # Renderização do Card (HTML definido no main.py)
            st.markdown(f"""
                <div class="lead-card {cor_classe}">
                    <div style="font-size: 1.2rem; font-weight: bold;">{icone} {lead['nome']}</div>
                    <div style="font-size: 0.85rem; text-transform: uppercase; font-weight: 600; opacity: 0.8;">
                        {lead['status']} | Responsável: {lead.get('vendedor_id', 'N/A')}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Detalhes e Ações
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

def exibir_novo_lead():
    st.header("➕ Cadastrar Novo Lead")
    u = st.session_state.user_data
    
    with st.form("form_novo_lead", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome do Cliente")
        tel = c2.text_input("WhatsApp (Ex: 5511999999999)")
        status = st.selectbox("Status Inicial", ["Pendente", "Em Negociação", "Urgente"])
        obs = st.text_area("Observações Adicionais")
        
        if st.form_submit_button("✅ Salvar Lead"):
            if nome and tel:
                dados = {
                    "nome": nome,
                    "telefone": tel,
                    "status": status,
                    "obs": obs,
                    "empresa_id": u['empresa_id'],
                    "vendedor_id": u['email']
                }
                if salvar_no_firebase("leads", dados):
                    st.success("Lead cadastrado com sucesso!")
                    st.balloons()
                else:
                    st.error("Erro ao salvar no banco de dados.")
            else:
                st.warning("Por favor, preencha Nome e Telefone.")

def exibir_estatisticas():
    st.header("📈 Relatórios de Desempenho")
    u = st.session_state.user_data
    leads = buscar_leads_filtrados(u)
    
    if not leads:
        st.info("Dados insuficientes para gerar relatórios.")
        return

    df = pd.DataFrame(leads)
    
    # Métricas Principais
    m1, m2, m3 = st.columns(3)
    total = len(df)
    finalizados = len(df[df['status'] == 'Finalizado'])
    taxa = (finalizados / total * 100) if total > 0 else 0
    
    m1.metric("Total de Leads", total)
    m2.metric("Ativos", len(df[df['status'] != 'Finalizado']))
    m3.metric("Conversão", f"{taxa:.1f}%")

    st.divider()

    # Gráficos
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Distribuição por Status")
        st.bar_chart(df['status'].value_counts(), color="#25D366")
    
    with g2:
        st.subheader("Leads por Vendedor")
        # Mostra performance por vendedor (Útil para Admins)
        st.bar_chart(df['vendedor_id'].value_counts(), color="#0ea5e9")

    # Opção de download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Base de Dados (CSV)", csv, "leads_gs.csv", "text/csv")
