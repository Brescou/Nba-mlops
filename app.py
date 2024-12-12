import streamlit as st
import sys
import os

if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NBA Dashboard", page_icon=":basketball:", layout="wide"
    )
    st.session_state["page_config_set"] = True

import logging

from utils.utils import ROOT_DIR


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.DB import DB

db_instance = DB()
db_instance.connect()


games_page = st.Page(os.path.join(ROOT_DIR, "app_pages/games.py"), title="Games")
player_page = st.Page(os.path.join(ROOT_DIR, "app_pages/player.py"), title="Player")
team_page = st.Page(os.path.join(ROOT_DIR, "app_pages/team.py"), title="Team")
game_page = st.Page(os.path.join(ROOT_DIR, "app_pages/game.py"), title="Game")
home_page = st.Page(os.path.join(ROOT_DIR, "app_pages/home.py"), title="Home")


st.session_state["db_instance"] = db_instance

st.logo(
    "https://seeklogo.com/images/N/nba-logo-41668C66DB-seeklogo.com.png", size="large"
)


pg = st.navigation([home_page, games_page, player_page, team_page, game_page])


pg.run()
