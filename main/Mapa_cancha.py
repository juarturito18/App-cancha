import folium as fl
import pandas as pd

data = pd.read_csv(r"C:\Users\Usuario\Documents\APP_Cancha\info\canchas_barranquilla.csv", skipinitialspace=True)


name = list(data["Nombre"])
barrio = list(data["Barrio"])
direc = list(data["Direccion"])
tipo = list(data["Tipo"])
lat = list(data["Latitud"])
lon = list(data["Longitud"])

for i in range(3, 9):
    # Crear un nuevo mapa por cada intervalo horario
    mapa = fl.Map(location=[10.96854, -74.78132], zoom_start=14, tiles="CartoDB Positron")
    fl.TileLayer('openstreetmap', name='Openstreetmap').add_to(mapa)

    dis = list(data[f"{i}-{i+1}pm"])

    marker = fl.FeatureGroup(name="Disponibilidad").add_to(mapa)

    for r, (lt, ln, nm, tp, br, d, dr) in enumerate(zip(lat, lon, name, tipo, barrio, dis, direc)):
        message = "La cancha esta libre" if d else "La cancha se encuentra ocupada"

        if d:
            icon_path = "championship (1).png"  
        else:
            icon_path = "championship (2).png"  

        icon = fl.CustomIcon(
            icon_image=icon_path,
            icon_size=(40, 40))

        fl.Marker(
            location=[lt, ln],
            popup=f"""<strong>Cancha:</strong> "{nm}", <br><strong>Barrio:</strong> "{br}",<br><strong>Dirrección:</strong> "{dr}",<br>{message}""",
            tooltip=f"<strong>Tipo de cancha:</strong> {tp}",
            icon=icon  # Aquí usamos el ícono personalizado
        ).add_to(marker)

    fl.LayerControl().add_to(mapa)
    mapa.save(f"canchas-sinteticas{i}-{i+1}PM.html")

