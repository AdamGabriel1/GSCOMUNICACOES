import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone # Adicione timezone ao seu import
import urllib.parse

# --- CONFIGURAÇÃO INICIAL ---
PROJECT_ID = "gscomunicacoes-91512"  # Verifique se este ID está correto no seu console
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/leads"

st.set_page_config(page_title="GSCOMUNICAÇÕES | CRM", page_icon="📞", layout="wide")

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .btn-zap {
        background-color: #25D366; color: white !important; padding: 12px;
        border-radius: 8px; text-decoration: none; font-weight: bold;
        display: flex; align-items: center; justify-content: center; width: 100%;
        transition: 0.3s;
    }
    .btn-zap:hover { background-color: #128C7E; transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE COMUNICAÇÃO (REST) ---
def buscar_dados_rest():
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            data = response.json()
            leads = []
            if 'documents' in data:
                for doc in data['documents']:
                    f = doc.get('fields', {})
                    leads.append({
                        "id": doc['name'].split('/')[-1],
                        "nome": f.get('nome', {}).get('stringValue', 'Sem nome'),
                        "telefone": f.get('telefone', {}).get('stringValue', ''),
                        "status": f.get('status', {}).get('stringValue', 'Pendente'),
                        "obs": f.get('obs', {}).get('stringValue', ''),
                        "data_criacao": f.get('data_criacao', {}).get('timestampValue', '')
                    })
            return leads
        return []
    except:
        return []

def salvar_lead_rest(nome, telefone, status, obs):
    # Forma moderna recomendada pelo Python 3.12+
    data_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    payload = {
        "fields": {
            "nome": {"stringValue": nome},
            "telefone": {"stringValue": telefone.replace(" ", "").replace("-", "")},
            "status": {"stringValue": status},
            "obs": {"stringValue": obs},
            "data_criacao": {"timestampValue": data_utc}
        }
    }
    res = requests.post(BASE_URL, json=payload)
    return res.status_code == 200

def eliminar_lead_rest(doc_id):
    url_del = f"{BASE_URL}/{doc_id}"
    res = requests.delete(url_del)
    return res.status_code == 200

def gerar_link_whatsapp(telefone, nome_cliente):
    texto = f"Olá {nome_cliente}, aqui é da GS COMUNICAÇÕES! Como podemos ajudar hoje?"
    return f"https://wa.me/{telefone}?text={urllib.parse.quote(texto)}"

# --- INTERFACE SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=60)
st.sidebar.title("GS COMUNICAÇÕES")
aba = st.sidebar.radio("Navegação", ["📊 Painel Geral", "➕ Novo Lead", "📈 Estatísticas"])

# --- ABA: NOVO LEAD ---
if aba == "➕ Novo Lead":
    st.header("🚀 Cadastrar Novo Lead")
    with st.form("cadastro_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome do Cliente")
        tel = c2.text_input("WhatsApp (com DDD)")
        stts = st.selectbox("Status Inicial", ["Pendente", "Em Negociação", "Urgente"])
        notas = st.text_area("Observações Adicionais")
        
        if st.form_submit_button("✅ Finalizar Cadastro"):
            if nome and tel:
                if salvar_lead_rest(nome, tel, stts, notas):
                    st.success(f"Lead {nome} cadastrado com sucesso!")
                else:
                    st.error("Erro ao salvar. Verifique as regras do Firebase.")
            else:
                st.warning("Nome e Telefone são obrigatórios.")

# --- ABA: PAINEL GERAL ---
elif aba == "📊 Painel Geral":
    st.header("📋 Gestão de Atendimento")
    dados = buscar_dados_rest()
    
    if dados:
        # Novo Filtro de Status no Painel
        status_filtro = st.multiselect(
            "Filtrar por Status", 
            ["Pendente", "Em Negociação", "Urgente", "Finalizado"],
            default=["Pendente", "Em Negociação", "Urgente"]
        )
        
        for lead in dados:
            # Só mostra se o status estiver no filtro
            if lead['status'] in status_filtro:
                with st.expander(f"👤 {lead['nome']} - {lead['status']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**WhatsApp:** {lead['telefone']}")
                        st.write(f"**Obs:** {lead['obs']}")
                        data_obj = pd.to_datetime(lead['data_criacao'])
                        data_ptbr = data_obj.strftime('%d/%m/%Y')
                        st.caption(f"📅 Cadastrado em: {data_ptbr}")
                    
                    with col2:
                        link_zap = gerar_link_whatsapp(lead['telefone'], lead['nome'])
                        st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-zap">CHAMAR</a>', unsafe_allow_html=True)
                        if st.button("🗑️ Apagar", key=f"del_{lead['id']}"):
                            if eliminar_lead_rest(lead['id']):
                                st.rerun()

# --- ABA: ESTATÍSTICAS ---
elif aba == "📈 Estatísticas":
    st.header("📈 Relatórios de Desempenho")
    dados = buscar_dados_rest()
    
    if not dados:
        st.warning("Não há dados suficientes para gerar relatórios.")
    else:
        df = pd.DataFrame(dados)
        
        # 1. CONVERSÃO SEGURA: Transforma a coluna em Data real
        # O errors='coerce' evita que o app quebre se houver um campo vazio
        df['data_criacao'] = pd.to_datetime(df['data_criacao'], errors='coerce')
        
        # 2. CRIAÇÃO DA COLUNA DE DATA (Ano-Mês-Dia) para o gráfico
        # Usamos .dt.date em vez de .str.split
        df['data_simples'] = df['data_criacao'].dt.date
        
        # Ordenar por data para o gráfico não ficar bagunçado
        df = df.sort_values('data_simples')

        # --- MÉTRICAS ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Leads", len(df))
        m2.metric("🔥 Urgentes", len(df[df['status'] == 'Urgente']))
        m3.metric("🤝 Em Negociação", len(df[df['status'] == 'Em Negociação']))
        
        st.markdown("---")
        
        # --- GRÁFICOS ---
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Situação dos Leads")
            st.bar_chart(df['status'].value_counts(), color="#25D366")
            
        with g2:
            st.subheader("Crescimento Diário")
            # Agrupa por data e conta quantos leads em cada dia
            leads_por_dia = df.groupby('data_simples').size()
            st.line_chart(leads_por_dia, color="#128C7E")
