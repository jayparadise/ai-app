import streamlit as st
import requests

# --- 1. CONFIGURATION ---
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"
BASE_URL = "https://api.oddsblaze.com/v1"

st.set_page_config(page_title="OddsBlaze App", layout="centered")
st.title("🏀 OddsBlaze Parlay Builder")

# --- 2. THE LOGIC (Based on your working snippet) ---
def find_game_id(team_name):
    """Finds the Event ID for the team you type."""
    odds_url = f"{BASE_URL}/odds"
    # Note: GET requests take key in params
    params = {"key": API_KEY, "league": "nba"}
    
    try:
        response = requests.get(odds_url, params=params)
        events = response.json()
        
        # Search for the team
        for event in events:
            if team_name.lower() in event['home_team'].lower() or \
               team_name.lower() in event['away_team'].lower():
                return event
        return None
    except Exception as e:
        st.error(f"Error finding game: {e}")
        return None

def get_sgp_price(event_id, legs):
    """Prices the parlay using your exact working POST structure."""
    sgp_url = f"{BASE_URL}/same_game_parlay"
    
    # Note: POST requests take key in the JSON body (payload)
    payload = {
        "key": API_KEY,
        "sportsbook": "draftkings",
        "event_id": event_id,
        "legs": legs
    }

    try:
        sgp_response = requests.post(sgp_url, json=payload)
        return sgp_response.json()
    except Exception as e:
        st.error(f"Error pricing parlay: {e}")
        return None

# --- 3. THE INTERFACE ---
st.write("Enter a team name to generate a DraftKings SGP.")
team_input = st.text_input("Team Name:", "Knicks")

if st.button("Generate Parlay Price"):
    with st.spinner(f"Searching for {team_input}..."):
        # A. Find the Game
        game = find_game_id(team_input)
        
        if game:
            st.success(f"Found Game: {game['away_team']} @ {game['home_team']}")
            
            # B. Define Legs (We use the Knicks/Brunson example you liked)
            # You can make these dynamic later, but let's keep it simple for now.
            legs = [
                {"market": "h2h", "selection": "New York Knicks"},
                {"market": "totals", "selection": "over", "line": 223.5},
                {"market": "player_points", "player": "Jalen Brunson", "selection": "over", "line": 26.5}
            ]
            
            # C. Get Price
            result = get_sgp_price(game['id'], legs)
            
            if result and 'odds_american' in result:
                st.metric("DraftKings Odds", result['odds_american'])
                st.write(f"Implied Win Probability: **{result.get('implied_probability')}%**")
                
                with st.expander("See Parlay Legs"):
                    st.write(legs)
            else:
                st.error("Could not price parlay. (Market might be closed or correlated legs invalid)")
                st.json(result) # Show error if any
        else:
            st.warning(f"Could not find a game for '{team_input}' today.")
