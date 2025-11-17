from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
MONGO_URI = os.getenv("MONGO_URI") # no computador: mongodb://root:root@localhost:27017 em produção: mongodb+srv://root:<db_password>@cluster0.i6ffdcs.mongodb.net/
DATABASE_NAME = "chat_database"