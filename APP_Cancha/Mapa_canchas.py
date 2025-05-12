import folium as fl
import pandas as pd
import random as rd

mapa = fl.Map(location=[10.96854, -74.78132], zoom_start = 14, tiles = "CartoDB Positron")

fl.TileLayer('openstreetmap', name='Openstreetmap').add_to(mapa)

data = pd.read_csv("canchas_barranquilla.csv")

name = list(data["Nombre"])
barrio = list(data["Barrio"])
tipo = list(data["Tipo"])
lat = list(data["Latitud"])
lon = list(data["Longitud"])


color = []
for i in range(0, len(name)):
    if rd.choice([True, False]):
        color.append("green")
    else:
        color.append("red")

marker = fl.FeatureGroup(name="markers").add_to(mapa)

for i,(lt, ln, nm, tp, br) in enumerate(zip(lat, lon, name, tipo, barrio)):
    if color[i] == "green":
        message = "<a href = 'https://github.com/juarturito18/First-app-with-python' target = '_blank'>Reserva aqui </a>"
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
mapa.save("Canchas sinteticas.html")