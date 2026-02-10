import streamlit as st
import requests
import json
import pandas as pd

# --- CONFIGURATION ---
# Your Specific Key
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"

# The EXACT URLs from your documentation
ODDS_URL = "https://odds.oddsblaze.com/"
SGP_URL = "https://draftkings.sgp.oddsblaze.com/"

st.set_page_config(page_title="OddsBlaze Pro Builder", layout="wide", page_icon="🏀")

# --- BACKEND FUNCTIONS ---

@st.cache_data(ttl=60)
def fetch_live_feed():
    """
    Hits the working URL you provided to get all NBA games/odds.
    """
    params = {
        "sportsbook": "draftkings",
        "league": "nba",
        "key": API_KEY
    }
    try:
        # We use a timeout to prevent hanging
        response = requests.get(ODDS_URL, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": "Connection Failed", "details": str(e)}

def calculate_sgp_price(event_id, legs):
    """
    Sends the legs to the SGP engine for correlated pricing.
    """
    # Key is passed in query string for SGP endpoint usually
    url = f"{SGP_URL}?key={API_KEY}"
    
    payload = {
        "event_id": event_id,
        "legs": legs
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "StreamlitApp/1.0"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- FRONTEND INTERFACE ---

st.title("🏀 OddsBlaze Pro Builder")
st.markdown("### DraftKings SGP Pricing Engine")

# Create Tabs for cleanliness
tab1, tab2 = st.tabs(["⚡ Parlay Generator", "🛠️ System Diagnostics"])

# --- TAB 1: GENERATOR ---
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("Step 1: Find Game")
        # 1. Load Data
        feed_data = fetch_live_feed()
        
        # Check for errors immediately
        if isinstance(feed_data, dict) and "error" in feed_data:
            st.error(f"API Error: {feed_data['error']}")
            st.stop()
            
        if not feed_data:
            st.warning("Feed is active but returned 0 games. (Off-hours?)")
            st.stop()
            
        # 2. Extract Teams for Dropdown
        # We map "Knicks" -> "New York Knicks" automatically
        game_map = {}
        team_list = []
        
        for game in feed_data:
            # Create a label like "Knicks @ Celtics"
            label = f"{game['away_team']} @ {game['home_team']}"
            game_map[label] = game
            team_list.append(label)
            
        selected_game_label = st.selectbox("Select Active Game:", team_list)
        selected_game = game_map[selected_game_label]
        
        st.write("---")
        st.info("Step 2: Define Parlay")
        
        # Simple inputs for the demo
        bet_type = st.radio("Who wins?", [selected_game['away_team'], selected_game['home_team']])
        total_line = st.number_input("Total Points Line", value=220.5, step=0.5)
        total_side = st.selectbox("Total Side", ["Over", "Under"])
        
        player_name = st.text_input("Player Name (Exact Spelling)", "Jalen Brunson")
        player_points = st.number_input("Player Points", value=24.5, step=1.0)
        
        if st.button("🚀 Price This Parlay", type="primary"):
            # Construct the Legs JSON
            legs = [
                {"market": "h2h", "selection": bet_type},
                {"market": "totals", "selection": total_side.lower(), "line": total_line},
                {"market": "player_points", "player": player_name, "selection": "over", "line": player_points}
            ]
            
            # Call API
            with st.spinner("Calculating correlation with DraftKings..."):
                result = calculate_sgp_price(selected_game['id'], legs)
                
                st.write("---")
                if "odds_american" in result:
                    st.success(f"## Odds: {result['odds_american']}")
                    st.metric("Implied Probability", f"{result.get('implied_probability', 'N/A')}%")
                else:
                    st.error("Pricing Failed")
                    st.json(result) # Show error detail

    with col2:
        st.write("#### Live Market Data for Selected Game")
        if selected_game:
            st.json(selected_game)

# --- TAB 2: DIAGNOSTICS ---
with tab2:
    st.write("Use this tab to verify the API is actually sending data.")
    if st.button("Refresh Raw Feed"):
        raw = fetch_live_feed()
        st.write(f"**Status:** {'Online' if raw else 'Offline'}")
        st.write(f"**Games Found:** {len(raw) if isinstance(raw, list) else 0}")
        st.code(json.dumps(raw, indent=2), language="json")
