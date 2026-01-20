import streamlit as st
import pandas as pd
import urllib.parse
from database import buscar_leads_filtrados, eliminar_documento, salvar_no_firebase, atualizar_status_rest
from database import buscar_todos_usuarios, buscar_todas_empresas, resetar_senha_usuario, registrar_perda_lead
from datetime import datetime, timezone, timedelta
import plotly.express as px

# --- FUNÇÕES AUXILIARES DE INTELIGÊNCIA ---

def calcular_temperatura(data_criacao):
    """Retorna o ícone e a cor baseada na idade do lead (Lead Scoring)"""
    try:
        agora = datetime.now(timezone.utc)
        data_c = pd.to_datetime(data_criacao)
        # Garante que data_c tenha fuso horário para comparação
        if data_c.tzinfo is None:
            data_c = data_c.tz_localize(timezone.utc)
        
        diff = agora - data_c

        if diff < timedelta(hours=2): return "🔥", "#ff4b4b"  # Quente
        if diff < timedelta(hours=24): return "⚡", "#ffa500" # Morno
        return "❄️", "#00f2ff"                               # Gelado
    except:
        return "👤", "#ccc"

def exibir_alertas_e_agendamentos(leads):
    """Sistema de Alerta de Leads Parados"""
    agora = datetime.now(timezone.utc).date()
    leads_atrasados = 0
    
    for l in leads:
        if l['status'] == "Pendente":
            try:
                data_c = pd.to_datetime(l['data_criacao']).date()
                if (agora - data_c).days >= 1:
                    leads_atrasados += 1
            except: continue
                
    if leads_atrasados > 0:
        st.error(f"🚨 **Alerta de Leads Parados:** Existem {leads_atrasados} leads sem atendimento há mais de 24h!")

# --- TELAS PRINCIPAIS ---

def renderizar_sidebar():
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
        st.rerun()
    return aba

