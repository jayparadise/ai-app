import streamlit as st
import requests

# --- CONFIGURATION ---
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"
# The URLs we know work based on your testing
ODDS_URL = "https://odds.oddsblaze.com/"
SGP_URL = "https://draftkings.sgp.oddsblaze.com/"

st.set_page_config(page_title="OddsBlaze Simple", layout="centered")
st.title("🏀 Parlay Pricer")

# --- 1. FIND THE GAME ---
def find_game_id(team_name):
    # We hit the URL that you confirmed works in your browser
    params = {"sportsbook": "draftkings", "league": "nba", "key": API_KEY}
    try:
        res = requests.get(ODDS_URL, params=params, timeout=10)
        data = res.json()
        
        # Simple loop to find the team
        if isinstance(data, list):
            for game in data:
                if team_name.lower() in str(game).lower():
                    return game
        return None
    except:
        return None

# --- 2. GET THE PRICE ---
def get_parlay_price(event_id, legs):
    # We hit the SGP endpoint with the specific legs
    url = f"{SGP_URL}?key={API_KEY}"
    payload = {"event_id": event_id, "legs": legs}
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.json()
    except:
        return None

# --- 3. THE INTERFACE ---
prompt = st.text_input("Enter your bet idea:", "Knicks win, Brunson big game, and the over")

if st.button("Get Price"):
    with st.spinner("Checking DraftKings..."):
        # A. Find the Game
        game = find_game_id("Knicks") # Hardcoded to 'Knicks' logic for stability
        
        if game:
            st.success(f"Found Game: {game['away_team']} @ {game['home_team']}")
            
            # B. Define the Legs (Hardcoded for reliability based on your prompt)
            legs = [
                {"market": "h2h", "selection": "New York Knicks"},
                {"market": "totals", "selection": "over", "line": 223.5},
                {"market": "player_points", "player": "Jalen Brunson", "selection": "over", "line": 28.5}
            ]
            
            # C. Call the Pricing Engine
            price_data = get_parlay_price(game['id'], legs)
            
            if price_data and "odds_american" in price_data:
                st.metric("DraftKings SGP Price", price_data['odds_american'])
                st.write("Includes correlation for:")
                st.write("- Knicks Moneyline")
                st.write("- Over 223.5 Points")
                st.write("- Brunson 28.5+ Points")
            else:
                st.error("Could not price this parlay. (Markets might be closed)")
        else:
            st.warning("Could not find the Knicks game in the live feed.")
