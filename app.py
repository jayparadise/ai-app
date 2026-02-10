import streamlit as st
import requests
import re

# --- CONFIGURATION ---
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"
BASE_URL = "https://api.oddsblaze.com/v1"

# --- BACKEND FUNCTIONS ---

@st.cache_data(ttl=600)
def get_all_nba_games():
    """Fetch live/upcoming NBA games from OddsBlaze."""
    try:
        response = requests.get(f"{BASE_URL}/odds", params={"key": API_KEY, "league": "nba"})
        return response.json()
    except:
        return []

def get_sgp_price(event_id, legs):
    """Price a specific set of legs via DraftKings on OddsBlaze."""
    payload = {
        "key": API_KEY,
        "sportsbook": "draftkings",
        "event_id": event_id,
        "legs": legs
    }
    try:
        res = requests.post(f"{BASE_URL}/same_game_parlay", json=payload)
        return res.json()
    except:
        return None

def parse_prompt(prompt, games):
    """Fuzzy logic to find the game and market intent from user text."""
    prompt = prompt.lower()
    found_event = None
    
    # 1. Match the team to get the Event ID
    for game in games:
        if any(team.lower() in prompt for team in [game['home_team'], game['away_team']]):
            found_event = game
            break
            
    if not found_event:
        return None, None

    # 2. Extract specific intent
    # We look for keywords to decide which markets to include
    intent_legs = []
    
    # Check for Moneyline
    if "win" in prompt or "ml" in prompt:
        team_name = found_event['home_team'] if found_event['home_team'].lower() in prompt else found_event['away_team']
        intent_legs.append({"market": "h2h", "selection": team_name})
    
    # Check for Over/Under
    if "over" in prompt or "points" in prompt:
        intent_legs.append({"market": "totals", "selection": "over", "line": 223.5})
        
    # Check for Player Props (Mocking Brunson for the demo logic)
    if "brunson" in prompt:
        intent_legs.append({"market": "player_points", "player": "Jalen Brunson", "selection": "over", "line": 27.5})

    return found_event, intent_legs

# --- STREAMLIT FRONTEND ---

st.set_page_config(page_title="ParlayBlaze Demo", layout="wide")

st.title("🏀 ParlayBlaze AI Demo")
st.markdown("### DraftKings Correlated SGP Pricing Engine")

# App Sidebar
with st.sidebar:
    st.image("https://docs.oddsblaze.com/img/logo.svg", width=150) # Assuming the logo path
    st.info("Currently monitoring live NBA feeds.")
    st.write("**Active Key:** `1001...2041`")

# Main Interface
prompt = st.text_input("Describe your bet idea:", value="Knicks win, over points, and Jalen Brunson points")

if st.button("Generate & Price on DraftKings", type="primary"):
    games = get_all_nba_games()
    event, legs = parse_prompt(prompt, games)
    
    if event and legs:
        st.subheader(f"Pricing Matchup: {event['away_team']} @ {event['home_team']}")
        
        # We generate 3 difficulty levels for the demo
        levels = [
            {"name": "Conservative", "offset": -5},
            {"name": "Standard", "offset": 0},
            {"name": "Aggressive", "offset": +5}
        ]
        
        cols = st.columns(3)
        for i, lvl in enumerate(levels):
            # Adjust the lines based on the level
            current_legs = []
            for leg in legs:
                new_leg = leg.copy()
                if "line" in new_leg:
                    new_leg["line"] += lvl["offset"]
                current_legs.append(new_leg)
            
            # Fetch real price
            data = get_sgp_price(event['id'], current_legs)
            
            with cols[i]:
                st.metric(label=lvl['name'], value=data.get('odds_american', 'N/A') if data else "N/A")
                st.caption(f"Win Probability: {data.get('implied_probability', '??')}%")
                for l in current_legs:
                    st.write(f"✅ {l.get('player', l.get('selection'))} {l.get('line', '')}")
                st.button("Bet This Slip", key=f"btn_{i}")
    else:
        st.error("Could not find a matching live game. Try mentioning 'Knicks' or 'Lakers'.")

st.divider()
st.caption("Powered by OddsBlaze API | Built for DraftKings SGP Markets")
