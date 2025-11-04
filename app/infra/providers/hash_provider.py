from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'])


# Gerador de Hash do texto(senha do usuário)
def hash_generator(text):
    return pwd_context.hash(text)



# Vai verificar se o texto em questão (text) é o mesmo texto criptografado (hash)
def hash_verifier(text, hash):
    return pwd_context.verify(text, hash)