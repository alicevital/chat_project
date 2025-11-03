from fastapi import FastAPI
from app.controllers.user_controller import UserRouter
from app.controllers.message_controller import MessageRouter
from app.controllers.chat_controller import ChatRouter

# Criação da API
app = FastAPI(title="Chat API")

# Rotas da API
app.include_router(UserRouter)
app.include_router(MessageRouter)
app.include_router(ChatRouter)