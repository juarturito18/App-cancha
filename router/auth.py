from fastapi import APIRouter, Depends, HTTPException, status, Form
from pydantic import BaseModel, EmailStr, validator
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import json
from pathlib import Path

# Configuración
algoritmo = "HS256"
access_token_time = 1  # minutos
secret = "f3c26f15a5b7484570ad1bfbf9b08df15a9a9ffbd3b801cfbaee5ea2a1f3e142"

# Rutas
router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="/login")
crypt = CryptContext(schemes=["bcrypt"])

# Modelos
class RegisterModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    age: int
    password: str

    @validator('password')
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

    @validator('age')
    def age_must_be_adult(cls, v):
        if v < 18:
            raise ValueError('Debes ser mayor de 18 años para registrarte')
        return v

class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    age: int

# Funciones auxiliares
USERS_PATH = Path(__file__).parent.parent / "data" / "users.json"


def load_users():
    with open(USERS_PATH, 'r') as f:
        return json.load(f)


def save_users(db: dict):
    with open(USERS_PATH, 'w') as f:
        json.dump(db, f, indent=2)

# Excepción de credenciales inválidas
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales de autenticación inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)

# Dependencia de autenticación
def auth_user(token: str = Depends(oauth2)) -> User:
    try:
        payload = jwt.decode(token, secret, algorithms=[algoritmo])
        first_name: str = payload.get("sub")
        if not first_name:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_data = load_users().get(first_name)
    if not user_data:
        raise credentials_exception
    return User(**user_data)

# Endpoints
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    users = load_users()
    user_db = users.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="Usuario incorrecto")

    if not crypt.verify(form.password, user_db['password']):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    expire = datetime.utcnow() + timedelta(minutes=access_token_time)
    token_data = {"sub": user_db['first_name'], "exp": expire}
    token = jwt.encode(token_data, secret, algorithm=algoritmo)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register")
async def register(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...),
    age: int = Form(...),
    password: str = Form(...)
):
    # Validación de campos
    data = RegisterModel(
        first_name=first_name,
        last_name=last_name,
        email=email,
        age=age,
        password=password
    )

    db = load_users()
    # usar first_name como username
    username = data.first_name
    if username in db:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    hashed = crypt.hash(data.password)
    db[username] = {
        "username": username,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "age": data.age,
        "password": hashed
    }
    save_users(db)
    return {"message": "Usuario registrado correctamente"}

@router.get("/users/me")
async def me(user: User = Depends(auth_user)):
    return user