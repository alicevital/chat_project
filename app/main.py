from fastapi import FastAPI
from app.controllers.user_controller import UserRouter
from fastapi.responses import FileResponse

# Criação da API
app = FastAPI(title="Chat API")

# Rotas da API
app.include_router(UserRouter)


# Front-End
@app.get("/")
def root():
    return FileResponse("app/views/html/cadastro.html")