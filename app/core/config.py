from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
RABBITMQ_URI=os.getenv("RABBITMQ_URI")
MONGO_URI = os.getenv("MONGO_URI") 
DATABASE_NAME = "chat_database"