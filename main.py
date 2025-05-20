from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
from router.auth import router as auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar frontend estático
app.mount("/reservar", StaticFiles(directory="Reserva", html=True), name="frontend")
app.mount("/auth", StaticFiles(directory="registro", html=True), name="auth")

# Incluir rutas de auth
app.include_router(auth)

CSV_PATH = "info/canchas_barranquilla.csv"

hora_column_map = {
    "15:00": "3-4pm",
    "16:00": "4-5pm",
    "17:00": "5-6pm",
    "18:00": "6-7pm",
    "19:00": "7-8pm",
    "20:00": "8-9pm",
}

@app.get("/disponibles")
def disponibles(hora: str = Query(..., pattern="^1[5-9]:00|20:00$")):
    if hora not in hora_column_map:
        raise HTTPException(status_code=400, detail="Hora inválida")
    try:
        df = pd.read_csv(CSV_PATH)
        columna = hora_column_map[hora]
        disponibles = df[df[columna] == True]["Nombre"].tolist()
        return disponibles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer CSV: {e}")

class ReservaRequest(BaseModel):
    cancha: str
    hora: str

@app.post("/reservar")
def reservar(data: ReservaRequest):
    cancha = data.cancha
    hora = data.hora

    if hora not in hora_column_map:
        raise HTTPException(status_code=400, detail="Hora inválida")

    try:
        df = pd.read_csv(CSV_PATH)
        columna = hora_column_map[hora]
        row = df[df["Nombre"] == cancha]
        if row.empty:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")
        if not row.iloc[0][columna]:
            raise HTTPException(status_code=400, detail="Cancha ya reservada para esa hora")

        df.loc[df["Nombre"] == cancha, columna] = False
        df.to_csv(CSV_PATH, index=False)
        return {"mensaje": "Reserva realizada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar reserva: {e}")
