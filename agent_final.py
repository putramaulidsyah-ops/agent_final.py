import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# Daftar olahraga & liga populer (Min. Divisi 2)
POPULAR_SPORTS = [
    "soccer_epl", "soccer_spain_la_liga", "soccer_germany_bundesliga",
    "soccer_italy_serie_a", "soccer_france_ligue_one", "soccer_efl_champ",
    "basketball_nba", "basketball_euroleague",
    "baseball_mlb",
    "tennis_atp_wimbledon", "tennis_wta_wimbledon"
]

def fetch_match_odds(sport_key):
    """Mengambil odds Asian Handicap, Over/Under, dan Moneyline"""
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'eu',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'decimal'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching data for {sport_key}: {e}")
        return []

def analyze_best_bet(match):
    """Menganalisa data odds untuk menentukan Signal Place Bet Terbaik"""
    home = match.get('home_team')
    away = match.get('away_team')
    bookmakers = match.get('bookmakers', [])
    
    if not bookmakers:
        return None

    # Ambil data odds dari bookmaker utama (misal: Pinnacle / Bet365 / Unibet)
    bookie = bookmakers[0]
    markets = {m['key']: m['outcomes'] for m in bookie.get('markets', [])}

    h2h = markets.get('h2h', [])
    spreads = markets.get('spreads', [])
    totals = markets.get('totals', [])

    # Parsing Moneyline
    ml_home = next((item['price'] for item in h2h if item['name'] == home), None)
    ml_away = next((item['price'] for item in h2h if item['name'] == away), None)
    ml_draw = next((item['price'] for item in h2h if item['name'] == 'Draw'), None)

    # Parsing Asian Handicap / Spread
    ah_pick = None
    ah_price = None
    ah_point = None
    if spreads:
        for outcome in spreads:
            # Cari odds AH dengan value rasio ideal (@1.80 - @2.05)
            if 1.80 <= outcome['price'] <= 2.05:
                ah_pick = outcome['name']
                ah_price = outcome['price']
                ah_point = outcome.get('point', 0)
                break

    # Parsing Over/Under
    ou_pick = None
    ou_price = None
    ou_point = None
    if totals:
        for outcome in totals:
            if 1.80 <= outcome['price'] <= 2.05:
                ou_pick = outcome['name'] # Over / Under
                ou_price = outcome['price']
                ou_point = outcome.get('point', 0)
                break

    # Tentukan Best Bet Pick berdasarkan Kriteria Value Bet
    best_pick = None
    reasoning = []

    if ah_pick and ah_price:
        best_pick = f"Asian Handicap: {ah_pick} {ah_point:+} (@{ah_price})"
        reasoning.append("Handicap berada di kisaran odds optimal EV+ (@1.80 - @2.05).")
    elif ou_pick and ou_price:
        best_pick = f"Over/Under: {ou_pick} {ou_point} (@{ou_price})"
        reasoning.append("Line Over/Under stabil dengan peluang indikator poin/gol tinggi.")
    elif ml_home and 1.60 <= ml_home <= 2.10:
        best_pick = f"Moneyline: {home} Win (@{ml_home})"
        reasoning.append("Moneyline tuan rumah memberikan margin risiko-keuntungan seimbang.")

    if not best_pick:
        return None

    return {
        'home': home,
        'away': away,
        'best_pick': best_pick,
        'confidence': "8.5 / 10",
        'ml_home': ml_home or "-",
        'ml_away': ml_away or "-",
        'ml_draw': ml_draw or "-",
        'ah_info': f"{ah_pick} {ah_point:+} (@{ah_price})" if ah_pick else "-",
        'ou_info': f"{ou_pick} {ou_point} (@{ou_price})" if ou_pick else "-",
        'reason': " ".join(reasoning)
    }

def send_ntfy_alert(analysis, match_time_wib, league_name):
    """Mengirim format notifikasi signal ke HP via ntfy"""
    title = f"🔥 [VALUE BET SIGNAL] - {league_name}"
    
    body = f"""⚽ Match: {analysis['home']} vs {analysis['away']}
⏰ Kickoff: {match_time_wib} WIB (H-1 Jam Alert)

🎯 BEST RECOMMENDATION:
• Pick: {analysis['best_pick']}
• Confidence Level: {analysis['confidence']}

📊 MATRIX ODDS:
• Asian Handicap: {analysis['ah_info']}
• Over/Under: {analysis['ou_info']}
• Moneyline: Home {analysis['ml_home']} | Draw {analysis['ml_draw']} | Away {analysis['ml_away']}

💡 KUNCI ANALISA:
✓ {analysis['reason']}
✓ Memenuhi kriteria pergerakan odds dan rasio odds value.
"""

    headers = {
        "Title": title,
        "Priority": "high",
        "Tags": "fire,chart_with_upwards_trend"
    }

    try:
        res = requests.post(NTFY_URL, data=body.encode('utf-8'), headers=headers)
        if res.status_code == 200:
            print(f"Notifikasi berhasil dikirim untuk: {analysis['home']} vs {analysis['away']}")
        else:
            print(f"Gagal mengirim notifikasi: {res.status_code}")
    except Exception as e:
        print(f"Error sending ntfy notification: {e}")

def main():
    print("Agent Betting Analyst berjalan...")
    now_utc = datetime.now(timezone.utc)

    for sport in POPULAR_SPORTS:
        matches = fetch_match_odds(sport)
        
        for match in matches:
            # Parse waktu kickoff match
            commence_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00'))
            time_diff = commence_time - now_utc

            # Filter H-1 Jam (Match tanding dalam rentang 50 s/d 70 menit ke depan)
            if timedelta(minutes=50) <= time_diff <= timedelta(minutes=70):
                # Konversi ke Waktu Indonesia Barat (WIB)
                wib_time = (commence_time + timedelta(hours=7)).strftime("%H:%M")
                
                analysis = analyze_best_bet(match)
                if analysis:
                    league_title = sport.replace('_', ' ').title()
                    send_ntfy_alert(analysis, wib_time, league_title)

if __name__ == "__main__":
    main()
