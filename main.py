import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Queste leggono i dati che hai messo su Render (Environment Variables)
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. Questa parte serve per il tasto "Verifica e Salva" su Facebook
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token Errato", 403

    # 2. Questa parte gestisce i commenti e risponde
    if request.method == 'POST':
        data = request.json
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    # Se è un nuovo commento
                    if change.get('field') == 'feed' and change['value'].get('item') == 'comment' and change['value'].get('verb') == 'add':
                        comment_id = change['value'].get('comment_id')
                        # Evita che il bot risponda a se stesso
                        if change['value'].get('from', {}).get('id') != entry.get('id'):
                            send_reply(comment_id, "Grazie per il tuo commento! Siamo operativi.")
        return "EVENT_RECEIVED", 200

def send_reply(comment_id, text):
    url = f"https://graph.facebook.com/{comment_id}/comments"
    payload = {'message': text, 'access_token': PAGE_ACCESS_TOKEN}
    requests.post(url, data=payload)

if __name__ == '__main__':
    # Render ha bisogno di questo per far funzionare l'indirizzo web
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
