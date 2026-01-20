import streamlit as st
from database import buscar_documento, salvar_no_firebase

def gerenciar_autenticacao():
    """Controlador central de acesso e navegação entre telas de login/cadastro"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.user_data = None
        st.session_state.tela = "login"

    if not st.session_state.autenticado:
        if st.session_state.tela == "login":
            tela_login()
        elif st.session_state.tela == "cadastro_usuario":
            tela_cadastro()
        elif st.session_state.tela == "cadastro_empresa":
            tela_cadastro_empresa()
        st.stop()  # Impede o carregamento do restante do app se não estiver logado

def tela_login():
    st.title("🔐 GS CRM - Acesso")
    
    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        btn_login = st.form_submit_button("Entrar", use_container_width=True)
        
        if btn_login:
            user = buscar_documento("usuarios", "email", email)
            
            if user and user.get("senha") == senha:
                st.session_state.user_data = user
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")

    st.markdown("---")
    if st.button("Não tem uma conta? Cadastre-se agora"):
        st.session_state.tela = "cadastro_usuario"
        st.rerun()

def tela_cadastro():
    st.title("🚀 Criar Nova Conta")
    st.info("Se a sua empresa já utiliza o GS CRM, digite o ID dela corretamente para se juntar à equipe.")
    
    with st.form("form_cadastro_vendedor"):
        nome = st.text_input("Nome Completo")
        email = st.text_input("Seu E-mail de trabalho")
        senha = st.text_input("Crie uma Senha", type="password")
        id_empresa_pretendido = st.text_input("ID da Empresa", help="Ex: gs_telecom ou empresa_xyz")
        
        if st.form_submit_button("Verificar Empresa"):
            if not (nome and email and senha and id_empresa_pretendido):
                st.warning("Preencha todos os campos.")
            else:
                # Verifica se a empresa já existe no banco
                empresa = buscar_documento("empresas", "id_empresa", id_empresa_pretendido.lower())
                
                if empresa:
                    # CASO 1: Empresa existe -> Cadastra como VENDEDOR
                    novo_user = {
                        "nome": nome,
                        "email": email,
                        "senha": senha,
                        "empresa_id": id_empresa_pretendido.lower(),
                        "nivel": "vendedor"
                    }
                    if salvar_no_firebase("usuarios", novo_user):
                        st.success(f"Conta vinculada à empresa {empresa['razao']}! Faça login.")
                        st.session_state.tela = "login"
                        st.rerun()
                else:
                    # CASO 2: Empresa não existe -> Direciona para cadastro de empresa
                    st.session_state.temp_user = {
                        "nome": nome, "email": email, 
                        "senha": senha, "id_empresa": id_empresa_pretendido.lower()
                    }
                    st.session_state.tela = "cadastro_empresa"
                    st.rerun()

    if st.button("⬅️ Voltar ao Login"):
        st.session_state.tela = "login"
        st.rerun()

def tela_cadastro_empresa():
    st.title("🏢 Registrar Nova Empresa")
    temp_u = st.session_state.temp_user
    st.warning(f"O ID '{temp_u['id_empresa']}' é novo. Para continuar, registre os dados da empresa.")
    
    with st.form("form_nova_empresa"):
        razao = st.text_input("Razão Social ou Nome Fantasia")
        cnpj = st.text_input("CNPJ / CPF (Opcional)")
        contato = st.text_input("Telefone de Contato")
        
        if st.form_submit_button("Finalizar e Criar Dashboard"):
            if not razao:
                st.error("O nome da empresa é obrigatório.")
            else:
                # 1. Salva a Empresa
                dados_empresa = {
                    "id_empresa": temp_u['id_empresa'],
                    "razao": razao,
                    "cnpj": cnpj,
                    "contato": contato
                }
                salvar_no_firebase("empresas", dados_empresa)
                
                # 2. Salva o Usuário como ADMIN daquela empresa
                novo_admin = {
                    "nome": temp_u['nome'],
                    "email": temp_u['email'],
                    "senha": temp_u['senha'],
                    "empresa_id": temp_u['id_empresa'],
                    "nivel": "admin"
                }
                salvar_no_firebase("usuarios", novo_admin)
                
                st.success("Empresa e Administrador cadastrados com sucesso!")
                st.session_state.tela = "login"
                st.rerun()

    if st.button("⬅️ Cancelar"):
        st.session_state.tela = "login"
        st.rerun()
