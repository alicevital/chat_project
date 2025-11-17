# PIXELCHAT - Plataforma de Chat em Tempo Real

Plataforma de chat desenvolvida com **Python**, **FastAPI**, **WebSockets** e **RabbitMQ**, permitindo comunicação em tempo real entre usuários, com suporte a histórico de mensagens e autenticação segura via JWT.

## Requisitos Funcionais

### RF1 — Cadastro e Autenticação
- Usuários podem criar contas e realizar login.
- Autenticação via **JWT** ou estratégia segura equivalente.
- Sessões compatíveis com conexões **WebSocket**.

### RF2 — Comunicação em Tempo Real
- Envio e recebimento de mensagens instantâneas via **WebSockets**.
- **Broadcast:** envio de mensagens para todos os usuários conectados.
- **Mensagens privadas:** comunicação direta entre dois usuários.
- Participação em **salas** com histórico acessível.

### RF3 — Filtragem e Persistência de Mensagens
- Todas as mensagens são armazenadas em banco de dados.
- Recuperação de histórico (público e privado).
- Cada mensagem inclui:
  - Remetente
  - Destinatário (ou broadcast)
  - Timestamp
  - Conteúdo

### - Como rodar
Clone o repositório na sua máquina:
```bash
git clone https://github.com/alicevital/chat_project.git
```
Rode o comando para criar as imagens e rodar os containers: 
```bash
docker compose up --build -d
```
### - Alguns blocos de código do projeto

Importa de um arquivo de configuração as variáveis de ambiente:
```python
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
```
Trecho do arquivo config.py onde carrega as variáveis de ambiente .env:
```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "chat_database"
```
Rota de Login que verifica a autenticação:
```python
@UserRouter.post("/users/login")
def login(login_schema: LoginSchema, db=Depends(get_db)):
    repository = UserRepository(db)

    user = repository.get_user_by_email(login_schema.email)

    if not user or not hash_verifier(login_schema.password, user["password"]):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    else:
        access_token = create_token(user["_id"])
        return {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "access_token": access_token,
            "token_type": "Bearer" 
        }
```
