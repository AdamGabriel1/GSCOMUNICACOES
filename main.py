import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. Conexão Segura com Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("chave-firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Configuração da Página
st.set_page_config(page_title="GSCOMUNICAÇÕES | CRM", page_icon="📞", layout="wide")

# Estilização CSS Avançada
st.markdown("""
    <style>
    /* Estilo Global */
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; }
    
    /* Badge de Status */
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; }
    .status-urgente { background-color: #fee2e2; color: #dc2626; }
    .status-pendente { background-color: #fef3c7; color: #d97706; }
    .status-negociacao { background-color: #dcfce7; color: #16a34a; }
    
    /* Botão WhatsApp */
    .btn-zap {
        background-color: #25D366;
        color: white !important;
        padding: 12px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        transition: 0.3s;
    }
    .btn-zap:hover { background-color: #128C7E; transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def buscar_dados():
    leads_ref = db.collection("leads").order_by("data_criacao", direction=firestore.Query.DESCENDING).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in leads_ref]

# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=60)
st.sidebar.title("GS COMUNICAÇÕES")
st.sidebar.markdown("---")

aba = st.sidebar.radio("Navegação", ["📊 Painel Geral", "➕ Novo Lead", "📈 Relatórios"])

# Filtros na Sidebar (Apenas para o Painel Geral)
filtro_nome = ""
filtro_status = "Todos"
if aba == "📊 Painel Geral":
    st.sidebar.subheader("🔍 Filtros")
    filtro_nome = st.sidebar.text_input("Buscar por nome")
    filtro_status = st.sidebar.selectbox("Filtrar por Status", ["Todos", "Pendente", "Em Negociação", "Urgente", "Finalizado"])

# --- ABA: NOVO LEAD ---
if aba == "➕ Novo Lead":
    st.header("🚀 Cadastrar Novo Cliente")
    with st.form("cadastro_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome completo do cliente")
        telefone = c2.text_input("WhatsApp (Ex: 5511999999999)")
        status = st.selectbox("Status Inicial", ["Pendente", "Em Negociação", "Urgente"])
        obs = st.text_area("Notas sobre o interesse do cliente")
        
        if st.form_submit_button("✅ Finalizar Cadastro"):
            if nome and telefone:
                db.collection("leads").add({
                    "nome": nome,
                    "telefone": telefone.replace(" ", "").replace("-", ""),
                    "status": status,
                    "obs": obs,
                    "data_criacao": datetime.now()
                })
                st.success("Lead salvo com sucesso!")
                st.balloons()
            else:
                st.warning("Preencha os campos obrigatórios!")

# --- ABA: PAINEL GERAL ---
elif aba == "📊 Painel Geral":
    data = buscar_dados()
    if not data:
        st.info("Nenhum lead cadastrado ainda.")
    else:
        # Métricas de Topo
        df = pd.DataFrame(data)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de Leads", len(df))
        c2.metric("🔥 Urgentes", len(df[df['status'] == 'Urgente']))
        c3.metric("🤝 Em Negociação", len(df[df['status'] == 'Em Negociação']))
        c4.metric("✅ Finalizados", len(df[df['status'] == 'Finalizado']))

        st.markdown("---")

        # Aplicação dos Filtros
        if filtro_status != "Todos":
            data = [d for d in data if d['status'] == filtro_status]
        if filtro_nome:
            data = [d for d in data if filtro_nome.lower() in d['nome'].lower()]

        # Exibição dos Leads
        for lead in data:
            with st.container():
                # Design do Card
                col_info, col_status, col_acao = st.columns([3, 2, 1.5])
                
                with col_info:
                    st.markdown(f"### {lead['nome']}")
                    st.caption(f"📅 Cadastrado em: {lead['data_criacao'].strftime('%d/%m/%Y %H:%M')}")
                    if lead.get('obs'):
                        st.info(f"📝 {lead['obs']}")

                with col_status:
                    # Mudar status rapidamente
                    novo_status = st.selectbox(
                        "Alterar Status", 
                        ["Pendente", "Em Negociação", "Urgente", "Finalizado"],
                        index=["Pendente", "Em Negociação", "Urgente", "Finalizado"].index(lead['status']),
                        key=f"status_{lead['id']}"
                    )
                    if novo_status != lead['status']:
                        db.collection("leads").document(lead['id']).update({"status": novo_status})
                        st.rerun()

                with col_acao:
                    link_zap = f"https://wa.me/{lead['telefone']}"
                    st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-zap">💬 WHATSAPP</a>', unsafe_allow_html=True)
                    if st.button("🗑️ Excluir", key=f"del_{lead['id']}"):
                        db.collection("leads").document(lead['id']).delete()
                        st.rerun()
                
                st.markdown("---")

# --- ABA: RELATÓRIOS ---
elif aba == "📈 Relatórios":
    st.header("📊 Análise GSCOMUNICAÇÕES")
    data = buscar_dados()
    if data:
        df = pd.DataFrame(data)
        
        # Gráfico Simples de Status
        st.subheader("Distribuição por Status")
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts)
        
        # Tabela de Dados Brutos
        with st.expander("Ver lista completa (Excel Style)"):
            st.dataframe(df)
