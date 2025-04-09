import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)
CORS(app)  # <-- TO DODAJ

@app.route("/")
def home():
    return "API działa! Użyj endpointu /transmissions?date=YYYY-MM-DD 🎯"
