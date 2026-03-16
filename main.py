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
    positive = ['grazie', 'bravo', 'bello', 'complimenti', 'ottimo', 'storia', 'top', 'grande', 'wow']
    is_buono = any(p in testo for p in positive)

    if is_buono:
        return "Grazie mille per le tue parole! Mi fa piacere che ti piaccia. 😊"
    
    parole = testo.split()
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
    # Verifica del Webhook per Facebook
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Token Errato", 403

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    # LOG FONDAMENTALE: Vedremo su Render cosa ci invia Facebook
    print(f"--- NOTIFICA RICEVUTA: {data}")

    if data and data.get("object") == "page":
        for entry in data["entry"]:
            page_id = entry.get("id")
            for change in entry.get("changes", []):
                # Gestione commenti sul feed (Post e Reel)
                val = change.get("value", {})
                if change["field"] == "feed" and val.get("item") == "comment" and val.get("verb") == "add":
                    
                    comment_id = val.get("comment_id")
                    comment_text = val.get("message", "")
                    sender_id = val.get("from", {}).get("id")

                    # Evita che il bot risponda a se stesso
                    if sender_id != page_id:
                        risposta = logica_psicologica(comment_text)
                        
                        # URL CORRETTO con versione API (v21.0 è la più recente stabile)
                        url = f"https://graph.facebook.com{comment_id}/comments"
                        
                        payload = {'message': risposta}
                        params = {'access_token': PAGE_ACCESS_TOKEN}
                        
                        try:
                            r = requests.post(url, params=params, json=payload)
                            print(f"DEBUG - Risposta inviata a: {comment_id}")
                            print(f"DEBUG - Esito Meta: {r.status_code} - {r.text}")
                        except Exception as e:
                            print(f"ERRORE INVIO: {e}")
                    else:
                        print("DEBUG - Messaggio ignorato: è un commento del bot stesso.")
                            
    return "OK", 200

if __name__ == "__main__":
    # Render usa la porta 10000 di default
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
