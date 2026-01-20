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
# Aqui definimos as cores dos cards e botões que a interface.py vai usar
st.markdown("""
    <style>
    /* Cores de Fundo e Layout */
    .main { background-color: #f8f9fa; }
    
/* Estilização das Métricas (Total, Ativos, Conversão) */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        text-align: center;
    }

    /* Alterar a cor do título da métrica (Label) */
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* Alterar a cor e tamanho do valor da métrica */
    [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-size: 2.2rem !important;
    }
    
    /* Estilização dos Cards de Leads */
    .lead-card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        border-left: 10px solid #ccc;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        color: #1e293b;
        transition: transform 0.2s;
    }
    .lead-card:hover { transform: translateY(-2px); }

    /* Estilização por Status - Fundo e Borda */
    .status-urgente { 
        background-color: #ffebee !important; 
        border-left-color: #ef4444 !important; 
    }
    .status-negociacao { 
        background-color: #fff7ed !important; 
        border-left-color: #f59e0b !important; 
    }
    .status-pendente { 
        background-color: #f0f9ff !important; 
        border-left-color: #0ea5e9 !important; 
    }
    .status-finalizado { 
        background-color: #f0fdf4 !important; 
        border-left-color: #22c55e !important; 
    }
    
    /* Ajuste do Título e Status dentro do Card */
    .lead-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 2px; }
    .lead-status { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }

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
        transition: 0.3s;
    }
    .btn-zap:hover { background-color: #128C7E; transform: scale(1.02); }

    /* Ajuste de métricas */
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# --- 3. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "tela" not in st.session_state:
    st.session_state.tela = "login"

# --- 4. FLUXO DE AUTENTICAÇÃO ---
# Chama o auth.py. Se não estiver logado, ele trava o app na tela de login/cadastro.
gerenciar_autenticacao()

# --- 5. INTERFACE DO USUÁRIO (SÓ EXECUTA SE LOGADO) ---
if st.session_state.autenticado:
    # Renderiza a Sidebar e captura qual aba o usuário clicou
    aba_selecionada = renderizar_sidebar()

    # Roteamento das Abas (chama funções da interface.py)
    if aba_selecionada == "📊 Painel Geral":
        exibir_painel_geral()
    elif aba_selecionada == "➕ Novo Lead":
        exibir_novo_lead()
    elif aba_selecionada == "📈 Estatísticas":
        exibir_estatisticas()
    elif aba_selecionada == "👑 Administração":
        from interface import exibir_painel_admin # Garanta a importação
        exibir_painel_admin()

    # Rodapé discreto
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 GS COMUNICAÇÕES - CRM v2.0")