def exibir_painel_geral():
    st.header("📋 Gestão de Atendimentos")
    u = st.session_state.user_data
    leads = buscar_leads_filtrados(u)
    
    if not leads:
        st.info("Nenhum lead encontrado.")
        return

    # Ativa Alertas Automáticos
    exibir_alertas_e_agendamentos(leads)

    # Filtros
    c_f1, c_f2 = st.columns([2, 1])
    busca = c_f1.text_input("🔍 Buscar lead...", placeholder="Nome do cliente")
    status_opcoes = ["Pendente", "Em Negociação", "Urgente", "Finalizado"]
    filtro_status = c_f2.multiselect("Filtrar Status", status_opcoes, default=["Pendente", "Em Negociação", "Urgente"])

    st.divider()

    for lead in leads:
        if lead['status'] in filtro_status and (busca.lower() in lead['nome'].lower()):
            
            # Lógica Visual
            cor_classe = {
                "Urgente": "status-urgente",
                "Em Negociação": "status-negociacao",
                "Finalizado": "status-finalizado"
            }.get(lead['status'], "status-pendente")
            
            temp_icone, temp_cor = calcular_temperatura(lead['data_criacao'])

            # Card Principal
            st.markdown(f"""
                <div class="lead-card {cor_classe}" style="border-right: 8px solid {temp_cor} !important;">
                    <div class="lead-title">{temp_icone} {lead['nome']}</div>
                    <div class="lead-status">{lead['status']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Ações
            with st.expander("🔍 Detalhes e Conversa"):
                col1, col2, col3 = st.columns([2, 1.5, 1])
                
                with col1:
                    st.write(f"**WhatsApp:** {lead['telefone']}")
                    st.info(f"📝 {lead.get('obs', 'Sem observações')}")
                
                with col2:
                    novo_st = st.selectbox("Mudar Status", status_opcoes, 
                                         index=status_opcoes.index(lead['status']), 
                                         key=f"st_{lead['id']}")
                    if novo_st != lead['status']:
                        if atualizar_status_rest(lead['id'], novo_st): st.rerun()
                
                with col3:
                    msg = urllib.parse.quote(f"Olá {lead['nome']}, tudo bem?")
                    link = f"https://wa.me/{lead['telefone']}?text={msg}"
                    st.markdown(f'<a href="{link}" target="_blank" class="btn-zap">WHATSAPP</a>', unsafe_allow_html=True)

            with st.expander("⚙️ Opções Avançadas"):
                c_adv1, c_adv2 = st.columns(2)
                with c_adv1:
                    motivo = st.selectbox("Motivo da Perda", ["Preço", "Concorrência", "Sem Resposta", "Outro"], key=f"lp_{lead['id']}")
                    if st.button("❌ Marcar como Perdido", key=f"btn_p_{lead['id']}", use_container_width=True):
                        if registrar_perda_lead(lead['id'], motivo): st.rerun()
                with c_adv2:
                    if st.button("🗑️ Excluir Definitivamente", key=f"del_{lead['id']}", use_container_width=True):
                        if eliminar_documento("leads", lead['id']): st.rerun()

def exibir_estatisticas():
    st.header("📈 Relatórios e Performance")
    u = st.session_state.user_data
    leads = buscar_leads_filtrados(u)
    
    if not leads:
        st.info("Aguardando dados para gerar gráficos.")
        return

    df = pd.DataFrame(leads)
    df['data_criacao'] = pd.to_datetime(df['data_criacao'])
    df['data_dia'] = df['data_criacao'].dt.date

    # Filtro de Período
    periodo = st.selectbox("Filtrar Período", ["Tudo", "Hoje", "7 Dias", "30 Dias"], index=0)
    
    # Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Leads", len(df))
    m2.metric("Conversão", f"{(len(df[df['status']=='Finalizado'])/len(df)*100):.1f}%")
    m3.metric("Perdidos", len(df[df['status']=='Perdido']) if 'status' in df else 0)

    st.divider()

    # Gráfico de Evolução
    st.subheader("📅 Entrada de Leads por Dia")
    evolucao = df.groupby('data_dia').size()
    st.line_chart(evolucao, color="#0ea5e9")

    # Gráficos de Distribuição
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("📊 Distribuição de Status")
        st.bar_chart(df['status'].value_counts(), color="#25D366")
    with g2:
        st.subheader("🏆 Ranking de Vendedores")
        st.bar_chart(df['vendedor_id'].value_counts(), color="#f59e0b")

    # Relatório de Perdas (Lead Loss)
    if 'motivo_perda' in df.columns:
        st.subheader("📉 Motivos de Perda")
        perdas = df['motivo_perda'].value_counts()
        if not perdas.empty:
            fig = px.pie(values=perdas.values, names=perdas.index, hole=.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig)

def exibir_novo_lead():
    st.header("➕ Cadastrar Novo Lead")
    u = st.session_state.user_data
    with st.form("form_novo"):
        nome = st.text_input("Nome do Cliente")
        tel = st.text_input("WhatsApp")
        obs = st.text_area("Notas")
        if st.form_submit_button("Salvar Lead"):
            if nome and tel:
                dados = {"nome": nome, "telefone": tel, "status": "Pendente", "obs": obs, 
                         "empresa_id": u['empresa_id'], "vendedor_id": u['email']}
                if salvar_no_firebase("leads", dados):
                    st.success("Lead salvo!")
                    st.balloons()
            else: st.warning("Preencha os campos obrigatórios.")

def exibir_painel_admin():
    u_logado = st.session_state.user_data
    st.header("👑 Administração")
    
    if u_logado['nivel'] == 'super':
        st.subheader("🏢 Gestão de Empresas")
        for emp in buscar_todas_empresas():
            with st.expander(f"Empresa: {emp['razao']}"):
                st.write(f"ID: {emp['id_empresa']}")
                if st.button("Remover Empresa", key=f"re_{emp['id']}"):
                    if eliminar_documento("empresas", emp['id']): st.rerun()

    st.subheader("👥 Usuários da Unidade")
    for user in buscar_todos_usuarios(u_logado):
        with st.expander(f"{user['nome']} ({user['nivel']})"):
            nova_p = st.text_input("Nova Senha", type="password", key=f"p_{user['id']}")
            if st.button("Atualizar Senha", key=f"up_{user['id']}"):
                from security import criptografar_senha
                if resetar_senha_usuario(user['id'], criptografar_senha(nova_p)):
                    st.success("Senha alterada!")
