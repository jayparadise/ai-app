import streamlit as st
import requests

# --- 1. CONFIGURATION ---
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"
BASE_URL = "https://api.oddsblaze.com/v1"

st.set_page_config(page_title="Knicks Parlay Pricer", layout="centered")
st.title("🏀 Knicks Parlay Pricer")

# --- 2. THE LOGIC (Exact copy of your working script) ---
def get_knicks_parlay_price():
    # A. Find the Game
    st.write("🔍 Searching for Knicks game...")
    odds_url = f"{BASE_URL}/odds"
    params = {"key": API_KEY, "league": "nba"}
    
    try:
        response = requests.get(odds_url, params=params)
        events = response.json()
    except Exception as e:
        st.error(f"Failed to fetch odds: {e}")
        return None

    event_id = None
    game_info = ""
    
    # Simple search for "Knicks"
    for event in events:
        if "Knicks" in event['home_team'] or "Knicks" in event['away_team']:
            event_id = event['id']
            game_info = f"{event['away_team']} @ {event['home_team']}"
            break
            
    if not event_id:
        st.warning("⚠️ Could not find a Knicks game in today's feed.")
        return None

    st.success(f"✅ Found Game: {game_info}")

    # B. Price the Parlay
    st.write("💲 Calculating DraftKings Price...")
    sgp_url = f"{BASE_URL}/same_game_parlay"
    
    # The exact legs you requested
    payload = {
        "key": API_KEY,
        "sportsbook": "draftkings",
        "event_id": event_id,
        "legs": [
            {"market": "h2h", "selection": "New York Knicks"},
            {"market": "totals", "selection": "over", "line": 223.5},
            {"market": "player_points", "player": "Jalen Brunson", "selection": "over", "line": 26.5}
        ]
    }

    try:
        sgp_response = requests.post(sgp_url, json=payload)
        return sgp_response.json()
    except Exception as e:
        st.error(f"Failed to price parlay: {e}")
        return None

# --- 3. THE BUTTON ---
if st.button("Get Price"):
    result = get_knicks_parlay_price()
    
    if result:
        # Check if we got a valid price back
        if 'odds_american' in result:
            st.metric("DraftKings SGP Odds", result['odds_american'])
            st.write(f"Implied Probability: **{result.get('implied_probability', 'N/A')}%**")
        else:
            st.error("Error from API:")
            st.json(result)
