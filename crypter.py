from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")

fernet = Fernet(FERNET_KEY.encode())

def encrypt(key : str):
    return fernet.encrypt(key.encode()).decode()

def decrypt(key : str): 
    return fernet.decrypt(key.encode()).decode()
