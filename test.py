from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# Configuración de JWT
SECRET_KEY = "supersecreto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Rutas y config inicial
app = FastAPI()
app.mount("/reservar", StaticFiles(directory="Reserva", html=True), name="frontend")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

CSV_PATH = "info/canchas_barranquilla.csv"
USERS_FILE = "users.json"

hora_column_map = {
    "15:00": "3-4pm",
    "16:00": "4-5pm",
    "17:00": "5-6pm",
    "18:00": "6-7pm",
    "19:00": "7-8pm",
    "20:00": "8-9pm",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilidades para usuarios
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username, password):
    users = load_users()
    user = users.get(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        users = load_users()
        if username not in users:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Modelos
class UserRegister(BaseModel):
    username: str
    password: str

class ReservaRequest(BaseModel):
    cancha: str
    hora: str

# Registro de usuarios
@app.post("/register")
def register(user: UserRegister):
    users = load_users()
    if user.username in users:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    users[user.username] = {
        "username": user.username,
        "password": get_password_hash(user.password)
    }
    save_users(users)
    return {"mensaje": "Usuario registrado correctamente"}

# Login
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# Obtener canchas disponibles
@app.get("/disponibles")
def obtener_canchas_disponibles(hora: str = Query(..., pattern="^1[5-9]:00|20:00$")):
    if hora not in hora_column_map:
        raise HTTPException(status_code=400, detail="Hora inválida")
    try:
        df = pd.read_csv(CSV_PATH)
        columna = hora_column_map[hora]
        disponibles = df[df[columna] == True]["Nombre"].tolist()
        return disponibles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer CSV: {e}")

# Reservar cancha (protegido con JWT)
@app.post("/reservar")
def reservar_cancha(data: ReservaRequest, username: str = Depends(get_current_user)):
    if data.hora not in hora_column_map:
        raise HTTPException(status_code=400, detail="Hora inválida")
    try:
        df = pd.read_csv(CSV_PATH)
        columna = hora_column_map[data.hora]
        row = df[df["Nombre"] == data.cancha]
        if row.empty:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")
        if not row.iloc[0][columna]:
            raise HTTPException(status_code=400, detail="Cancha ya reservada para esa hora")
        df.loc[df["Nombre"] == data.cancha, columna] = False
        df.to_csv(CSV_PATH, index=False)
        return {"mensaje": f"Reserva realizada correctamente por {username}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar reserva: {e}")
