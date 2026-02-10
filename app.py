import streamlit as st
import requests
import json

# Try to get key from secrets, fallback to hardcoded for this demo
API_KEY = st.secrets.get("ODDSBLAZE_KEY", "10019992-c9b1-46b5-be2c-9e760b1c2041")
BASE_URL = "https://api.oddsblaze.com/v1"

st.set_page_config(page_title="OddsBlaze Connection Tester", layout="wide")
st.title("🛠️ API Connection Debugger")

# Checkbox to show raw data
debug_mode = st.checkbox("Show Raw API Responses", value=True)

def test_connection():
    # Attempt 1: Just get leagues to see if Key is valid
    url = f"{BASE_URL}/leagues"
    params = {"key": API_KEY}
    
    st.write("---")
    st.write("### Test 1: Connectivity & Key Check")
    try:
        r = requests.get(url, params=params)
        st.write(f"**Status Code:** {r.status_code}")
        if debug_mode:
            st.json(r.json())
        return r.status_code == 200
    except Exception as e:
        st.error(f"Connection Failed: {e}")
        return False

def pull_nba_odds():
    # Attempt 2: Pull real NBA data
    url = f"{BASE_URL}/odds"
    params = {"key": API_KEY, "league": "nba"}
    
    st.write("---")
    st.write("### Test 2: NBA Game Feed")
    try:
        r = requests.get(url, params=params)
        data = r.json()
        
        if not data:
            st.warning("⚠️ Connected, but NBA list is EMPTY. It might be off-season or between games.")
        else:
            st.success(f"✅ Found {len(data)} games!")
            for game in data:
                st.write(f"👉 {game.get('away_team')} @ {game.get('home_team')} (ID: `{game.get('id')}`)")
        
        if debug_mode:
            st.json(data)
    except Exception as e:
        st.error(f"Failed to fetch NBA odds: {e}")

# EXECUTE TESTS
if st.button("Run Connection Tests"):
    if test_connection():
        pull_nba_odds()
