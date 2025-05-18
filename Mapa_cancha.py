import folium as fl
import pandas as pd


mapa = fl.Map(location=[10.96854, -74.78132], zoom_start = 14, tiles = "CartoDB Positron")

fl.TileLayer('openstreetmap', name='Openstreetmap').add_to(mapa)

data = pd.read_csv("info\canchas_barranquilla.csv")
print(data.head(13))

name = list(data["Nombre"])
barrio = list(data["Barrio"])
tipo = list(data["Tipo"])
lat = list(data["Latitud"])
lon = list(data["Longitud"])
for i in range(3,9):
    dis = list(data[f"{i}-{i+1}pm"])

    color = []
    for c in dis:
        if c:
            color.append("green")
        else:
            color.append("red")

    marker = fl.FeatureGroup(name="markers").add_to(mapa)

    for r,(lt, ln, nm, tp, br, dis) in enumerate(zip(lat, lon, name, tipo, barrio, dis)):
        if color[r] == "green":
            message = "<a href = 'http://127.0.0.1:8000/reservar/reserva.html' target = '_blank'>Reserva aqui </a>"
        else:
            message = "La cancha se encuentra ocupada"
        fl.Marker(
            location=[lt,ln],
            popup = f"""<strong>Cancha: </strong>\"{nm}\", <br> <strong>barrio: </strong> \"{br}\" <br>  
            {message}""", 
            tooltip= f"<strong>Tipo de la cancha: </strong> {tp}",
            icon = fl.Icon(color= color[i], icon='soccer-ball-o', prefix='fa')
        ).add_to(marker)

    fl.LayerControl().add_to(mapa)
    mapa.save(f"Canchas sinteticas{i-2}.html")