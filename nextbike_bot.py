import os
import requests
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
import ssl

# SSL Fix für Windows / lokale Tests
ssl._create_default_https_context = ssl._create_unverified_context

# Telegram Einstellungen aus Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Bitte BOT_TOKEN und CHAT_ID als Environment Variables setzen!")

CHAT_ID = int(CHAT_ID)

bot = Bot(token=BOT_TOKEN)

# Nextbike Sursee Märtplatz
CITY_ID = 88            # Sursee Plus
STATION_NUMBER = 9005   # Märtplatz
API_URL = f"https://api.nextbike.net/maps/nextbike-live.json?city={CITY_ID}"

def check_nextbike():
    try:
        response = requests.get(API_URL)
        data = response.json()
        places = data['countries'][0]['cities'][0]['places']
        for place in places:
            if place['number'] == STATION_NUMBER:
                available = place['bikes_available_to_rent']
                if available > 0:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f"Nextbike verfügbar am Märtplatz! ({available} Bikes)")
                break
    except Exception as e:
        print("Fehler beim Abrufen:", e)

# Scheduler: nur zwischen 6-8 Uhr morgens, alle 30 Sekunden prüfen
scheduler = BlockingScheduler(timezone="Europe/Zurich")
scheduler.add_job(check_nextbike, 'cron', hour='6-7', second='*/30')

print("Bot läuft...")
scheduler.start()