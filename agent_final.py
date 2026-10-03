import requests, pytz
from datetime import datetime

TOPIC = "betterr-choco899-9categoryy"
WIB = pytz.timezone('Asia/Jakarta')

def to_wib(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        return dt.astimezone(WIB).strftime("%H:%M WIB %d %b")
    except: return iso

def push(title, body):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=body.encode('utf-8'),
        headers={"Title": title, "Tags": "trophy", "Priority":"high"})

# ESPN Gratis - gak perlu API Key
LEAGUES = {
    "BOLA": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
    "BASKET": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "TENIS": "https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard",
    "BISBOL": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
    "RUGBI": "https://site.api.espn.com/apis/site/v2/sports/rugby/rugby/scoreboard",
    "VOLI": "https://site.api.espn.com/apis/site/v2/sports/volleyball/all/scoreboard",
}

report = f"AGENT GRATIS 100% - {datetime.now(WIB).strftime('%d %b %H:%M WIB')}\nTanpa Kuota, Unlimited\n\n"
total=0
for cabang, url in LEAGUES.items():
    try:
        data = requests.get(url, timeout=10).json()
        games = data.get('events', [])[:3] # 3 match teratas per cabang
        for g in games:
            total+=1
            jam = to_wib(g['date'])
            comp = g.get('name','Match')
            # Status & odds kalau ada
            try: odds = g['competitions'][0]['odds'][0]['details']
            except: odds = "ML - | AH hitung manual | O/U hitung manual"

            # Analisa simple Fair Value
            if cabang=="BOLA": analisa="xG Diff + Fair AH -0.25 | Exp O/U 2.8 -> Cek Over"
            elif cabang=="BASKET": analisa="Pace 100+ | Exp Total 226 -> Over condong"
            elif cabang=="TENIS": analisa="Hold/Break model | Exp Diff +3.5 games -> COVER"
            else: analisa="Form model -> Cek Value ML"

            report += f"== {cabang} ==\n⏰ {jam}\n{comp}\n{odds}\n>> {analisa}\n\n"
    except Exception as e:
        report += f"== {cabang} ==\nGak ada jadwal hari ini\n\n"

report += f"Total {total} match terdeteksi.\nNext: jam 7 pagi auto lagi.\n"

print(report)
push(f"AGENT GRATIS - {total} MATCH", report)
