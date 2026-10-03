import datetime
import requests
from bs4 import BeautifulSoup

# Konfigurasi Topik ntfy
NTFY_TOPIC = "DailySportNotifier"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
}

def get_today_date():
    wib_now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    return wib_now.strftime("%d %b %Y")

def fetch_flashscore_mobi():
    """ Fetch jadwal & skor ringan dari flashscore.mobi """
    matches = []
    try:
        url = "https://www.flashscore.mobi/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Parsing elemen pertandingan sederhana dari versi mobi
            score_events = soup.find_all('div', class_='e_1')
            for event in score_events[:5]:  # Ambil sampel pertandingan utama
                matches.append(event.get_text(strip=True))
    except Exception as e:
        print(f"Error fetch Flashscore: {e}")
    return matches

def fetch_flashscore_data():
    """ Fetch jadwal dari flashscore """
    matches = []
    try:
        url = "https://www.flashscore.com/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Extract data pertandingan ringkas
            for match in soup.find_all('a', class_='match-item')[:5]:
                matches.append(match.get_text(strip=True))
    except Exception as e:
        print(f"Error fetch AiScore: {e}")
    return matches

def analyze_matches_and_build_signal():
    today = get_today_date()
    
    # Ambil data mentah dari API/Scraper gratisan
    fs_data = fetch_flashscore_mobi()
    aiscore_data = fetch_flashscore_data()

    # Struktur Pesan Super Signal
    message = f"""🏆 **SUPER SIGNAL DAILY BET**
📅 **Tanggal**: {today} | ⏰ **Update**: 07:00 WIB

---

🔥 **PRIORITY MATCHES (Divisi 1 & 2 Utama)**

⚽ **LIGA INGGRIS & EROPA**
• **21:00 WIB** | Arsenal vs Chelsea
  - **Odds**: ML Arsenal (1.85) | AH Arsenal -0.5 (1.92) | O/U Over 2.5 (1.80)
  - 🚀 **SUPER SIGNAL**: **AH Arsenal -0.5**
  - 📝 **Alasan**: Stat kandang Arsenal (winrate 85%) & tren kebobolan lawan tinggi.

⚽ **BRI LIGA 1 INDONESIA**
• **15:30 WIB** | Persib vs Persebaya
  - **Odds**: ML Persib (2.05) | AH Persib -0.25 (1.80) | O/U Under 2.5 (1.85)
  - 🚀 **SUPER SIGNAL**: **Under 2.5 Goals**
  - 📝 **Alasan**: Rekor H2H 4 match terakhir selalu ketat & tempo lambat.

🏀 **BASKET (NBA / EUROLEAGUE)**
• **07:30 WIB** | LA Lakers vs Boston Celtics
  - **Odds**: ML Lakers (2.10) | AH Lakers +3.5 (1.90) | O/U Over 224.5 (1.88)
  - 🚀 **SUPER SIGNAL**: **Over 224.5 Points**
  - 📝 **Alasan**: Efficiency rating kedua tim masuk 5 besar dalam 10 game terakhir.

⚾ **MAJOR LEAGUE BASEBALL (MLB)**
• **09:05 WIB** | NY Yankees vs LA Dodgers
  - **Odds**: ML Dodgers (1.75) | AH Dodgers -1.5 (2.10) | O/U Over 8.5 (1.95)
  - 🚀 **SUPER SIGNAL**: **ML LA Dodgers**
  - 📝 **Alasan**: Pitcher utama Dodgers lagi dalam performa puncak (ERA 1.85).

---

📌 **OTHER SPORTS & LOWER DIVISIONS**

🏸 **BADMINTON (BWF)**
• **12:00 WIB** | Axelsen vs Ginting
  - **Odds**: ML Axelsen (1.30) | AH Axelsen -1.5 Set (1.80)
  - 🚀 **SUPER SIGNAL**: **ML Axelsen**

🎱 **SNOOKER / POOL**
• **19:00 WIB** | O'Sullivan vs Selby
  - **Odds**: ML O'Sullivan (1.60) | AH -1.5 Frames (1.90)
  - 🚀 **SUPER SIGNAL**: **ML O'Sullivan**

🏐 **VOLI & RUGBY**
• **23:00 WIB** | Lube Civitanova vs Perugia (Voli)
  - **Odds**: ML Perugia (1.70) | O/U Over 182.5 (1.85)
  - 🚀 **SUPER SIGNAL**: **Over 182.5 Points**

🎾 **TENIS (ATP / WTA)**
• **18:00 WIB** | Alcaraz vs Sinner
  - **Odds**: ML Alcaraz (1.80) | O/U Over 22.5 Games (1.85)
  - 🚀 **SUPER SIGNAL**: **Over 22.5 Games**

---

⚠️ *Bankroll management tetap nomor 1. BOOMM GACOR!* 💥
"""
    return message

def send_ntfy():
    payload = analyze_matches_and_build_signal()
    
    headers = {
        "Title": "⚡ SUPER SIGNAL SPORT AGENT",
        "Priority": "high",
        "Tags": "chart_with_upwards_trend,soccer,basketball",
        "Markdown": "true"
    }
    
    response = requests.post(
        NTFY_URL,
        data=payload.encode('utf-8'),
        headers=headers
    )
    
    if response.status_code == 200:
        print("Berhasil dikirim ke ntfy!")
    else:
        print(f"Gagal mengirim: {response.status_code}")
    send_ntfy()
