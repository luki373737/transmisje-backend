import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)  # <-- To umożliwia dostęp z frontendu (np. z gabinet.5v.pl)

# Nagłówki do symulowania przeglądarki
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Funkcja do pobierania transmisji z ProgramTV (naziemna)
def fetch_from_naziemna(date):
    url = f"https://programtv.naziemna.info/program/sportnazywo/{date}"
    response = requests.get(url, headers=headers)  # Dodajemy nagłówki
    soup = BeautifulSoup(response.text, 'html.parser')
    
    transmissions = []
    for item in soup.find_all('tr', class_='program'):
        time = item.find('td', class_='time').text.strip()
        event = item.find('td', class_='event').text.strip()
        channel = item.find('td', class_='channel').text.strip()

        if 'na żywo' in event.lower() or "live" in event.lower():
            transmissions.append({"time": time, "event": event, "channel": channel})
    
    return transmissions

# Funkcja do pobierania transmisji z Teleman
def fetch_from_teleman(date):
    url = f"https://www.teleman.pl/sport/{date}"
    response = requests.get(url, headers=headers)  # Dodajemy nagłówki
    soup = BeautifulSoup(response.text, 'html.parser')
    
    transmissions = []
    for item in soup.find_all('div', class_='transmission'):
        time = item.find('div', class_='time').text.strip()
        event = item.find('div', class_='event').text.strip()
        channel = item.find('div', class_='channel').text.strip()
        
        if 'na żywo' in event.lower() or "live" in event.lower():
            transmissions.append({"time": time, "event": event, "channel": channel})
    
    return transmissions

# Endpoint do pobierania transmisji
@app.route('/transmissions', methods=['GET'])
def get_transmissions():
    date = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
    
    transmissions = fetch_from_naziemna(date)
    
    teleman_transmissions = fetch_from_teleman(date)
    for teleman_trans in teleman_transmissions:
        if teleman_trans not in transmissions:
            transmissions.append(teleman_trans)

    # Łączenie duplikatów na podstawie czasu i wydarzenia
    unique_transmissions = []
    seen = set()
    for trans in transmissions:
        identifier = (trans['event'], trans['time'])
        if identifier not in seen:
            seen.add(identifier)
            unique_transmissions.append(trans)
    
    return jsonify(unique_transmissions)

# Uruchamianie aplikacji
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
