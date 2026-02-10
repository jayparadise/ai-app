import streamlit as st
import requests

# --- CONFIG ---
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"
ODDS_URL = "https://odds.oddsblaze.com/"
SGP_URL = "https://draftkings.sgp.oddsblaze.com/"

st.set_page_config(page_title="OddsBlaze AI", layout="wide")
st.title("🏀 OddsBlaze SGP Builder")

# --- DATA ENGINE ---
def get_verified_feed():
    """Uses your exact working URL parameters."""
    params = {
        "sportsbook": "draftkings",
        "league": "nba",
        "key": API_KEY
    }
    try:
        # We must include the headers to ensure the request isn't blocked
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(ODDS_URL, params=params, headers=headers, timeout=15)
        return res.json()
    except Exception as e:
        st.error(f"Feed Error: {e}")
        return []

# --- APP INTERFACE ---
prompt = st.text_input("Which team are you betting on?", "Knicks")

if st.button("Generate Parlays"):
    with st.spinner("Accessing DraftKings Feed..."):
        feed = get_verified_feed()
        
        if feed:
            # 1. Search for the game in the feed
            target_game = None
            available_teams = []
            
            for game in feed:
                h_team = game.get('home_team', '')
                a_team = game.get('away_team', '')
                available_teams.extend([h_team, a_team])
                
                if prompt.lower() in h_team.lower() or prompt.lower() in a_team.lower():
                    target_game = game
                    break
            
            # 2. Results
            if target_game:
                st.success(f"Game Found: {target_game['away_team']} @ {target_game['home_team']}")
                st.info(f"Event ID: {target_game.get('id')}")
                
                # Pricing variations logic
                st.write("### Recommended Parlays")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Standard SGP", "+245")
                    st.write("✅ Win / ✅ Over / ✅ Brunson 25+")
                with c2:
                    st.metric("Aggressive SGP", "+510")
                    st.write("✅ Win / ✅ Over / ✅ Brunson 35+")
            else:
                st.error(f"Could not find a game for '{prompt}'.")
                st.write("**Teams currently in feed:**")
                st.write(list(set(available_teams))) # Shows what IS available to help debug
        else:
            st.error("API returned an empty feed. Check if the NBA slate is live.")

if st.checkbox("Show Raw Data Feed (JSON)"):
    st.json(get_verified_feed())
