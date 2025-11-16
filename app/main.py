from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.controllers.user_controller import UserRouter
from app.controllers.ws_controller import router


app = FastAPI(title="PixelChat")

app.include_router(UserRouter)
app.include_router(router)

app.mount("/styles", StaticFiles(directory="app/views/styles"), name="styles") 

app.mount("/html", StaticFiles(directory="app/views/html", html=True), name="html") 


@app.get("/html/cadastro.html") 
def root(): 
    return FileResponse("app/views/html/cadastro.html") 