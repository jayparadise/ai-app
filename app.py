import streamlit as st
import requests

# Exact configuration based on your working URL
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"
# We use the root URL since your browser test confirms this is where the data lives
BASE_URL = "https://odds.oddsblaze.com" 

st.set_page_config(page_title="OddsBlaze AI Demo", layout="wide")
st.title("🏀 OddsBlaze AI Parlay Builder")

def get_data():
    """Fetches the full DK NBA market feed."""
    params = {
        "sportsbook": "draftkings",
        "league": "nba",
        "key": API_KEY
    }
    try:
        # No extra path needed based on your working link
        response = requests.get(BASE_URL, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- UI LOGIC ---
prompt = st.text_input("Describe your parlay:", "Knicks win, Jalen Brunson points, over points")

if st.button("Generate & Price"):
    with st.spinner("Fetching Live DraftKings Data..."):
        data = get_data()
        
        if data:
            # The OddsBlaze feed structure usually returns a list of events
            # We search for the team mentioned in your prompt
            matched_event = None
            search_term = "Knicks" # This would be dynamic in the full version
            
            for event in data:
                if search_term.lower() in event.get('home_team', '').lower() or \
                   search_term.lower() in event.get('away_team', '').lower():
                    matched_event = event
                    break
            
            if matched_event:
                st.success(f"Matched: {matched_event['away_team']} @ {matched_event['home_team']}")
                
                # Layout for the parlay results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Safe Parlay", "+180")
                    st.write("✅ Knicks ML")
                    st.write("✅ Over 215.5")
                with col2:
                    st.metric("Value Parlay", "+258")
                    st.write("✅ Knicks ML")
                    st.write("✅ Over 223.5")
                with col3:
                    st.metric("Lotto Parlay", "+550")
                    st.write("✅ Knicks ML")
                    st.write("✅ Brunson 35+ Pts")
            else:
                st.warning(f"Could not find a live game for '{search_term}' in the current feed.")
                if st.checkbox("Show Raw Feed"):
                    st.json(data)
