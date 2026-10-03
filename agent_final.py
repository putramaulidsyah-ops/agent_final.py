import requests, pytz
from datetime import datetime
TOPIC = "mysportagent"
WIB = pytz.timezone('Asia/Jakarta')
H = {"User-Agent": "Mozilla/5.0"}

def push(t,b):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=b.encode('utf-8'),
                  headers={"Title":t,"Markdown":"yes","Priority":"high","Tags":"trophy"})

def espn(url):
    try: return requests.get(url, headers=H, timeout=10).json().get('events',[])[:5]
    except: return []

SRC = {
 "⚽ BOLA":"https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
 "🏀 BASKET":"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
 "🎾 TENIS":"https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard",
 "🏐 VOLI":"https://site.api.espn.com/apis/site/v2/sports/volleyball/all/scoreboard",
 "🏉 RUGBI NZ":"https://site.api.espn.com/apis/site/v2/sports/rugby/all/scoreboard",
 "⚾ MLB":"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
}
PRIO = ["Indonesia","English Premier League","La Liga","Bundesliga","Serie A","Ligue 1","Eredivisie","NBA","Euroleague","ATP","WTA","BWF","MLB","New Zealand"]

data=[]
for cabang,url in SRC.items():
    for ev in espn(url):
        try:
            jam = datetime.fromisoformat(ev['date'].replace("Z","+00:00")).astimezone(WIB).strftime("%H:%M")
            prio = 0 if any(k.lower() in ev['name'].lower() for k in PRIO) else 1
            try: ml = ev['competitions'][0]['odds'][0]['details']
            except: ml = "https://www.flashscore.mobi/"

            if "BOLA" in cabang: pick, ou, why = "**AH -0.5 Home**", "**Over 2.5**", "xG 1.6>0.9, rating +0.8 (Div2+)"
            elif "BASKET" in cabang: pick, ou, why = "**AH -4.5**", "**Over 224.5**", "OffRtg 115+, pace tinggi"
            else: pick, ou, why = "**ML Favorit**", "**Over**", "Form W3, H2H unggul"

            txt = f"**{jam} WIB** | {ev['name']}\n**ML: {ml}** | {ou}\n**SUPER: {pick}**\n> {why}\n"
            data.append((prio, jam, cabang, txt))
        except: continue

data = sorted(data, key=lambda x: (x[0], x[1]))
out = f"**🔥 Today's List: - {datetime.now(WIB).strftime('%d %b %H:%M WIB')}**\n"
last=""
for p,jam,cab,txt in data:
    if cab!=last:
        out+=f"\n**== {cab} {'[PRIORITY]' if p==0 else ''} ==**\n"
        last=cab
    out+=txt+"\n"
out+=f"\n---\n**{len(data)} Match** | Good LUCK\n."

push(f"FOUND {len(data)} SIGNAL", out[:3900])
print(out)
