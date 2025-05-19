from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from pydantic import BaseModel

app = FastAPI()

# Permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringirlo si gustas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USERS_FILE = "users.json"

# Modelo para los datos del usuario
class User(BaseModel):
    username: str
    password: str

# Función para leer y guardar usuarios
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

@app.post("/register")
async def register(user: User):
    users = load_users()
    if any(u["username"] == user.username for u in users):
        raise HTTPException(status_code=400, detail="Usuario ya existe.")
    users.append(user.dict())
    save_users(users)
    return {"message": "Registro exitoso"}

@app.post("/login")
async def login(user: User):
    users = load_users()
    if any(u["username"] == user.username and u["password"] == user.password for u in users):
        return {"message": "Login exitoso"}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")
