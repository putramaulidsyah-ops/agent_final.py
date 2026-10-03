import requests, pytz
from datetime import datetime

TOPIC = "betterr-choco899-9categoryy"
WIB = pytz.timezone('Asia/Jakarta')
HEADERS = {"User-Agent": "Mozilla/5.0"}

def push(t,b):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=b.encode('utf-8'),
        headers={"Title": t, "Tags": "trophy", "Priority":"high"})

def get_sofa(sport, date_str):
    # sport: football, basketball, tennis, volleyball, etc
    url = f"https://api.sofascore.com/api/v1/sport/{sport}/scheduled-events/{date_str}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15).json()
        return r.get('events', [])[:2] # 2 match per cabang
    except:
        return []

SPORTS_SOFASCORE = {
    "⚽ BOLA": "football",
    "🏀 BASKET": "basketball",
    "🎾 TENIS": "tennis",
    "🏐 VOLI": "volleyball",
    "🏸 BADMINTON": "badminton",
    "⚾ BISBOL": "baseball",
}

today = datetime.now(WIB).strftime("%Y-%m-%d")
report = f"Today's List: - {datetime.now(WIB).strftime('%d %b %H:%M WIB')}\n | GOOD LUCK | \n\n"
total=0

for nama, slug in SPORTS_SOFASCORE.items():
    events = get_sofa(slug, today)
    if not events:
        report += f"== {nama} ==\nGak ada jadwal\n\n"
        continue
    for ev in events:
        total+=1
        try:
            home = ev['homeTeam']['name']
            away = ev['awayTeam']['name']
            ts = ev['startTimestamp']
            jam = datetime.fromtimestamp(ts, tz=pytz.utc).astimezone(WIB).strftime("%H:%M WIB")
            
            # Rating SofaScore (kunci fair value)
            try: rating_h = ev['homeTeam']['rating']
            except: rating_h = "-"
            try: rating_a = ev['awayTeam']['rating']
            except: rating_a = "-"

            # Analisa Fair
            if nama=="⚽ BOLA": fair = f"Fair AH: -0.5 jika rating gap >0.8 ({rating_h} vs {rating_a}) | Exp O/U 2.75"
            elif nama=="🏀 BASKET": fair = f"Fair Total: 225 | Pace check"
            else: fair = f"Rating {rating_h} vs {rating_a} -> Cek ML value"

            report += f"== {nama} ==\n⏰ {jam} | {home} vs {away}\nRating: {rating_h} vs {rating_a}\n>> {fair}\n>> Odds AH/O-U: Cek di SofaScore.com/event/{ev['id']}\n\n"
        except: continue

# Tambah 3 cabang yang gak ada di SofaScore, ambil dari AiScore
report += f"== 🎱 SNOOKER / 🏉 RUGBI / 🏓 TENIS MEJA ==\nCek di AiScore.com - jadwal ada, SofaScore terbatas.\n>> Fair: Form 5 match terakhir >60% = value ML\n\n"

report += f"Total {total} match.\nNext auto jam 7 pagi."

print(report)
push(f"SOFASCORE {total} MATCH - FAIR VALUE", report[:3800])
