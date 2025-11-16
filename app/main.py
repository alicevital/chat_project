from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.controllers.user_controller import UserRouter
from app.controllers.ws_controller import ws_router


app = FastAPI(title="PixelChat",
              description='Plataforma de chats em tempo real',
              version="1.2.0")

app.include_router(UserRouter)
app.include_router(ws_router)
