import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import datetime
import os

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Lista słów wykluczających (studio, magazyn itp.)
EXCLUDE_KEYWORDS = ["studio", "magazyn", "analiza", "zapowiedź"]

def is_live_transmission(title):
    title_lower = title.lower()
    if any(kw in title_lower for kw in EXCLUDE_KEYWORDS):
        return False
    return "na żywo" in title_lower or "live" in title_lower

def fetch_from_naziemna(date):
    url = f"https://programtv.naziemna.info/program/sportnazywo/{date}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        transmissions = []

        for row in soup.find_all('tr', class_='program'):
            time = row.find('td', class_='time')
            event = row.find('td', class_='event')
            channel = row.find('td', class_='channel')
            if not time or not event or not channel:
                continue

            title = event.text.strip()
            if is_live_transmission(title):
                transmissions.append({
                    "time": time.text.strip(),
                    "event": title,
                    "channel": channel.text.strip()
                })
        return transmissions
    except Exception as e:
        print("Error fetching from naziemna:", e)
        return []

def fetch_from_teleman(date):
    url = f"https://www.teleman.pl/sport/{date}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        transmissions = []

        for item in soup.find_all('div', class_='transmission'):
            time = item.find('div', class_='time')
            event = item.find('div', class_='event')
            channel = item.find('div', class_='channel')
            if not time or not event or not channel:
                continue

            title = event.text.strip()
            if is_live_transmission(title):
                transmissions.append({
                    "time": time.text.strip(),
                    "event": title,
                    "channel": channel.text.strip()
                })
        return transmissions
    except Exception as e:
        print("Error fetching from teleman:", e)
        return []

@app.route("/transmissions", methods=["GET"])
def get_transmissions():
    date = request.args.get("date", datetime.datetime.today().strftime("%Y-%m-%d"))

    naziemna = fetch_from_naziemna(date)
    teleman = fetch_from_teleman(date)

    combined = naziemna[:]

    for t in teleman:
        if not any(n["event"] == t["event"] and n["time"] == t["time"] for n in combined):
            combined.append(t)

    # Łączenie kanałów regionalnych (np. TVP3 Białystok + TVP3 Opole → TVP3)
    for item in combined:
        if "tvp3" in item["channel"].lower():
            item["channel"] = "TVP3"

    # Unikalność po czasie i nazwie wydarzenia
    seen = set()
    unique = []
    for trans in combined:
        key = (trans["event"], trans["time"])
        if key not in seen:
            seen.add(key)
            unique.append(trans)

    return jsonify(unique)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
