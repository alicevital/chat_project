from fastapi import FastAPI
from app.controllers.user_controller import UserRouter

# Criação da API
app = FastAPI(title="Chat API")

# Rotas da API
app.include_router(UserRouter)