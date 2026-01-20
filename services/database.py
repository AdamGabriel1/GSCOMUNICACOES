import requests
from datetime import datetime, timezone

# --- CONFIGURAÇÃO ---
PROJECT_ID = "gscomunicacoes-91512"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

def buscar_documento(colecao, campo, valor):
    """Busca um documento específico em uma coleção filtrando por um campo"""
    url = f"{BASE_URL}/{colecao}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            docs = res.json().get('documents', [])
            for doc in docs:
                f = doc.get('fields', {})
                # Verifica se o valor do campo bate com o esperado
                if f.get(campo, {}).get('stringValue') == valor:
                    # Converte o formato complexo do Firebase em um dicionário simples
                    data = {k: list(v.values())[0] for k, v in f.items()}
                    data['id'] = doc['name'].split('/')[-1]
                    return data
        return None
    except Exception as e:
        print(f"Erro ao buscar documento: {e}")
        return None

def salvar_no_firebase(colecao, dados):
    """Salva um novo documento em qualquer coleção"""
    payload = {"fields": {}}
    
    for k, v in dados.items():
        payload["fields"][k] = {"stringValue": str(v)}
    
    # Se for lead, garante o timestamp correto no formato do Google
    if colecao == "leads" and "data_criacao" not in dados:
        data_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        payload["fields"]["data_criacao"] = {"timestampValue": data_utc}
        
    try:
        res = requests.post(f"{BASE_URL}/{colecao}", json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False

def atualizar_status_rest(doc_id, novo_status):
    """Atualiza apenas o campo 'status' de um lead específico"""
    url = f"{BASE_URL}/leads/{doc_id}?updateMask.fieldPaths=status"
    payload = {
        "fields": {
            "status": {"stringValue": novo_status}
        }
    }
    try:
        res = requests.patch(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")
        return False

def eliminar_documento(colecao, doc_id):
    """Remove um documento do Firebase"""
    url = f"{BASE_URL}/{colecao}/{doc_id}"
    try:
        res = requests.delete(url)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao eliminar: {e}")
        return False

def buscar_leads_filtrados(user_data):
    """Busca leads aplicando a lógica de hierarquia (SaaS/Multitenant)"""
    url = f"{BASE_URL}/leads"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return []
            
        leads = []
        docs = res.json().get('documents', [])
        
        for doc in docs:
            f = doc.get('fields', {})
            # Extração limpa dos campos
            l = {k: list(v.values())[0] for k, v in f.items()}
            l['id'] = doc['name'].split('/')[-1]
            
            empresa_id = l.get('empresa_id')
            vendedor_id = l.get('vendedor_id')

            # --- LÓGICA DE VISIBILIDADE ---
            # 1. Super Admin vê absolutamente tudo
            if user_data['nivel'] == 'super':
                leads.append(l)
            
            # 2. Admin da Empresa vê todos os leads da sua empresa
            elif user_data['nivel'] == 'admin' and empresa_id == user_data['empresa_id']:
                leads.append(l)
            
            # 3. Vendedor vê apenas os leads que ele mesmo criou
            elif user_data['nivel'] == 'vendedor' and vendedor_id == user_data['email']:
                leads.append(l)
                
        return leads
    except Exception as e:
        print(f"Erro ao carregar leads: {e}")
        return []
        
def buscar_todos_usuarios(user_data):
    """Busca usuários dependendo do nível de acesso"""
    url = f"{BASE_URL}/usuarios"
    res = requests.get(url)
    usuarios = []
    if res.status_code == 200:
        docs = res.json().get('documents', [])
        for doc in docs:
            f = doc.get('fields', {})
            u = {k: list(v.values())[0] for k, v in f.items()}
            u['id'] = doc['name'].split('/')[-1]
            
            # Super Admin vê todos / Admin vê apenas os da sua empresa
            if user_data['nivel'] == 'super':
                usuarios.append(u)
            elif user_data['nivel'] == 'admin' and u.get('empresa_id') == user_data['empresa_id']:
                usuarios.append(u)
    return usuarios

def buscar_todas_empresas():
    """Busca todas as empresas cadastradas (Apenas para Super Admin)"""
    url = f"{BASE_URL}/empresas"
    res = requests.get(url)
    empresas = []
    if res.status_code == 200:
        docs = res.json().get('documents', [])
        for doc in docs:
            f = doc.get('fields', {})
            e = {k: list(v.values())[0] for k, v in f.items()}
            e['id'] = doc['name'].split('/')[-1]
            empresas.append(e)
    return empresas
    
def resetar_senha_usuario(user_id, nova_senha):
    """Atualiza a senha de um usuário específico"""
    url = f"{BASE_URL}/usuarios/{user_id}?updateMask.fieldPaths=senha"
    payload = {
        "fields": {
            "senha": {"stringValue": nova_senha}
        }
    }
    try:
        res = requests.patch(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao resetar senha: {e}")
        return False

def eliminar_empresa_completa(id_empresa_doc, id_empresa_slug):
    """
    Remove o registro da empresa. 
    Nota: Em um sistema real, você também deletaria os leads vinculados a esse slug.
    """
    url = f"{BASE_URL}/empresas/{id_empresa_doc}"
    try:
        res = requests.delete(url)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao eliminar empresa: {e}")
        return False

def registrar_perda_lead(doc_id, motivo):
    """Versão simplificada e mais robusta para atualizar o status e motivo"""
    # Atualizamos o status e o motivo_perda simultaneamente
    url = f"{BASE_URL}/leads/{doc_id}?updateMask.fieldPaths=status&updateMask.fieldPaths=motivo_perda"
    
    payload = {
        "fields": {
            "status": {"stringValue": "Perdido"},
            "motivo_perda": {"stringValue": motivo}
        }
    }
    
    try:
        # Usamos PATCH para atualizar apenas esses dois campos
        res = requests.patch(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao registrar perda: {e}")
        return False