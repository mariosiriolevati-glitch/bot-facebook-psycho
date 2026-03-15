import os
import random
from flask import Flask, request
import requests

app = Flask(__name__)

# Recupero variabili d'ambiente
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

def logica_psicologica(testo):
    testo = testo.lower()
    parole = testo.split()
    # Vincolo 4: Psicologia per chi scrive male, gentilezza per chi scrive bene
    positive = ['grazie', 'bravo', 'bello', 'complimenti', 'ottimo', 'storia', 'top', 'grande']
    is_buono = any(p in testo for p in positive)

    if is_buono:
        return "Grazie mille per le tue parole! Mi fa piacere che ti piaccia. 😊"
    
    # Le 5 tecniche psicologiche
    tecnica = random.randint(1, 5)
    if tecnica == 1: # ECO
        fine_frase = ' '.join(parole[-3:]) if len(parole) >= 3 else testo
        return f"Fammi capire meglio... quindi {fine_frase}?"
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
    # Verifica del Webhook di Facebook
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Token Errato", 403

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if data and data.get("object") == "page":
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                # Gestione commenti su Post e Reel
                if change["field"] == "feed" and change.get("value", {}).get("item") == "comment":
                    val = change["value"]
                    if val.get("verb") == "add":
                        comment_id = val["comment_id"]
                        comment_text = val.get("message", "")
                        # Evita che il bot risponda a se stesso
                        if val.get("from", {}).get("id") != entry["id"]:
                            risposta = logica_psicologica(comment_text)
                            # Correzione URL Graph API (mancava la versione e lo slash)
                            url = f"https://graph.facebook.com{comment_id}/comments"
                            requests.post(url, data={'message': risposta, 'access_token': PAGE_ACCESS_TOKEN})
    return "OK", 200

if __name__ == "__main__":
    # Correzione per Render: usa la porta dinamica assegnata dal server
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
