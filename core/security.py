import hashlib

def criptografar_senha(senha):
    """Transforma a senha em texto puro num hash seguro"""
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha_digitada, senha_do_banco):
    """Compara a senha digitada com o hash guardado no banco"""
    return criptografar_senha(senha_digitada) == senha_do_banco
