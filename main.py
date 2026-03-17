import os
from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
BOT_USER_ID = os.environ.get('BOT_USER_ID')  # Add your bot's user ID

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token Errato", 403

    if request.method == 'POST':
        data = request.json
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    # Check if it's a new comment
                    if (change.get('field') == 'feed' and 
                        change['value'].get('item') == 'comment' and 
                        change['value'].get('verb') == 'add'):
                        
                        comment_id = change['value'].get('comment_id')
                        sender_id = change['value'].get('sender_id')
                        
                        # Avoid bot replying to itself
                        if sender_id and sender_id != BOT_USER_ID:
                            send_reply(comment_id, "Grazie per il tuo commento! Siamo operativi.")
        return "EVENT_RECEIVED", 200

def send_reply(comment_id, text):
    url = f"https://graph.facebook.com/v18.0/{comment_id}/comments"
    payload = {'message': text, 'access_token': PAGE_ACCESS_TOKEN}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Reply sent successfully to comment {comment_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending reply: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
