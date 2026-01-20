import streamlit as st
from services.database import (
    buscar_todos_usuarios, 
    buscar_todas_empresas, 
    eliminar_documento, 
    eliminar_empresa_completa,
    resetar_senha_usuario
)

def exibir_painel_admin():
    u_logado = st.session_state.user_data
    st.header("👑 Painel de Administração")

    # --- GESTÃO DE EMPRESAS ---
    if u_logado['nivel'] == 'super':
        st.subheader("🏢 Gestão de Empresas (Master)")
        empresas = buscar_todas_empresas()
        
        if empresas:
            for emp in empresas:
                with st.expander(f"🏢 {emp['razao']} (ID: {emp['id_empresa']})"):
                    col_e1, col_e2 = st.columns([3, 1])
                    with col_e1:
                        st.write(f"**CNPJ:** {emp.get('cnpj', 'N/A')}")
                        st.write(f"**Contato:** {emp.get('contato', 'N/A')}")
                    with col_e2:
                        if st.button("🗑️ Deletar Empresa", key=f"del_emp_{emp['id']}"):
                            if eliminar_empresa_completa(emp['id'], emp['id_empresa']):
                                st.success(f"Empresa {emp['razao']} removida!")
                                st.rerun()

    # --- GESTÃO DE USUÁRIOS ---
    st.subheader("👥 Controle de Usuários")
    usuarios = buscar_todos_usuarios(u_logado)
    
    if usuarios:
        for user in usuarios:
            status_cor = "🔵" if user['nivel'] == 'admin' else "🟢"
            with st.expander(f"{status_cor} {user['nome']} - {user['email']}"):
                c1, c2 = st.columns([2, 2])
                with c1:
                    st.write(f"**Nível:** {user['nivel'].upper()}")
                    if st.button("🗑️ Remover Acesso", key=f"del_u_{user['id']}"):
                        if user['email'] != "admin@gs.com":
                            eliminar_documento("usuarios", user['id'])
                            st.rerun()
                with c2:
                    nova_senha = st.text_input("Nova Senha", type="password", key=f"pw_{user['id']}")
                    if st.button("Confirmar", key=f"btn_pw_{user['id']}"):
                        from core.security import criptografar_senha
                        if resetar_senha_usuario(user['id'], criptografar_senha(nova_senha)):
                            st.success("Senha atualizada!")