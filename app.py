import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)  # Umożliwia dostęp z zewnętrznych źródeł, np. Twojego frontendu

@app.route('/')
def index():
    return "API działa!"

# Funkcja do pobierania transmisji z ProgramTV
def fetch_from_naziemna(date):
    url = f"https://programtv.naziemna.info/program/sportnazywo/{date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    transmissions = []
    for item in soup.find_all('tr', class_='program'):
        time = item.find('td', class_='time').text.strip()
        event = item.find('td', class_='event').text.strip()
        channel = item.find('td', class_='channel').text.strip()
        if 'na żywo' in event.lower() or "live" in event.lower():
            transmissions.append({"time": time, "event": event, "channel": channel})
    
    return transmissions

# Endpoint do pobierania transmisji
@app.route('/transmissions', methods=['GET'])
def get_transmissions():
    date = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
    
    transmissions = fetch_from_naziemna(date)
    
    return jsonify(transmissions)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
