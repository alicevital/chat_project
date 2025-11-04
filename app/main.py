from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.controllers.message_controller import MessageRouter
from app.controllers.chat_controller import ChatRouter
from app.controllers.user_controller import UserRouter


# Criação da API
app = FastAPI(title="Chat API")

# Rotas da API
app.include_router(UserRouter)
app.include_router(MessageRouter)
app.include_router(ChatRouter)


# Front-End
@app.get("/")
def root():
    return FileResponse("app/views/html/cadastro.html")