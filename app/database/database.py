from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os


MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:root@localhost:27017")  # Default local com auth
DATABASE_NAME = "chat_database"
# no computador: mongodb://root:root@localhost:27017 em produção: mongodb+srv://root:<db_password>@cluster0.i6ffdcs.mongodb.net/

client = None

def get_mongo_client():
    global client

    if client is None:
        try:

            print(f"Conectando a: {MONGO_URI}")

            client = MongoClient(MONGO_URI)

            client.admin.command('ping')  

            print("Conectado ao MongoDB com auth!")

        except ConnectionFailure as e:

            print(f"Falha na conexão: {e}")

            raise Exception("Falha na conexão com MongoDB")
        
    return client

def get_database():
    client = get_mongo_client()
    return client[DATABASE_NAME]
