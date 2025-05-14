from flask import Flask, request, jsonify, render_template, send_from_directory
from keras.models import load_model
from fpdf import FPDF
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
import pickle
import json
import random
import os
import sys

nltk.download('punkt')
nltk.download('wordnet')

# Configurar static_folder para que apunte a la carpeta static principal
app = Flask(__name__, template_folder='html/main_page', static_folder='APP_Cancha/static')

# Cargar modelo y archivos del chatbot (asegúrate de que las rutas son correctas)
lemmatizer = WordNetLemmatizer()
try:
    intents = json.loads(open("info/respuestas.json", encoding="utf-8").read())
    words = pickle.load(open("chat-bot/words.pkl", "rb"))
    clases = pickle.load(open("chat-bot/clases.pkl", "rb"))
    model = load_model("chat-bot/Chatbot_cancha.keras")
except FileNotFoundError as e:
    print(f"Error al cargar archivos del chatbot: {e}")
    intents = {"intents": []}
    words = []
    clases = []
    model = None

# Archivos de datos (asegúrate de que las rutas son correctas)
RESERVAS_FILE = "info/reserva_data.json"

# Inicializar archivos si no existen
if not os.path.exists(RESERVAS_FILE):
    with open(RESERVAS_FILE, 'w') as f:
        json.dump({}, f)

# --- Procesamiento del mensaje para el chatbot ---
def clean_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_words(sentence):
    sentence_words = clean_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, word in enumerate(words):
            if word == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    if model is None or not words or not clases:
        return "fallback"
    bow = bag_words(sentence)
    res = model.predict(np.array([bow]))[0]
    tag = clases[np.argmax(res)]
    return tag

def get_response(tag, intents_json):
    for i in intents_json["intents"]:
        if i["tag"] == tag:
            return random.choice(i["responses"])
    return "Lo siento, no entendí o no puedo procesar tu solicitud en este momento."

# --- Generación de PDF ---
def generar_pdf(usuario, cancha, hora):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Comprobante de Reserva", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Usuario: {usuario}", ln=2)
    pdf.cell(200, 10, txt=f"Cancha: {cancha}", ln=3)
    pdf.cell(200, 10, txt=f"Hora reservada: {hora}", ln=4)
    pdf.cell(200, 10, txt=f"Código: {random.randint(1000,9999)}", ln=5)
    pdf_output_path = os.path.join("/content/", f"comprobante_{usuario}_{random.randint(100,999)}.pdf")
    pdf.output(pdf_output_path)
    return pdf_output_path

# --- Rutas de la aplicación ---

@app.route("/")
def main_page():
    return render_template("main_page.html")

@app.route("/canchas_mapa")
def canchas_mapa():
    # CAMBIO: Leer el contenido del archivo HTML del mapa generado por Mapa_canchas.py
    # Asumiendo que Mapa_canchas.py guarda el archivo en la misma carpeta que app.py
    mapa_html_path = os.path.join(os.path.dirname(__file__), 'Canchas sinteticas.html')
    try:
        with open(mapa_html_path, 'r', encoding='utf-8') as f:
            mapa_html_content = f.read()
        return mapa_html_content
    except FileNotFoundError:
        return "Error: No se encontró el archivo del mapa (Canchas sinteticas.html). Asegúrate de que Mapa_canchas.py lo genera en la misma carpeta que app.py y que has ejecutado Mapa_canchas.py previamente."
    except Exception as e:
        return f"Error al leer el archivo del mapa: {e}"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get('message')
    if not msg:
        return jsonify({"tag": "error", "answer": "Mensaje vacío."})
    tag = predict_class(msg)
    response_text = get_response(tag, intents)
    return jsonify({"tag": tag, "answer": response_text})

@app.route("/reservar", methods=["POST"])
def reservar():
    data = request.get_json()
    cancha = data.get("cancha")
    hora = data.get("hora")
    usuario = data.get("usuario", "Usuario Desconocido")

    with open(RESERVAS_FILE, 'r') as f:
        reservas = json.load(f)

    reservas.setdefault(cancha, []).append({"hora": hora, "usuario": usuario})
    with open(RESERVAS_FILE, 'w') as f:
        json.dump(reservas, f, indent=4)

    pdf_path = generar_pdf(usuario, cancha, hora)
    return jsonify({"message": "Reserva confirmada", "cancha": cancha, "hora": hora, "pdf_path": pdf_path})

# Ruta para servir archivos estáticos (si es necesario para el PDF)
@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory("/content/", filename, as_attachment=True)

if __name__ == "__main__":
    os.makedirs("/content/", exist_ok=True)
    app.run(debug=True)
