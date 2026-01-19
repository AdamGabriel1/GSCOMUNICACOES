import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone
import urllib.parse

# --- CONFIGURAÇÃO INICIAL ---
PROJECT_ID = "gscomunicacoes-91512" 
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/leads"

st.set_page_config(page_title="GS COMUNICAÇÕES | CRM", page_icon="📞", layout="wide")

# --- ESTILIZAÇÃO CSS AVANÇADA ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    /* Estilo dos Cards */
    .lead-card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 8px solid #ccc;
        background-color: white;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    /* Cores por Status */
    .status-urgente { border-left-color: #ff4b4b !important; background-color: #fff5f5; }
    .status-negociacao { border-left-color: #ffa500 !important; }
    .status-pendente { border-left-color: #3e95cd !important; }
    .status-finalizado { border-left-color: #28a745 !important; opacity: 0.8; }
    
    .btn-zap {
        background-color: #25D366; color: white !important; padding: 10px;
        border-radius: 8px; text-decoration: none; font-weight: bold;
        display: flex; align-items: center; justify-content: center; width: 100%;
        transition: 0.3s;
    }
    .btn-zap:hover { background-color: #128C7E; transform: scale(1.05); }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
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
    except: return []

def atualizar_status_rest(doc_id, novo_status):
    url = f"{BASE_URL}/{doc_id}?updateMask.fieldPaths=status"
    payload = {"fields": {"status": {"stringValue": novo_status}}}
    return requests.patch(url, json=payload).status_code == 200

def salvar_lead_rest(nome, telefone, status, obs):
    data_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = {"fields": {
        "nome": {"stringValue": nome},
        "telefone": {"stringValue": telefone.replace(" ", "").replace("-", "")},
        "status": {"stringValue": status},
        "obs": {"stringValue": obs},
        "data_criacao": {"timestampValue": data_utc}
    }}
    return requests.post(BASE_URL, json=payload).status_code == 200

def eliminar_lead_rest(doc_id):
    return requests.delete(f"{BASE_URL}/{doc_id}").status_code == 200

# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=60)
st.sidebar.title("GS COMUNICAÇÕES")
aba = st.sidebar.radio("Navegação", ["📊 Painel Geral", "➕ Novo Lead", "📈 Estatísticas"])

# --- ABA: PAINEL GERAL ---
if aba == "📊 Painel Geral":
    st.header("📋 Gestão de Leads")
    dados = buscar_dados_rest()
    
    if dados:
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            busca = st.text_input("🔍 Buscar cliente...")
        with col_f2:
            status_filtro = st.multiselect("Filtrar por:", ["Pendente", "Em Negociação", "Urgente", "Finalizado"], default=["Pendente", "Em Negociação", "Urgente"])

        st.markdown("---")

        for lead in dados:
            if lead['status'] in status_filtro and (busca.lower() in lead['nome'].lower()):
                # Definição da Classe CSS Dinâmica
                classe_status = ""
                if lead['status'] == "Urgente": classe_status = "status-urgente"
                elif lead['status'] == "Em Negociação": classe_status = "status-negociacao"
                elif lead['status'] == "Finalizado": classe_status = "status-finalizado"
                else: classe_status = "status-pendente"

                # Renderização do Card com Container Customizado
                st.markdown(f"""
                    <div class="lead-card {classe_status}">
                        <h3 style='margin:0;'>{lead['nome']} {'🔥' if lead['status'] == 'Urgente' else ''}</h3>
                        <p style='margin:0; color: #666;'>Status atual: <b>{lead['status']}</b></p>
                    </div>
                """, unsafe_allow_html=True)

                with st.expander("Ações e Detalhes"):
                    c1, c2, c3 = st.columns([2, 1.5, 1])
                    with c1:
                        st.write(f"**WhatsApp:** {lead['telefone']}")
                        st.info(f"**Notas:** {lead['obs']}" if lead['obs'] else "Sem observações.")
                        dt = pd.to_datetime(lead['data_criacao']).strftime('%d/%m/%Y %H:%M')
                        st.caption(f"📅 Registrado em {dt}")

                    with c2:
                        novo_st = st.selectbox("Mudar Status", ["Pendente", "Em Negociação", "Urgente", "Finalizado"], 
                                             index=["Pendente", "Em Negociação", "Urgente", "Finalizado"].index(lead['status']),
                                             key=f"st_{lead['id']}")
                        if novo_st != lead['status']:
                            if atualizar_status_rest(lead['id'], novo_st): st.rerun()

                    with c3:
                        msg = f"Olá {lead['nome']}, aqui é da GS COMUNICAÇÕES!"
                        link = f"https://wa.me/{lead['telefone']}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{link}" target="_blank" class="btn-zap">WHATSAPP</a>', unsafe_allow_html=True)
                        if st.button("🗑️ Excluir", key=f"del_{lead['id']}", use_container_width=True):
                            if eliminar_lead_rest(lead['id']): st.rerun()

# --- ABA: NOVO LEAD ---
elif aba == "➕ Novo Lead":
    st.header("🚀 Cadastrar Cliente")
    with st.form("add_form", clear_on_submit=True):
        n = st.text_input("Nome")
        t = st.text_input("Telefone")
        s = st.selectbox("Status", ["Pendente", "Em Negociação", "Urgente"])
        o = st.text_area("Notas")
        if st.form_submit_button("Salvar"):
            if n and t:
                if salvar_lead_rest(n, t, s, o): st.success("Sucesso!"); st.balloons()
            else: st.warning("Preencha os campos.")

# --- ABA: ESTATÍSTICAS ---
elif aba == "📈 Estatísticas":
    st.header("📈 Desempenho GS")
    dados = buscar_dados_rest()
    if dados:
        df = pd.DataFrame(dados)
        df['data_criacao'] = pd.to_datetime(df['data_criacao'])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Leads", len(df))
        m2.metric("Atendimentos Ativos", len(df[df['status'] != 'Finalizado']))
        m3.metric("Conversão", f"{len(df[df['status'] == 'Finalizado'])/len(df):.1%}" if len(df)>0 else "0%")
        
        st.subheader("Volume por Status")
        st.bar_chart(df['status'].value_counts())
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Base de Dados", csv, "leads.csv", "text/csv")
