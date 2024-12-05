import streamlit as st
import sys
import os

from utils.pages_utils import *

st.set_page_config(page_title="NBA Dashboard", page_icon="🏀", layout="wide")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.DB import DB

db_instance = DB()
db_instance.connect()

st.session_state["db_instance"] = db_instance

st.logo("https://seeklogo.com/images/N/nba-logo-41668C66DB-seeklogo.com.png",
        size="large")

pages = [games_page, player_page, team_page, game_page]

navigate_to_page(pages)



