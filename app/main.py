from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import os
from app.infra.providers.rabbitmq_private import init_rabbit


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI(title="PixelChat")

from app.controllers.global_chat_controller import GlobalRouter, start_global_chat
from app.controllers.user_controller import UserRouter
from app.controllers.chat_controller import PrivateRouter

app.include_router(UserRouter)

@app.on_event("startup")
async def startup_event():
    # inicializa rabbitMQ no startup (await)
    try:
        await init_rabbit()
        print("RabbitMQ init ok")
    except Exception as e:
        print("Falha ao inicializar RabbitMQ:", e)

app.include_router(PrivateRouter)


@app.on_event("startup")
async def startup():
    await start_global_chat()
    
app.include_router(GlobalRouter)

app.mount("/styles", StaticFiles(directory="app/views/styles"), name="styles") 

app.mount("/html", StaticFiles(directory="app/views/html", html=True), name="html") 


@app.get("/html/cadastro.html") 
def root(): 
    return FileResponse("app/views/html/cadastro.html")