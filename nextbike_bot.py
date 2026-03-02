from flask import Flask
import threading
import time
import requests
import os
from telegram import Bot

app = Flask(__name__)

# Telegram Setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

# Nextbike-Check-Funktion
CITY_ID = os.getenv("CITY_ID")  # z.B. 88 für Sursee Plus
PLACE_NUMBER = os.getenv("PLACE_NUMBER")  # z.B. 9005 für Märtplatz

def check_nextbike():
    while True:
        try:
            url = f"https://api.nextbike.ch/v2/nextbike-api-endpoint?city={CITY_ID}"
            response = requests.get(url)
            data = response.json()
            # Bikes für den ausgewählten Platz
            available_bikes = 0
            for place in data['cities'][0]['places']:
                if place['number'] == int(PLACE_NUMBER):
                    available_bikes = place['bikes_available_to_rent']
            if available_bikes > 0:
                bot.send_message(chat_id=CHAT_ID, text=f"{available_bikes} Bikes verfügbar!")
        except Exception as e:
            print("Fehler beim Check:", e)
        time.sleep(30)  # alle 30 Sekunden prüfen

# Thread starten, damit Flask nicht blockiert wird
threading.Thread(target=check_nextbike, daemon=True).start()

# einfacher Webserver für Render
@app.route("/")
def index():
    return "Nextbike-Bot läuft!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render setzt PORT automatisch
    app.run(host="0.0.0.0", port=port)
