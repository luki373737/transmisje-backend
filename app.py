import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__)

# Funkcja do pobierania transmisji
def fetch_from_naziemna(date):
    url = f'https://programtv.naziemna.info/program/sportnazywo/{date}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Przykład: wyciąganie informacji o transmisjach
    transmissions = []
    for item in soup.find_all('div', class_='program-item'):
        title = item.find('span', class_='title').text.strip()
        channel = item.find('span', class_='channel').text.strip()
        time = item.find('span', class_='time').text.strip()
        transmissions.append({
            'title': title,
            'channel': channel,
            'time': time
        })
    return transmissions

@app.route('/transmissions', methods=['GET'])
def get_transmissions():
    date = request.args.get('date', default='2025-04-09')  # domyślnie 9 kwietnia 2025
    try:
        transmissions = fetch_from_naziemna(date)
        return jsonify(transmissions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
