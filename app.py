import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# Funkcja do pobierania transmisji z ProgramTV (naziemna)
def fetch_from_naziemna(date):
    url = f"https://programtv.naziemna.info/program/sportnazywo/{date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    transmissions = []
    # Parsowanie transmisji (przykładowo, musisz dostosować do struktury HTML)
    for item in soup.find_all('tr', class_='program'):
        time = item.find('td', class_='time').text.strip()
        event = item.find('td', class_='event').text.strip()
        channel = item.find('td', class_='channel').text.strip()
        
        # Filtrujemy transmisje na żywo (np. poprzez sprawdzenie słowa "na żywo" w opisie lub godzinie)
        if 'na żywo' in event.lower() or "live" in event.lower():
            transmissions.append({"time": time, "event": event, "channel": channel})
    
    return transmissions

# Funkcja do pobierania transmisji z Teleman
def fetch_from_teleman(date):
    url = f"https://www.teleman.pl/sport/{date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    transmissions = []
    # Parsowanie transmisji
    for item in soup.find_all('div', class_='transmission'):
        time = item.find('div', class_='time').text.strip()
        event = item.find('div', class_='event').text.strip()
        channel = item.find('div', class_='channel').text.strip()
        
        # Filtrujemy transmisje na żywo
        if 'na żywo' in event.lower() or "live" in event.lower():
            transmissions.append({"time": time, "event": event, "channel": channel})
    
    return transmissions

# Endpoint do pobierania transmisji
@app.route('/transmissions', methods=['GET'])
def get_transmissions():
    date = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
    
    transmissions = fetch_from_naziemna(date)
    
    # Dodaj transmisje z Teleman, jeśli ich brakuje
    teleman_transmissions = fetch_from_teleman(date)
    for teleman_trans in teleman_transmissions:
        if teleman_trans not in transmissions:
            transmissions.append(teleman_trans)

    # Filtracja i łączenie duplikatów (np. regionalne wersje)
    unique_transmissions = []
    seen = set()
    for trans in transmissions:
        identifier = (trans['event'], trans['time'])
        if identifier not in seen:
            seen.add(identifier)
            unique_transmissions.append(trans)
    
    return jsonify(unique_transmissions)

if __name__ == "__main__":
    app.run(debug=True)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
