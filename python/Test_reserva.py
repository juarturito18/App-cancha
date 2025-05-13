from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

@app.route("/reservar", methods=["GET", "POST"])
def reservar():
    if request.method == "POST":
        # Obtener datos del formulario
        usuario = request.form["usuario"]
        cancha = request.form["cancha"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        # Aquí podrías guardar la reserva en una base de datos o lista
        reserva = {
            "usuario": usuario,
            "cancha": cancha,
            "fecha": fecha,
            "hora": hora
        }

        return jsonify({"mensaje": "Reserva creada con éxito", "reserva": reserva}), 201

    # Si se accede por GET, mostrar formulario
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reservar Cancha</title>
         <link rel="stylesheet" href="style_reserva.css">
    </head>
    <body>
        <h1>Formulario de Reserva</h1>
        <form action="/reservar" method="POST">
            Usuario: <input type="text" name="usuario"><br><br>
            Cancha: <input type="text" name="cancha"><br><br>
            Fecha: <input type="date" name="fecha"><br><br>
            Hora: <input type="time" name="hora"><br><br>
            <button type="submit">Reservar</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True)
