import requests
from bs4 import BeautifulSoup  # Dodajemy poprawny import BeautifulSoup
from flask import Flask, jsonify, request
import datetime
import logging
from flask_cors import CORS

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)  # Zezwolenie na CORS

# Funkcja do pobierania transmisji z ProgramTV (naziemna)
def fetch_from_naziemna(date):
    try:
        url = f"https://programtv.naziemna.info/program/sportnazywo/{date}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        transmissions = []
        # Parsowanie transmisji
        for item in soup.find_all('tr', class_='program'):
            time = item.find('td', class_='time').text.strip()
            event = item.find('td', class_='event').text.strip()
            channel = item.find('td', class_='channel').text.strip()
            
            # Filtrujemy transmisje na żywo
            if 'na żywo' in event.lower() or "live" in event.lower():
                transmissions.append({"time": time, "event": event, "channel": channel})
        
        return transmissions
    except Exception as e:
        logging.error(f"Error fetching data from ProgramTV (naziemna): {e}")
        return []

# Funkcja do pobierania transmisji z Teleman
def fetch_from_teleman(date):
    try:
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
    except Exception as e:
        logging.error(f"Error fetching data from Teleman: {e}")
        return []

# Endpoint do pobierania transmisji
@app.route('/transmissions', methods=['GET'])
def get_transmissions():
    try:
        # Pobieranie daty z parametrów żądania
        date = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
        
        # Pobieranie transmisji z ProgramTV i Teleman
        transmissions = fetch_from_naziemna(date)
        teleman_transmissions = fetch_from_teleman(date)
        
        # Łączenie transmisji z obu źródeł
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

    except Exception as e:
        logging.error(f"Error processing the transmission request: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=10000)
