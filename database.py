import requests
from datetime import datetime, timezone

# --- CONFIGURAÇÃO ---
PROJECT_ID = "gscomunicacoes-91512"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

def buscar_documento(colecao, campo, valor):
    """Busca um documento específico filtrando por um campo (Ex: login por email)"""
    url = f"{BASE_URL}/{colecao}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            docs = res.json().get('documents', [])
            for doc in docs:
                f = doc.get('fields', {})
                # Verifica se o valor do campo bate com o esperado
                if f.get(campo, {}).get('stringValue') == valor:
                    data = {k: list(v.values())[0] for k, v in f.items()}
                    data['id'] = doc['name'].split('/')[-1]
                    return data
        return None
    except Exception as e:
        print(f"Erro ao buscar documento: {e}")
        return None

def salvar_no_firebase(colecao, dados):
    """Salva um novo documento garantindo o formato de timestamp para leads"""
    payload = {"fields": {}}
    
    for k, v in dados.items():
        payload["fields"][k] = {"stringValue": str(v)}
    
    # IMPORTANTE: Grava data como timestampValue para permitir ordenação e gráficos
    if colecao == "leads":
        data_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        payload["fields"]["data_criacao"] = {"timestampValue": data_utc}
        
    try:
        res = requests.post(f"{BASE_URL}/{colecao}", json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False

def atualizar_status_rest(doc_id, novo_status):
    """Atualiza apenas o campo 'status' via PATCH"""
    url = f"{BASE_URL}/leads/{doc_id}?updateMask.fieldPaths=status"
    payload = {"fields": {"status": {"stringValue": novo_status}}}
    try:
        res = requests.patch(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")
        return False

def registrar_perda_lead(doc_id, motivo):
    """Atualiza o status para 'Perdido' e registra o motivo da perda"""
    url = f"{BASE_URL}/leads/{doc_id}?updateMask.fieldPaths=status,motivo_perda"
    payload = {
        "fields": {
            "status": {"stringValue": "Perdido"},
            "motivo_perda": {"stringValue": motivo}
        }
    }
    try:
        res = requests.patch(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao registrar perda: {e}")
        return False

def eliminar_documento(colecao, doc_id):
    """Remove um documento permanentemente"""
    url = f"{BASE_URL}/{colecao}/{doc_id}"
    try:
        res = requests.delete(url)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao eliminar: {e}")
        return False

def buscar_leads_filtrados(user_data):
    """Busca leads aplicando multitenancy (segurança de dados por nível)"""
    url = f"{BASE_URL}/leads"
    try:
        res = requests.get(url)
        if res.status_code != 200: return []
            
        leads = []
        docs = res.json().get('documents', [])
        
        for doc in docs:
            f = doc.get('fields', {})
            # Extração dinâmica de valores do Firestore
            l = {k: list(v.values())[0] for k, v in f.items()}
            l['id'] = doc['name'].split('/')[-1]
            
            # Lógica de Hierarquia
            if user_data['nivel'] == 'super':
                leads.append(l)
            elif user_data['nivel'] == 'admin' and l.get('empresa_id') == user_data['empresa_id']:
                leads.append(l)
            elif user_data['nivel'] == 'vendedor' and l.get('vendedor_id') == user_data['email']:
                leads.append(l)
                
        return leads
    except Exception as e:
        print(f"Erro ao carregar leads: {e}")
        return []

def buscar_todos_usuarios(user_data):
    """Filtra usuários visíveis para o Admin logado"""
    url = f"{BASE_URL}/usuarios"
    try:
        res = requests.get(url)
        usuarios = []
        if res.status_code == 200:
            docs = res.json().get('documents', [])
            for doc in docs:
                f = doc.get('fields', {})
                u = {k: list(v.values())[0] for k, v in f.items()}
                u['id'] = doc['name'].split('/')[-1]
                
                if user_data['nivel'] == 'super' or (user_data['nivel'] == 'admin' and u.get('empresa_id') == user_data['empresa_id']):
                    usuarios.append(u)
        return usuarios
    except: return []

def buscar_todas_empresas():
    """Retorna lista de empresas (Acesso restrito Super Admin)"""
    url = f"{BASE_URL}/empresas"
    try:
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
    except: return []

def resetar_senha_usuario(user_id, nova_senha_hash):
    """Sobrescreve o campo senha com o novo hash gerado"""
    url = f"{BASE_URL}/usuarios/{user_id}?updateMask.fieldPaths=senha"
    payload = {"fields": {"senha": {"stringValue": nova_senha_hash}}}
    try:
        return requests.patch(url, json=payload).status_code == 200
    except: return False
