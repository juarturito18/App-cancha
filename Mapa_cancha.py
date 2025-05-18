import folium as fl
import pandas as pd

data = pd.read_csv("info/canchas_barranquilla.csv")


name = list(data["Nombre"])
barrio = list(data["Barrio"])
tipo = list(data["Tipo"])
lat = list(data["Latitud"])
lon = list(data["Longitud"])

for i in range(3, 9):
    # Crear un nuevo mapa por cada intervalo horario
    mapa = fl.Map(location=[10.96854, -74.78132], zoom_start=14, tiles="CartoDB Positron")
    fl.TileLayer('openstreetmap', name='Openstreetmap').add_to(mapa)

    dis = list(data[f"{i}-{i+1}pm"])
    color = ["green" if c else "red" for c in dis]

    marker = fl.FeatureGroup(name="Disponibilidad").add_to(mapa)

    for r, (lt, ln, nm, tp, br, d) in enumerate(zip(lat, lon, name, tipo, barrio, dis)):
        message = "<a href='http://127.0.0.1:8000/reservar/reserva.html' target='_blank'>Reserva aquí</a>" if d else "La cancha se encuentra ocupada"

        if color[r] == "green":
            icon_path = "championship (1).png"  
        else:
            icon_path = "championship (2).png"  

        icon = fl.CustomIcon(
            icon_image=icon_path,
            icon_size=(40, 40))

        fl.Marker(
            location=[lt, ln],
            popup=f"""<strong>Cancha:</strong> "{nm}", <br><strong>Barrio:</strong> "{br}"<br>{message}""",
            tooltip=f"<strong>Tipo de cancha:</strong> {tp}",
            icon=icon  # Aquí usamos el ícono personalizado
        ).add_to(marker)

    fl.LayerControl().add_to(mapa)
    mapa.save(f"canchas-sinteticas{i}-{i+1}PM.html")

