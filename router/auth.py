from fastapi import APIRouter, Depends, HTTPException, status, Form
from pydantic import BaseModel, EmailStr, validator
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Optional

# Configuración
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tiempo de expiración del token aumentado
SECRET_KEY = "f3c26f15a5b7484570ad1bfbf9b08df15a9a9ffbd3b801cfbaee5ea2a1f3e142" # Mantén tu secret key

# Rutas
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login") # Asegúrate que tokenUrl coincida con tu endpoint de login en el router principal si es diferente
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos Pydantic
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    age: int

class UserCreate(UserBase):
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

class UserInDB(UserBase):
    hashed_password: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    age: int

# Funciones auxiliares para manejar users.json
# Asumiendo que auth.py está en una carpeta (ej: 'router') y users.json en la raíz del proyecto.
USERS_FILE_PATH = Path(__file__).resolve().parent.parent / "users.json"

def load_users_db():
    """Carga la base de datos de usuarios desde el archivo JSON."""
    if not USERS_FILE_PATH.exists():
        return {}
    with open(USERS_FILE_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users_db(users_db: dict):
    """Guarda la base de datos de usuarios en el archivo JSON."""
    with open(USERS_FILE_PATH, 'w') as f:
        json.dump(users_db, f, indent=2)

def get_user(db: dict, email: str) -> Optional[dict]:
    """Obtiene un usuario de la 'base de datos' por email."""
    return db.get(email)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña plana contra la hasheada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un nuevo token de acceso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Decodifica el token y obtiene el usuario actual."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    users_db = load_users_db()
    user_dict = get_user(users_db, token_data.email)
    if user_dict is None:
        raise credentials_exception
    # Excluir 'hashed_password' antes de pasarlo a UserResponse
    user_info_for_response = {k: v for k, v in user_dict.items() if k != 'hashed_password'}
    return UserResponse(**user_info_for_response)


# Endpoints de Autenticación

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login. Espera 'username' (que será el email) y 'password'.
    Devuelve un token de acceso.
    """
    users_db = load_users_db()
    user = get_user(users_db, form_data.username) # form_data.username será el email
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "firstName": user["first_name"], "lastName": user["last_name"]}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "first_name": user["first_name"]}

@router.post("/register", response_model=UserResponse)
async def register_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...), # Pydantic valida el formato del email
    age: int = Form(...),
    password: str = Form(...)
):
    """Endpoint de registro de nuevos usuarios."""
    try:
        user_data = UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            age=age,
            password=password  # La validación de longitud y edad se hace en UserCreate
        )
    except ValueError as e: # Captura errores de validación de Pydantic
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    users_db = load_users_db()
    if user_data.email in users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado.")

    hashed_password = get_password_hash(user_data.password)
    
    new_user_data_for_db = {
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "age": user_data.age,
        "hashed_password": hashed_password
    }
    users_db[user_data.email] = new_user_data_for_db
    save_users_db(users_db)

    return UserResponse(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        age=user_data.age
    )

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """Endpoint para obtener la información del usuario actualmente logueado."""
    return current_user
