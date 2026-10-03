import requests, pytz
from datetime import datetime
import os

TOPIC = "betterr-choco899-9categoryy"
WIB = pytz.timezone('Asia/Jakarta')
HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"}

def push(title, body):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=body.encode('utf-8'),
        headers={"Title": title, "Tags": "trophy", "Priority":"high"})

def to_wib(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=pytz.utc).astimezone(WIB).strftime("%H:%M WIB")
    except:
        return datetime.now(WIB).strftime("%H:%M WIB")

def get_sport(sport_path):
    today = datetime.now(WIB).strftime("%Y%m%d")
    url = f"https://www.aiscore.com/api/{sport_path}/match/list?date={today}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15).json()
        data = r.get('data', [])
        if isinstance(data, dict): # kadang bentuknya dict
            data = data.get('matches', []) or list(data.values())[0] if data else []
        return data[:3] # ambil 3 match per cabang biar gak kepanjangan
    except Exception as e:
        print(f"Gagal {sport_path}: {e}")
        return []

# 9 CABANG -> PATH AISCORE
SPORTS = {
    "⚽ BOLA": "football",
    "🏀 BASKET": "basketball",
    "🎾 TENIS": "tennis",
    "🏸 BADMINTON": "badminton",
    "🎱 SNOOKER": "snooker",
    "🏐 VOLI": "volleyball",
    "🏉 RUGBI": "rugby",
    "⚾ BISBOL": "baseball",
    "🏓 TENIS MEJA": "tabletennis",
}

report = f"🔥
