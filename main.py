import streamlit as st
from core.auth import gerenciar_autenticacao
from views.interface import renderizar_sidebar, exibir_painel_geral, exibir_novo_lead, exibir_estatisticas

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
    
    /* Estilização das Métricas com Fundo Cinza Escuro */
    [data-testid="stMetric"] {
        background-color: #262730 !important; /* Cinza Escuro */
        border: 1px solid #41444C !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
    }

    /* Título da Métrica (Label) em cinza claro para ler no fundo escuro */
    [data-testid="stMetricLabel"] {
        color: #B9BBC1 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        justify-content: center !important;
    }

    /* Valor da Métrica em Branco para alto contraste */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 2rem !important;
        text-align: center !important;
    }

    /* Centraliza o conteúdo da métrica */
    [data-testid="stMetric"] > div {
        width: fit-content !important;
        margin: auto !important;
    }
    /* Estilização dos Cards de Leads - Tema Dark Profissional */
    .lead-card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        /* Fundo escuro padrão para todos os cards */
        background-color: #1e293b !important; 
        border: 1px solid #334155;
        border-left: 10px solid #ccc;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        color: #f1f5f9 !important; /* Texto claro para leitura no escuro */
        transition: transform 0.2s;
    }
    .lead-card:hover { transform: translateY(-2px); border-color: #475569; }

    /* Cores das Bordas Laterais por Status (Mantendo o fundo escuro) */
    .status-urgente { 
        border-left-color: #ef4444 !important; 
        background: linear-gradient(90deg, #2d1a1a 0%, #1e293b 100%) !important;
    }
    .status-negociacao { 
        border-left-color: #f59e0b !important; 
        background: linear-gradient(90deg, #2d241a 0%, #1e293b 100%) !important;
    }
    .status-pendente { 
        border-left-color: #0ea5e9 !important; 
        background: linear-gradient(90deg, #1a252d 0%, #1e293b 100%) !important;
    }
    .status-finalizado { 
        border-left-color: #22c55e !important; 
        background: linear-gradient(90deg, #1a2d1e 0%, #1e293b 100%) !important;
    }
    
    /* Status "Perdido" (Cinza mais opaco) */
    .status-perdido {
        border-left-color: #64748b !important;
        opacity: 0.8;
    }

    /* Ajuste de contraste para textos dentro do card */
    .lead-card div, .lead-card span {
        color: #f1f5f9 !important;
    }
            
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
        from views.interface import exibir_painel_admin # Garanta a importação
        exibir_painel_admin()

    # Rodapé discreto
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 GS COMUNICAÇÕES - CRM v2.0")
