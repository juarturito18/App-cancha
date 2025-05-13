from flask import Flask, render_template, request, jsonify
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import nltk
import numpy as np
import pickle, json, random, os

nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__, static_url_path='/static')

lemmatizer = WordNetLemmatizer()
intents = json.load(open(r"info\respuestas.json", encoding="utf-8"))
words = pickle.load(open(r"chat-bot\words.pkl", "rb"))
clases = pickle.load(open(r"chat-bot\clases.pkl", "rb"))
model = load_model(r"chat-bot\Chatbot_cancha.keras")

RESERVAS_FILE = r"info\reserva_data.json"
if not os.path.exists(RESERVAS_FILE):
    with open(RESERVAS_FILE, 'w') as f:
        json.dump({}, f)

@app.route("/")
def main_page():
    return render_template("main_page.html")

@app.route("/reserva")
def reserva():
    # Puedes filtrar solo las canchas disponibles si manejas el CSV en el backend
    canchas = ["Cancha Sintética El Campito", "Cancha de Fútbol San Isidro", "Cancha de Microfútbol Las Palmas", "Cancha Sintética Brasileirao", "Cancha de Fútbol Estadio Metropolitano"]
    return render_template("reserva.html", canchas=canchas)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get('message', '')
    tag = predict_class(msg)
    response = get_response(tag, intents)

    # Simulación de extracción de datos para llenar el formulario
    cancha = "Cancha Sintética El Campito" if "cancha" in msg.lower() else None
    hora = "18:00" if "6" in msg or "tarde" in msg else None
    usuario = "Juan" if "juan" in msg.lower() else None

    return jsonify({"tag": tag, "response": response, "cancha": cancha, "hora": hora, "usuario": usuario})

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

    return jsonify({"message": "Reserva registrada correctamente"})

# Funciones auxiliares
def clean_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(w.lower()) for w in sentence_words]

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
    return clases[np.argmax(res)]

def get_response(tag, intents_json):
    for i in intents_json["intents"]:
        if i["tag"] == tag:
            return random.choice(i["responses"])
    return "No entendí, ¿puedes repetirlo?"

if __name__ == "__main__":
    app.run(debug=True)
