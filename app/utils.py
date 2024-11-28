import streamlit as st


def colorize_multiselect_options(colors: list[str]) -> None:
    rules = ""
    n_colors = len(colors)

    for i, color in enumerate(colors):
        rules += f""".stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]:nth-child({n_colors}n+{i + 1}){{background-color: {color};}}"""

    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)


def get_seasons_from_db(db):
    query = "SELECT DISTINCT season_year FROM game ORDER BY season_year DESC;"
    seasons = db.fetch_data(query)
    return [season[0] for season in seasons]

def fetch_games_by_season(db, season):
    query = """
        SELECT game_id, date, home_team_id, away_team_id, result
        FROM game
        WHERE season_year = %s
        ORDER BY date ASC;
    """
    games = db.fetch_data_with_params(query, (season,))
    return games