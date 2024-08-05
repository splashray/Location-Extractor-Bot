from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_BOT_URL = f'https://api.telegram.org/bot{os.getenv("TELEGRAM_TOKEN")}'

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    command = data.get("command", "")
    chat_id = data.get("chat_id", "")

    if not command or not chat_id:
        return jsonify({"error": "Missing command or chat_id"}), 400

    url = f"{TELEGRAM_BOT_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": command
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return jsonify({"error": "Failed to send command to bot"}), 500

    return jsonify({"status": "Command sent successfully"}), 200

if __name__ == "__main__":
    app.run(port=5000)

