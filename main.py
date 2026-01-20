import streamlit as st
from auth import gerenciar_autenticacao
from interface import renderizar_sidebar, exibir_painel_geral, exibir_novo_lead, exibir_estatisticas

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="GS COMUNICAÇÕES | CRM Multi-Empresa",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILIZAÇÃO CSS GLOBAL ---
st.markdown("""
    <style>
    /* Cores de Fundo e Layout Principal */
    .stApp { background-color: #f8f9fa; }
    
    /* MÉTRICAS - Fundo Cinza Escuro (Dark Mode Style) */
    [data-testid="stMetric"] {
        background-color: #262730 !important; 
        border: 1px solid #41444C !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
    }

    /* Ajuste de Texto nas Métricas */
    [data-testid="stMetricLabel"] {
        color: #B9BBC1 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }

    /* CARDS DE LEADS - Estrutura Base */
    .lead-card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        background-color: #ffffff;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        color: #1e293b;
        transition: transform 0.2s;
        border-left: 8px solid #ccc; /* Cor padrão para status */
        /* A borda direita (Temperatura) é injetada via style inline no interface.py */
    }
    .lead-card:hover { transform: translateY(-3px); }

    /* Estilização de Bordas por Status (Esquerda) */
    .status-urgente { border-left-color: #ef4444 !important; background-color: #fff5f5 !important; }
    .status-negociacao { border-left-color: #f59e0b !important; background-color: #fff9f0 !important; }
    .status-pendente { border-left-color: #0ea5e9 !important; background-color: #f0f9ff !important; }
    .status-finalizado { border-left-color: #22c55e !important; background-color: #f0fdf4 !important; }

    /* Títulos e Detalhes dentro do Card */
    .lead-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 2px; display: flex; align-items: center; }
    .lead-status { font-size: 0.75rem; text-transform: uppercase; font-weight: 800; opacity: 0.7; }

    /* Botão customizado para WhatsApp */
    .btn-zap {
        background-color: #25D366;
        color: white !important;
        padding: 10px 15px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        text-align: center;
        margin-top: 10px;
    }
    .btn-zap:hover { background-color: #128C7E; text-decoration: none; }

    /* Ajustes Gerais de Tabelas e Gráficos */
    .stTable { background-color: white; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "tela" not in st.session_state:
    st.session_state.tela = "login"

# --- 4. CONTROLE DE ACESSO (Login/Cadastro) ---
gerenciar_autenticacao()

# --- 5. INTERFACE LOGADA ---
if st.session_state.autenticado:
    # Renderiza a Sidebar
    aba_selecionada = renderizar_sidebar()

    # Roteamento de Páginas
    try:
        if aba_selecionada == "📊 Painel Geral":
            exibir_painel_geral()
        
        elif aba_selecionada == "➕ Novo Lead":
            exibir_novo_lead()
        
        elif aba_selecionada == "📈 Estatísticas":
            exibir_estatisticas()
        
        elif aba_selecionada == "👑 Administração":
            from interface import exibir_painel_admin
            exibir_painel_admin()
            
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar esta página: {e}")
        st.info("Tente recarregar a página ou fazer login novamente.")

    # Rodapé da Sidebar
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 GS COMUNICAÇÕES")
    st.sidebar.caption("CRM Inteligente v2.5")
