from flask import Flask
import threading
import time
import requests
import os
from datetime import datetime
from telegram import Bot

app = Flask(__name__)

# Telegram Setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

# Nextbike-Setup
CITY_ID = os.getenv("CITY_ID")  # z.B. 88
PLACE_NUMBER = os.getenv("PLACE_NUMBER")  # z.B. 9005

def check_nextbike():
    while True:
        now = datetime.now()
        # Prüfen, ob Uhrzeit zwischen 6:30 und 7:50
        if now.hour == 6 and now.minute >= 30 or now.hour == 7 and now.minute <= 50:
            try:
                url = f"https://api.nextbike.ch/v2/nextbike-api-endpoint?city={CITY_ID}"
                response = requests.get(url)
                data = response.json()
                available_bikes = 0
                for place in data['cities'][0]['places']:
                    if place['number'] == int(PLACE_NUMBER):
                        available_bikes = place['bikes_available_to_rent']
                if available_bikes > 0:
                    bot.send_message(chat_id=CHAT_ID, text=f"{available_bikes} Bikes verfügbar!")
            except Exception as e:
                print("Fehler beim Check:", e)
        else:
            print("Außerhalb der Prüfzeiten, nächster Check in 30 Sekunden")
        time.sleep(30)  # alle 30 Sekunden prüfen

# Thread starten, damit Flask nicht blockiert wird
threading.Thread(target=check_nextbike, daemon=True).start()

# Webserver für Render
@app.route("/")
def index():
    return "Nextbike-Bot läuft!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
