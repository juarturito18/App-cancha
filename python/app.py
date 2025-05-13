from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
from keras.models import load_model
from fpdf import FPDF
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
import pickle
import json
import random
import os

nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__)
run_with_ngrok(app)

# Cargar modelo y archivos
lemmatizer = WordNetLemmatizer()
intents = json.loads(open("respuestas.json", encoding="utf-8").read())
words = pickle.load(open("words.pkl", "rb"))
clases = pickle.load(open("clases.pkl", "rb"))
model = load_model("Chatbot_cancha.keras")

RESERVAS_FILE = "reserva_data.json"
if not os.path.exists(RESERVAS_FILE):
    with open(RESERVAS_FILE, 'w') as f:
        json.dump({}, f)

# Procesamiento del mensaje
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
    bow = bag_words(sentence)
    res = model.predict(np.array([bow]))[0]
    tag = clases[np.argmax(res)]
    return tag

def get_response(tag, intents_json):
    for i in intents_json["intents"]:
        if i["tag"] == tag:
            return random.choice(i["responses"])
    return "Lo siento, no entendí."

# Rutas
@app.route("/")
def home():
    return "Chatbot Canchas funcionando. Usa /chat o /reservar"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get('message')
    tag = predict_class(msg)
    response = get_response(tag, intents)
    return jsonify({"tag": tag, "response": response})

@app.route("/reservar", methods=["POST"])
def reservar():
    data = request.get_json()
    cancha = data.get("cancha")
    hora = data.get("hora")
    usuario = data.get("usuario")

    with open(RESERVAS_FILE, 'r') as f:
        reservas = json.load(f)

    reservas.setdefault(cancha, []).append(hora)
    with open(RESERVAS_FILE, 'w') as f:
        json.dump(reservas, f)

    generar_pdf(usuario, cancha, hora)
    return jsonify({"message": "Reserva confirmada", "cancha": cancha, "hora": hora})

def generar_pdf(usuario, cancha, hora):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Comprobante de Reserva", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Usuario: {usuario}", ln=2)
    pdf.cell(200, 10, txt=f"Cancha: {cancha}", ln=3)
    pdf.cell(200, 10, txt=f"Hora reservada: {hora}", ln=4)
    pdf.cell(200, 10, txt=f"Código: {random.randint(1000,9999)}", ln=5)
    pdf.output("/content/comprobante.pdf")

if __name__ == "__main__":
    app.run()
