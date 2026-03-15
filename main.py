import os
import random
from flask import Flask, request
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

def logica_psicologica(testo):
    testo = testo.lower()
    parole = testo.split()
    positive = ['grazie', 'bravo', 'bello', 'complimenti', 'ottimo', 'storia']
    is_buono = any(p in testo for p in positive)

    if is_buono:
        return "Grazie mille per le tue parole! Mi fa piacere che ti piaccia. 😊"
    
    tecnica = random.randint(1, 5)
    if tecnica == 1: # ECO
        return f"Fammi capire meglio... quindi { ' '.join(parole[-3:]) }?"
    elif tecnica == 2: # MIRRORING
        return f"Capisco il tuo punto di vista. Quindi per te: '{testo}'"
    elif tecnica == 3: # RIMESCOLAMENTO
        random.shuffle(parole)
        return f"Interessante rimescolare i fatti: {' '.join(parole[:5])}?"
    elif tecnica == 4: # VALIDAZIONE
        return "Sembra che questa situazione ti provochi fastidio. Posso comprendere la tua reazione."
    else: # DOMANDA APERTA
        return "Cosa ti spinge a reagire con questo tono specifico? Vorrei capire meglio."

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Token Errato", 403

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if data.get("object") == "page":
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if change["field"] == "feed" and change.get("value", {}).get("item") == "comment":
                    comment_id = change["value"]["comment_id"]
                    comment_text = change["value"].get("message", "")
                    if change["value"].get("from", {}).get("id") != entry["id"]:
                        risposta = logica_psicologica(comment_text)
                        url = f"https://graph.facebook.com{comment_id}/comments"
                        requests.post(url, data={'message': risposta, 'access_token': PAGE_ACCESS_TOKEN})
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
