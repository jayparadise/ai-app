import streamlit as st
import requests

# Use your key
API_KEY = "10019992-c9b1-46b5-be2c-9e760b1c2041"
# Note: Try 'https://api.oddsblaze.com/v1' or 'https://odds.oddsblaze.com/v1' 
# if one fails.
BASE_URL = "https://api.oddsblaze.com/v1"

st.title("🛠️ OddsBlaze Robust Tester")

def fetch_data(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    if params is None:
        params = {}
    params["key"] = API_KEY
    
    # Adding a User-Agent often fixes 'char 0' errors 
    # because it prevents the server from thinking you are a bot.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        
        # If it's not JSON, this will fail gracefully
        if response.status_code == 200:
            try:
                return response.json()
            except:
                st.error("Server returned 200 OK, but it wasn't JSON.")
                st.text(f"Raw Response: {response.text[:500]}") # Show first 500 chars
        else:
            st.error(f"Server Error: {response.status_code}")
            st.text(f"Response Body: {response.text}")
            
    except Exception as e:
        st.error(f"Request Failed: {e}")
    return None

if st.button("Try Connectivity Again"):
    # 1. Test League list
    leagues = fetch_data("leagues")
    if leagues:
        st.success("✅ Successfully pulled leagues!")
        st.json(leagues)
        
    # 2. Test NBA Odds
    odds = fetch_data("odds", params={"league": "nba"})
    if odds:
        st.success(f"✅ Found {len(odds)} NBA games!")
        st.json(odds)
