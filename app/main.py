from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.controllers.user_controller import UserRouter


# Criação da API
app = FastAPI(title="PixelChat")

# Rotas da API
app.include_router(UserRouter)


# Front-End
# Adicione esta linha para montar o diretório de estilos (CSS) 
app.mount("/styles", StaticFiles(directory="app/views/styles"), name="styles") 

# Adicione esta linha para montar o diretório HTML em /html 
app.mount("/html", StaticFiles(directory="app/views/html", html=True), name="html") 


@app.get("/html/cadastro.html") 
def root(): 
    return FileResponse("app/views/html/cadastro.html")