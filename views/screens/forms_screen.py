import streamlit as st
from services.database import salvar_no_firebase

def exibir_novo_lead():
    st.header("➕ Cadastrar Novo Lead")
    u = st.session_state.user_data
    
    with st.form("form_novo_lead", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome do Cliente")
        tel = c2.text_input("WhatsApp")
        status = st.selectbox("Status Inicial", ["Pendente", "Em Negociação", "Urgente"])
        obs = st.text_area("Observações")
        
        if st.form_submit_button("✅ Salvar Lead"):
            if nome and tel:
                dados = {
                    "nome": nome, "telefone": tel, "status": status,
                    "obs": obs, "empresa_id": u['empresa_id'], "vendedor_id": u['email']
                }
                if salvar_no_firebase("leads", dados):
                    st.success("Lead cadastrado!")
                    st.balloons()
            else:
                st.warning("Preencha os campos obrigatórios.")