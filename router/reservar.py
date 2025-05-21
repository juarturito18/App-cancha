from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
from datetime import datetime

router = APIRouter()
RESERVAS_FILE_PATH = Path("info/reservas.json")

class Reserva(BaseModel):
    nombre: str
    email: str
    fecha: str
    hora: str
    cancha: str

def load_reservas_from_file() -> list[dict]:
    if not RESERVAS_FILE_PATH.exists():
        return []
    try:
        with open(RESERVAS_FILE_PATH, 'r', encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []
    except Exception:
        return []

def save_reservas_to_file(reservas_data: list[dict]):
    RESERVAS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESERVAS_FILE_PATH, 'w', encoding="utf-8") as f:
        json.dump(reservas_data, f, indent=2, ensure_ascii=False)

@router.get("/reservas/por_email")
async def obtener_reservas_por_email(email: str):
    all_reservas = load_reservas_from_file()
    
    if not isinstance(all_reservas, list):
        raise HTTPException(status_code=500, detail="Error interno al leer datos de reservas.")

    try:
        user_reservas = [r for r in all_reservas if isinstance(r, dict) and r.get("email") == email]
        return user_reservas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar reservas: {e}")

@router.post("/reservas/guardar")
async def guardar_reserva(reserva: Reserva):
    all_reservas = load_reservas_from_file()
    nueva_reserva = reserva.dict()
    
    if not isinstance(all_reservas, list):
        all_reservas = []

    all_reservas.append(nueva_reserva)

    try:
        save_reservas_to_file(all_reservas)
        return {"mensaje": "Reserva guardada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar reserva: {e}")

@router.delete("/reservas/eliminar")
async def eliminar_reserva(data: Reserva):
    all_reservas = load_reservas_from_file()

    if not all_reservas:
        raise HTTPException(status_code=404, detail="No existen reservas registradas")
    
    reserva_encontrada_obj = None
    for r_dict in all_reservas:
        if (
            r_dict.get("nombre") == data.nombre and
            r_dict.get("email") == data.email and
            r_dict.get("fecha") == data.fecha and
            r_dict.get("hora") == data.hora and
            r_dict.get("cancha") == data.cancha
        ):
            reserva_encontrada_obj = r_dict
            break
    
    if not reserva_encontrada_obj:
        raise HTTPException(status_code=404, detail="Reserva no encontrada para eliminar")

    try:
        reserva_dt_str = f"{data.fecha} {data.hora}"
        reserva_dt = datetime.strptime(reserva_dt_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha u hora inválido")

    ahora = datetime.now()
    diferencia = reserva_dt - ahora

    if diferencia.total_seconds() < 2 * 3600:
        raise HTTPException(status_code=403, detail="No se puede cancelar una reserva con menos de 2 horas de anticipación")

    reservas_filtradas = [r for r in all_reservas if r != reserva_encontrada_obj]

    try:
        save_reservas_to_file(reservas_filtradas)
        return {"mensaje": "Reserva eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar reserva: {e}")