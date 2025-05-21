# router/reserva_json.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

router = APIRouter()
RESERVAS_JSON = Path("info/reservas.json")

class Reserva(BaseModel):
    nombre: str
    email: str
    fecha: str
    hora: str
    cancha: str

@router.post("/reservas/guardar")
def guardar_reserva(reserva: Reserva):
    try:
        nueva_reserva = reserva.dict()

        if RESERVAS_JSON.exists():
            with open(RESERVAS_JSON, "r", encoding="utf-8") as f:
                reservas = json.load(f)
        else:
            reservas = []

        reservas.append(nueva_reserva)

        with open(RESERVAS_JSON, "w", encoding="utf-8") as f:
            json.dump(reservas, f, indent=2, ensure_ascii=False)

        return {"mensaje": "Reserva guardada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar reserva: {e}")


@router.get("/reservas")
def obtener_reservas():
    try:
        if not RESERVAS_JSON.exists():
            return []

        with open(RESERVAS_JSON, "r", encoding="utf-8") as f:
            reservas = json.load(f)
        return reservas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer reservas: {e}")
