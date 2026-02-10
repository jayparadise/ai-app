import streamlit as st
import requests

# Use the key you provided
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"

# We will test these two base URLs
URL_OPTIONS = [
    "https://api.oddsblaze.com/v1",
    "https://odds.oddsblaze.com/v1"
]

def get_working_url():
    """Finds which subdomain OddsBlaze is using."""
    for base in URL_OPTIONS:
        try:
            # Test with the 'leagues' endpoint which is standard
            test_url = f"{base}/leagues"
            res = requests.get(test_url, params={"key": API_KEY}, timeout=5)
            if res.status_code == 200:
                return base
        except:
            continue
    return None

st.set_page_config(page_title="OddsBlaze AI", layout="wide")
st.title("🏀 ParlayBlaze AI")

# --- AUTO-CONFIG ---
WORKING_BASE = get_working_url()

if not WORKING_BASE:
    st.error("🚨 API CONNECTION FAILED: Both subdomains returned errors. Check if your API key is active or if the service is down.")
    st.stop()

st.success(f"Connected to OddsBlaze at: `{WORKING_BASE}`")

# --- APP LOGIC ---
prompt = st.text_input("Describe your parlay:", "Knicks win, Jalen Brunson points, over total")

if st.button("Generate Parlays"):
    with st.spinner("Fetching live markets..."):
        # 1. Pull NBA games
        res = requests.get(f"{WORKING_BASE}/odds", params={"key": API_KEY, "league": "nba"})
        
        if res.status_code == 200:
            games = res.json()
            # Logic to match 'Knicks' from prompt to game data
            match = next((g for g in games if "knicks" in g['home_team'].lower() or "knicks" in g['away_team'].lower()), None)
            
            if match:
                st.subheader(f"Game Found: {match['away_team']} @ {match['home_team']}")
                # Proceed to price variations...
                st.info("Pricing variations for DraftKings...")
            else:
                st.warning("No live Knicks games found. Try a team playing today.")
        else:
            st.error(f"Error {res.status_code}: {res.text}")
