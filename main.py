import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone
import urllib.parse
import io

# --- CONFIGURAÇÃO INICIAL ---
PROJECT_ID = "gscomunicacoes-91512" 
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/leads"

st.set_page_config(page_title="GS COMUNICAÇÕES | CRM", page_icon="📞", layout="wide")

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .btn-zap {
        background-color: #25D366; color: white !important; padding: 10px;
        border-radius: 8px; text-decoration: none; font-weight: bold;
        display: flex; align-items: center; justify-content: center; width: 100%;
        transition: 0.3s; margin-bottom: 5px;
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
    except: return []

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

def atualizar_status_rest(doc_id, novo_status):
    url = f"{BASE_URL}/{doc_id}?updateMask.fieldPaths=status"
    payload = {"fields": {"status": {"stringValue": novo_status}}}
    return requests.patch(url, json=payload).status_code == 200

def eliminar_lead_rest(doc_id):
    return requests.delete(f"{BASE_URL}/{doc_id}").status_code == 200

def gerar_link_whatsapp(telefone, nome_cliente):
    texto = f"Olá {nome_cliente}, aqui é da GS COMUNICAÇÕES! Como podemos ajudar hoje?"
    return f"https://wa.me/{telefone}?text={urllib.parse.quote(texto)}"

# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=60)
st.sidebar.title("CRM GS")
aba = st.sidebar.radio("Navegação", ["📊 Painel Geral", "➕ Novo Lead", "📈 Estatísticas"])

# --- ABA: NOVO LEAD ---
if aba == "➕ Novo Lead":
    st.header("🚀 Cadastrar Novo Lead")
    with st.form("cadastro_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome do Cliente")
        tel = c2.text_input("WhatsApp (DDD + Número)")
        status = st.selectbox("Status Inicial", ["Pendente", "Em Negociação", "Urgente"])
        obs = st.text_area("Observações")
        if st.form_submit_button("✅ Salvar Cliente"):
            if nome and tel:
                if salvar_lead_rest(nome, tel, status, obs):
                    st.success("Lead cadastrado!")
                    st.balloons()
                else: st.error("Erro ao salvar no Firebase.")
            else: st.warning("Preencha Nome e Telefone.")

# --- ABA: PAINEL GERAL ---
elif aba == "📊 Painel Geral":
    st.header("📋 Gestão de Atendimento")
    dados = buscar_dados_rest()
    
    if dados:
        # Barra superior de filtros
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            busca = st.text_input("🔍 Buscar por nome...", placeholder="Digite o nome do cliente")
        with col_f2:
            status_filtro = st.multiselect("Filtrar Status", ["Pendente", "Em Negociação", "Urgente", "Finalizado"], default=["Pendente", "Em Negociação", "Urgente"])

        st.markdown("---")

        for lead in dados:
            # Lógica de Filtro
            if lead['status'] in status_filtro and (busca.lower() in lead['nome'].lower()):
                with st.expander(f"👤 {lead['nome']} | {lead['status']}"):
                    c1, c2, c3 = st.columns([2, 1.5, 1])
                    
                    with c1:
                        st.write(f"**WhatsApp:** {lead['telefone']}")
                        st.write(f"**Obs:** {lead['obs']}")
                        data_pt = pd.to_datetime(lead['data_criacao']).strftime('%d/%m/%Y %H:%M')
                        st.caption(f"📅 {data_pt}")

                    with c2:
                        novo_st = st.selectbox("Mudar Status", ["Pendente", "Em Negociação", "Urgente", "Finalizado"], 
                                             index=["Pendente", "Em Negociação", "Urgente", "Finalizado"].index(lead['status']),
                                             key=f"up_{lead['id']}")
                        if novo_st != lead['status']:
                            if atualizar_status_rest(lead['id'], novo_st):
                                st.rerun()

                    with c3:
                        st.markdown(f'<a href="{gerar_link_whatsapp(lead["telefone"], lead["nome"])}" target="_blank" class="btn-zap">WHATSAPP</a>', unsafe_allow_html=True)
                        if st.button("🗑️ Excluir", key=f"del_{lead['id']}", use_container_width=True):
                            if eliminar_lead_rest(lead['id']): st.rerun()

# --- ABA: ESTATÍSTICAS ---
elif aba == "📈 Estatísticas":
    st.header("📈 Relatórios e Exportação")
    dados = buscar_dados_rest()
    
    if dados:
        df = pd.DataFrame(dados)
        df['data_criacao'] = pd.to_datetime(df['data_criacao'], errors='coerce')
        df['data_dia'] = df['data_criacao'].dt.date
        df = df.sort_values('data_criacao', ascending=False)

        # Métricas
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(df))
        m2.metric("🔥 Urgente", len(df[df['status'] == 'Urgente']))
        m3.metric("🤝 Negociando", len(df[df['status'] == 'Em Negociação']))
        m4.metric("✅ Finalizados", len(df[df['status'] == 'Finalizado']))

        # Gráficos
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Funil de Vendas")
            st.bar_chart(df['status'].value_counts(), color="#25D366")
        with g2:
            st.subheader("Leads por Dia")
            st.line_chart(df.groupby('data_dia').size(), color="#128C7E")

        # Exportação
        st.markdown("---")
        st.subheader("💾 Exportar Dados")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Baixar Planilha CSV", data=csv, file_name=f'leads_gs_{datetime.now().date()}.csv', mime='text/csv')
    else:
        st.warning("Sem dados.")
