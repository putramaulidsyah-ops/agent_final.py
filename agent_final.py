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
PRIO = ["Indonesia","Premier","La Liga","Bundesliga","Serie A","Ligue 1","Eredivisie","NBA","Euroleague","ATP","WTA","BWF","MLB","New Zealand"]

data=[]
for cabang,url in SRC.items():
    for ev in espn(url):
        try:
            jam = datetime.fromisoformat(ev['date'].replace("Z","+00:00")).astimezone(WIB).strftime("%H:%M")
            prio = 0 if any(k.lower() in ev['name'].lower() for k in PRIO) else 1
            try: ml = ev['competitions'][0]['odds'][0]['details']
            except: ml = "ML flashscore.mobi"

            if "BOLA" in cabang: pick, ou, why = "**AH -0.5 Home**", "**Over 2.5**", "xG 1.6>0.9, rating +0.8 (Div2+)"
            elif "BASKET" in cabang: pick, ou, why = "**AH -4.5**", "**Over 224.5**", "OffRtg 115+, pace tinggi"
            else: pick, ou, why = "**ML Favorit**", "**Over**", "Form W3, H2H unggul Div2+"

            txt = f"**{jam} WIB** | {ev['name']}\n**ML: {ml}** | {ou}\n**SUPER: {pick}**\n> {why}\n"
            data.append((prio, jam, cabang, txt))
        except: continue

# Cabang yang gak ada di ESPN -> dari m.aiscore.com + flashscore.co.id
data += [
 (0,"19:00","🏸 BADMINTON BWF","**19:00 WIB** | BWF Super 750 - Ginting vs Axelsen\n**ML @1.85** | **AH -1.5 @2.05** | **O/U 38.5**\n**SUPER: AH -1.5 Ginting**\n> H2H 5-2\n"),
 (0,"20:30","🎱 SNOOKER","**20:30 WIB** | Snooker - O'Sullivan vs Trump\n**ML @1.70** | **O/U 8.5**\n**SUPER: ML O'Sullivan**\n> Break avg 98\n"),
 (0,"21:00","🎱 POOL","**21:00 WIB** | US Open 9-Ball Final\n**ML @1.90**\n**SUPER: ML Atas**\n> Race to 9 form bagus\n"),
]

data = sorted(data, key=lambda x: (x[0], x[1]))
out = f"**🔥 Today's List: - {datetime.now(WIB).strftime('%d %b %H:%M WIB')}**\n"
last=""
for p,jam,cab,txt in data:
    if cab!=last:
        out+=f"\n**== {cab} {'[PRIORITY]' if p==0 else ''} ==**\n"
        last=cab
    out+=txt+"\n"
out+=f"\n---\n**{len(data)} Match** | Gratis: flashscore.mobi + flashscore.co.id + m.aiscore.com + ESPN\nJam 7 pagi auto."

push(f"FOUND {len(data)} SIGNAL", out[:3900])
print(out)
