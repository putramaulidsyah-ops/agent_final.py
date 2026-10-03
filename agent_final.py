import requests
from datetime import datetime
import pytz

TOPIC = "better-kranji-9cabang" # GANTI SESUAI TOPIC LU DI ATAS

# === DATA JADWAL & ODDS (Ini nanti lu ganti manual / API) ===
# Format: [Cabang, Match, Jam UTC, Odds ML, Odds AH, Odds O/U, Analisa Fair Value]
# Jam UTC contoh: Malam ini Man City main jam 20:00 WIB = 13:00 UTC

MATCHES = [
    ["BOLA", "Man City vs Arsenal", "2026-10-03T13:00:00Z", "1.85 vs 2.10", "AH -0.25", "O/U 2.75", "Fair ML: City 55% | Exp AH: -0.4 | Exp Goals: 2.9 -> Over condong"],
    ["BASKET", "Lakers vs Warriors", "2026-10-04T02:00:00Z", "1.90 vs 1.90", "AH -1.5", "O/U 225.5", "Fair ML: 50/50 | Pace 101 | Exp Total 228 -> Over tipis"],
    ["TENIS", "Vekic vs Zhu Lin", "2026-10-03T06:00:00Z", "1.55 vs 2.45", "AH -3.5", "O/U 20.5", "H2H 3-0 Vekic | Fair ML Vekic 68% | Exp Diff +4.2 -> Vekic -3.5 COVER | Exp Total 21.1 Over"],
    ["BADMINTON", "Axelsen vs Ginting", "2026-10-03T08:00:00Z", "1.65 vs 2.20", "AH -3.5 poin", "O/U -", "Form Axelsen on-fire | Fair -4.1 -> COVER"],
    ["SNOOKER", "O'Sullivan vs Trump", "2026-10-03T12:00:00Z", "1.80 vs 2.00", "AH -1.5 frame", "O/U 9.5", "Best of 11 | Exp Frame Diff +1.8 -> Ronnie COVER"],
    ["POOL", "Biado vs Filler", "2026-10-03T13:00:00Z", "2.10 vs 1.75", "AH -1.5", "O/U -", "Race to 9 | Break & Run 35% vs 38% -> Filler tipis"],
    ["VOLI", "Japan vs Brazil", "2026-10-03T09:00:00Z", "2.20 vs 1.65", "AH +7.5", "O/U 178.5", "Total Points Exp 181 -> Over"],
    ["RUGBI", "All Blacks vs Wallabies", "2026-10-03T07:00:00Z", "1.45 vs 2.75", "AH -7.5", "O/U 52.5", "Exp Diff -9.2 -> All Blacks COVER | Over"],
    ["BISBOL", "Yankees vs Dodgers", "2026-10-04T00:00:00Z", "1.95 vs 1.85", "Run Line -1.5", "O/U 8.5", "Pitcher ERA 3.2 vs 3.8 -> Exp Runs 9.1 Over"],
]

def to_wib(utc_str):
    dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    dt_wib = dt_utc.astimezone(pytz.timezone('Asia/Jakarta'))
    return dt_wib.strftime("%H:%M WIB, %d %b")

def push(title, body, tag="trophy"):
    requests.post(f"https://ntfy.sh/{TOPIC}",
        data=body.encode('utf-8'),
        headers={"Title": title, "Tags": tag, "Priority": "high"})

# Kirim 1 notif rangkuman jam 7 pagi
full_report = f"JADWAL HARI INI - {datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%d %b')}\n\n"
for cabang, match, jam_utc, ml, ah, ou, analisa in MATCHES:
    jam_wib = to_wib(jam_utc)
    full_report += f"== {cabang} ==\n⏰ {jam_wib}\n{match}\n{ml} | {ah} | {ou}\n>> {analisa}\n\n"

# 1. Push rangkuman utama (yang muncul di notif bar)
push(f"AGENT 9 CABANG - {len(MATCHES)} MATCH", full_report, "alarm_clock")

# 2. Push per cabang (opsional, kalau lu mau notif misah)
# for m in MATCHES:
# push(f"{m[0]}: {m[1]}", f"⏰ {to_wib(m[2])}\n{m[6]}", m[0].lower())

print(full_report)
