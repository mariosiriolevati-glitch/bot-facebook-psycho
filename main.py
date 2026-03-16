import os
import random
from flask import Flask, request
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

def logica_psicologica(testo):
    testo = testo.lower()
    positive = ['grazie', 'bravo', 'bello', 'complimenti', 'ottimo', 'storia', 'top', 'grande', 'wow']
    is_buono = any(p in testo for p in positive)

    if is_buono:
        return "Grazie mille per le tue parole! Mi fa piacere che ti piaccia. 😊"
    
    parole = testo.split()
    tecnica = random.randint(1, 5)
    if tecnica == 1:
        fine_frase = ' '.join(parole[-3:]) if len(parole) >= 3 else testo
        return f"Fammi capire meglio... quindi {fine_frase}?"
    elif tecnica == 2:
        return f"Capisco il tuo punto di vista. Quindi per te: '{testo}'"
    elif tecnica == 3:
        random.shuffle(parole)
        return f"Interessante rimescolare i fatti: {' '.join(parole[:5])}?"
    elif tecnica == 4:
        return "Sembra che questa situazione ti provochi fastidio. Posso comprendere la tua reazione."
    else:
        return "Cosa ti spinge a reagire con questo tono specifico? Vorrei capire meglio."

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Token Errato", 403

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    # Log per vedere cosa arriva da Facebook
    print(f"DEBUG: Payload ricevuto -> {data}")

    if data and data.get("object") == "page":
        for entry in data["entry"]:
            page_id = entry.get("id")
            for change in entry.get("changes", []):
                if change["field"] == "feed":
                    val = change.get("value", {})
                    # Verifichiamo che sia un NUOVO commento e non una modifica/cancellazione
                    if val.get("item") == "comment" and val.get("verb") == "add":
                        comment_id = val.get("comment_id")
                        comment_text = val.get("message", "")
                        sender_id = val.get("from", {}).get("id")

                        # Evita che il bot risponda a se stesso confrontando l'ID del mittente con l'ID della pagina
                        if sender_id != page_id:
                            risposta = logica_psicologica(comment_text)
                            
                            # URL con versione API e headers
                            url = f"https://graph.facebook.com{comment_id}/comments"
                            payload = {'message': risposta}
                            params = {'access_token': PAGE_ACCESS_TOKEN}
                            
                            try:
                                r = requests.post(url, params=params, json=payload)
                                print(f"DEBUG - Risposta inviata a {comment_id}")
                                print(f"DEBUG - Esito Meta: {r.status_code} - {r.text}")
                            except Exception as e:
                                print(f"ERROR: Fallimento invio -> {e}")
                            
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
