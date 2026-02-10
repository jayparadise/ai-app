import streamlit as st
import requests

# --- CONFIGURATION ---
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"
FEED_URL = "https://odds.oddsblaze.com"
SGP_URL = "https://draftkings.sgp.oddsblaze.com"

st.set_page_config(page_title="OddsBlaze SGP Builder", layout="wide")
st.title("🏀 OddsBlaze SGP BlazeBuilder")
st.write("Pricing live correlated parlays via DraftKings.")

def get_live_feed():
    """Fetches the main NBA market feed to find event IDs."""
    params = {"sportsbook": "draftkings", "league": "nba", "key": API_KEY}
    try:
        res = requests.get(FEED_URL, params=params, timeout=15)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def get_sgp_price(event_id, legs):
    """Hits the specialized SGP subdomain for pricing."""
    # The SGP engine usually takes the key as a query param
    url = f"{SGP_URL}/" 
    payload = {
        "event_id": event_id,
        "legs": legs
    }
    try:
        # Note: Some OddsBlaze configs take the key in the JSON or as a query param
        res = requests.post(url, params={"key": API_KEY}, json=payload, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# --- UI LOGIC ---
prompt = st.text_input("Enter team (e.g., 'Knicks'):", value="Knicks")

if st.button("Build SGP Variations"):
    with st.spinner("Finding live markets..."):
        feed = get_live_feed()
        # Find the game ID
        game = next((g for g in feed if prompt.lower() in str(g).lower()), None)
        
        if game:
            event_id = game.get('id')
            st.success(f"Matched Game: {game.get('away_team')} @ {game.get('home_team')} (ID: {event_id})")
            
            # Example Legs (In a full app, these would be parsed from your text)
            variations = [
                {"name": "Standard Over", "line": 223.5, "pts": 27.5},
                {"name": "Aggressive Over", "line": 228.5, "pts": 32.5}
            ]
            
            cols = st.columns(2)
            for i, var in enumerate(variations):
                legs = [
                    {"market": "h2h", "selection": "New York Knicks"},
                    {"market": "totals", "selection": "over", "line": var["line"]},
                    {"market": "player_points", "player": "Jalen Brunson", "selection": "over", "line": var["pts"]}
                ]
                
                # PRICE IT
                price_data = get_sgp_price(event_id, legs)
                
                with cols[i]:
                    st.metric(var["name"], price_data.get("odds_american", "N/A"))
                    st.json(legs)
        else:
            st.warning("No live game found for that team. Check the NBA slate!")
