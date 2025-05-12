import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open(r"APP_Cancha\respuestas.json").read())

words = pickle.load(open("words.pkl","rb"))
clases = pickle.load(open("clases.pkl", "rb"))
model = load_model("Chatbot_cancha.keras")

def clean_sentence(sentence): 
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_words(sentence):
    sentence_words = clean_sentence(sentence)
    bag = [0]*len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word  == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_words(sentence)
    res = model.predict(np.array([bow]))[0]
    max_index = np.where(res == np.max(res))[0][0]
    category = clases[max_index]
    return category

def get_response(tag, intents_json):
    list_of_intents = intents_json["intents"]
    result = ""
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i["responses"])

    return result

while True:
    message = input("-->")
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(res)

    if message.lower() in ["adios", "hasta luego", "termine", "esto es todo", "acabe"]:
        break

