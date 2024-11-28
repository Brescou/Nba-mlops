import pandas as pd
import streamlit as st

from app.utils import fetch_seasons, fetch_games_by_season
from db.DB import DB

st.title("NBA Games")

# Initialisation des variables d'état
if "current_page" not in st.session_state:
    st.session_state["current_page"] = 1
if "matches_per_page" not in st.session_state:
    st.session_state["matches_per_page"] = 10

# Connexion à la base de données
db_instance = DB()
db_instance.connect()

# Fonction pour gérer les changements de page via le slider
def update_page():
    st.session_state["current_page"] = st.session_state["slider_page"]

# Récupération des saisons
seasons = fetch_seasons(db_instance)
if isinstance(seasons, pd.DataFrame) and seasons.empty:
    st.warning("No seasons found.")
else:
    # Sélection de la saison
    season_col = st.columns([2, 6, 2])  # Largeur centrée pour le sélecteur
    with season_col[1]:
        selected_season = st.selectbox("Choose a season:", options=seasons)

    if selected_season:
        matches = fetch_games_by_season(db_instance, selected_season)
        if matches.empty:
            st.info(f"No matches found for season {selected_season}.")
        else:
            # Pagination
            total_matches = len(matches)
            matches_per_page = st.session_state["matches_per_page"]
            total_pages = (total_matches + matches_per_page - 1) // matches_per_page

            # Gestion des interactions utilisateur
            st.divider()  # Ligne de séparation
            pagination_cols = st.columns([1, 4, 1, 2])  # Largeurs ajustées pour alignement
            with pagination_cols[0]:
                if st.button("⬅️", help="Previous Page") and st.session_state["current_page"] > 1:
                    st.session_state["current_page"] -= 1
            with pagination_cols[1]:
                st.slider(
                    "Go to page:",
                    min_value=1,
                    max_value=total_pages,
                    value=st.session_state["current_page"],
                    step=1,
                    key="slider_page",
                    on_change=update_page,
                )
            with pagination_cols[2]:
                if st.button("➡️", help="Next Page") and st.session_state["current_page"] < total_pages:
                    st.session_state["current_page"] += 1
            with pagination_cols[3]:
                matches_per_page = st.selectbox(
                    "Matches per page:",
                    [5, 10, 20, 50],
                    index=[5, 10, 20, 50].index(st.session_state["matches_per_page"]),
                )
                if matches_per_page != st.session_state["matches_per_page"]:
                    st.session_state["matches_per_page"] = matches_per_page
                    st.session_state["current_page"] = 1

            # Calcul des indices pour afficher les matchs
            start_idx = (st.session_state["current_page"] - 1) * matches_per_page
            end_idx = min(start_idx + matches_per_page, total_matches)
            paginated_matches = matches.iloc[start_idx:end_idx]

            # Afficher les matchs
            st.write(
                f"Page {st.session_state['current_page']} / {total_pages} "
                f"(Matches {start_idx + 1} to {end_idx} of {total_matches})"
            )
            for _, match in paginated_matches.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"{match['home_team_name']} vs {match['away_team_name']}")
                col2.write(f"{match['home_team_score']} - {match['away_team_score']}")
                if col3.button("Details", key=match["game_id"]):
                    st.session_state["selected_game_id"] = match["game_id"]
                    st.switch_page("/Users/thomasrivemale/PycharmProjects/Nba-Mlops/app/pages/game.py")
