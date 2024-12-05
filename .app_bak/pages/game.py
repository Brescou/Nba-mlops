import streamlit as st
from app.utils import fetch_game_details
from db.DB import DB

st.set_page_config(page_title="Game Details", page_icon="🏀", layout="wide")

st.title("Game Details")

db_instance = DB()
db_instance.connect()

game_id = st.session_state.get("selected_game_id")

if not game_id:
    st.warning("No game selected.")
else:
    game_details = fetch_game_details(db_instance, game_id)
    if game_details.empty:
        st.error("Game not found.")
    else:
        st.write(game_details)
