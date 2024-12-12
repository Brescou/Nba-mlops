import re
import pandas as pd
import streamlit as st
import logging
from geopy.geocoders import Nominatim
import time
import requests
import json
import plotly.express as px
import plotly.graph_objects as go

from utils.utils import fetch_seasons

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("Team")

db = st.session_state["db_instance"]

search_container = st.container()

with search_container:
    st.markdown("### Recherches")
    col = st.columns([1, 4])

    with col[0]:
        seasons = fetch_seasons(db)
        selected_season = st.selectbox("Saison", seasons, index=0, key="team_season")
        teams_query = """
            SELECT DISTINCT t.team_id, t.name 
            FROM team t
            JOIN team_boxscore tb ON t.team_id = tb.team_id
            WHERE tb.season_year = %s
            ORDER BY t.name
         """
        teams = db.fetch_dataframe(teams_query, (selected_season,))

        teams_names = {f"{row['name']}": row["team_id"] for _, row in teams.iterrows()}
        selected_team = st.selectbox("Equipe", teams_names.keys(), index=0, key="team")

        if selected_team:
            team_id = teams_names[selected_team]

    with col[1]:
        team_info_query = """
            SELECT team_id, name, city, abbreviation
            FROM team
            WHERE team_id = %s
        """
        team_info = db.fetch_dataframe(team_info_query, (team_id,)).iloc[0]

        city_mapping = {
            "LA": "Los Angeles",
            "NY": "New York",
            "BROOKLYN": "Brooklyn",
            "GS": "San Francisco",
        }

        search_city = city_mapping.get(team_info["city"], team_info["city"])

        geolocator = Nominatim(user_agent="nba_app")
        location = geolocator.geocode(f"{search_city}, USA", exactly_one=True)

        wiki_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": search_city,
            "prop": "revisions",
            "rvprop": "content",
            "rvsection": "0",
            "rvslots": "*",
        }

        try:
            response = requests.get(wiki_url, params=params)
            if response.status_code == 200:
                data = response.json()
                pages = data["query"]["pages"]
                page = next(iter(pages.values()))
                content = page["revisions"][0]["slots"]["main"]["*"]

                population_match = re.search(
                    r"\|\s*population_total\s*=\s*([0-9,]+)", content
                )
                if population_match:
                    city_pop = int(population_match.group(1).replace(",", ""))
                else:
                    city_pop = None
            else:
                city_pop = None
        except Exception as e:
            print(f"Erreur lors de la récupération des données Wikipedia: {e}")
            city_pop = None

        image_url = (
            f"https://cdn.nba.com/logos/nba/{team_info['team_id']}/global/L/logo.svg"
        )

        population_info = (
            f"""<p style="margin: 5px 0;"><strong>Population:</strong> {'{:,}'.format(city_pop).replace(',', ' ')} habitants</p>"""
            if city_pop
            else ""
        )

        st.markdown(
            f"""
            <div style="display: flex; gap: 20px; border-radius: 10px; border: 1px solid #ddd; background-color: #f8f9fa; padding: 20px;">
                <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
                    <img src="{image_url}" alt="Logo de l'équipe" style="width: 100px; height: auto;">
                    <div>
                        <h3 style="margin: 0;">{team_info['city']} {team_info['name']}</h3>
                        <p style="margin: 5px 0;"><strong>Abréviation:</strong> {team_info['abbreviation']}</p>
                    </div>
                </div>
                <div style="flex: 1; border-left: 1px solid #ddd; padding-left: 20px;">
                    <h4 style="margin-top: 0;">Informations sur {search_city}</h4>
                    <p style="margin: 5px 0;"><strong>État:</strong> {location.address.split(', ')[-2]}</p>
                    <p style="margin: 5px 0;"><strong>Coordonnées:</strong> {location.latitude:.2f}°N, {location.longitude:.2f}°W</p>
                    {population_info}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

content_container = st.container()

with content_container:

    tab_games, tab_roster, tab_boxscore, tab_stats = st.tabs(
        ["Games", "Roster", "Boxscore", "Stats"]
    )

    with tab_games:
        st.markdown("### Games")

        games_query = """
            SELECT g.game_id, g.date,
                   ht.team_id as home_team_id, ht.name as home_team,
                   at.team_id as away_team_id, at.name as away_team,
                   home_tb.pts as home_team_score,
                   away_tb.pts as away_team_score
            FROM game g
            JOIN team ht ON g.home_team_id = ht.team_id 
            JOIN team at ON g.away_team_id = at.team_id
            JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
            JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
            JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
            JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
            WHERE (g.home_team_id = %s OR g.away_team_id = %s)
            AND g.season_year = %s
            ORDER BY g.date DESC
        """
        games = db.fetch_dataframe(games_query, (team_id, team_id, selected_season))

        if not games.empty:
            games["date"] = pd.to_datetime(games["date"]).dt.strftime("%d/%m/%Y")

            games["Score"] = games.apply(
                lambda x: f"{x['home_team_score']} - {x['away_team_score']}", axis=1
            )

            games["Match"] = games.apply(
                lambda x: (
                    '<div style="display: flex; align-items: center; justify-content: space-between; padding: 10px;">'
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    f'<img src="https://cdn.nba.com/logos/nba/{x["home_team_id"]}/global/L/logo.svg" '
                    'style="width: 40px; height: 40px;">'
                    f'<span>{x["home_team"]}</span>'
                    "</div>"
                    f'<strong>{x["Score"]}</strong>'
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    f'<span>{x["away_team"]}</span>'
                    f'<img src="https://cdn.nba.com/logos/nba/{x["away_team_id"]}/global/L/logo.svg" '
                    'style="width: 40px; height: 40px;">'
                    "</div>"
                    "</div>"
                ),
                axis=1,
            )

            display_games = games[["date", "Match"]].copy()
            display_games.columns = ["Date", "Match"]

            st.write(
                display_games.to_html(
                    escape=False, index=False, classes=["dataframe"], justify="center"
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <style>
                    .dataframe {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    .dataframe th {
                        background-color: #f8f9fa;
                        padding: 12px;
                        text-align: center;
                        border: 1px solid #ddd;
                    }
                    .dataframe td {
                        padding: 12px;
                        text-align: center;
                        border: 1px solid #ddd;
                    }
                    .dataframe tr:nth-child(even) {
                        background-color: #f8f9fa;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No games found for this team and season.")

    with tab_roster:
        st.markdown("### Roster")

        players_query = """
            SELECT DISTINCT p.player_id, p.firstname, p.lastname, p.jersey_number, p.position
            FROM player p
            INNER JOIN player_boxscore pb ON p.player_id = pb.player_id 
            WHERE pb.team_id = %s
            AND pb.season_year = %s
            ORDER BY p.lastname, p.firstname
        """

        players = db.fetch_dataframe(players_query, (team_id, selected_season))

        if not players.empty:
            players["Player"] = players["firstname"] + " " + players["lastname"]
            players["Image"] = players["player_id"].apply(
                lambda x: f'<img src="https://cdn.nba.com/headshots/nba/latest/260x190/{x}.png" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">'
            )

            display_players = players[
                ["Image", "Player", "jersey_number", "position"]
            ].copy()
            display_players.columns = ["", "Player", "Jersey", "Position"]

            st.write(
                display_players.to_html(
                    escape=False, index=False, classes=["dataframe"], justify="center"
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <style>
                    .dataframe {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    .dataframe th {
                        background-color: #f8f9fa;
                        padding: 12px;
                        text-align: center;
                        border: 1px solid #ddd;
                    }
                    .dataframe td {
                        padding: 12px;
                        text-align: center;
                        border: 1px solid #ddd;
                        vertical-align: middle;
                    }
                    .dataframe tr:nth-child(even) {
                        background-color: #f8f9fa;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No players found for this team and season.")

    with tab_boxscore:
        st.markdown("### Boxscore")

        tab_base, tab_advanced, tab_four_factors, tab_misc, tab_scoring = st.tabs(
            ["Base", "Advanced", "Four Factors", "Misc", "Scoring"]
        )

        with tab_base:
            query = """
                SELECT 
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN 'vs'
                        ELSE '@'
                    END as location,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away.name
                        ELSE home.name
                    END as opponent,
                    g.date,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN home_tb.pts
                        ELSE away_tb.pts
                    END as team_score,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away_tb.pts
                        ELSE home_tb.pts
                    END as opponent_score,
                    tbb.fgm, tbb.fga, tbb.fg_pct, 
                    tbb.fg3m, tbb.fg3a, tbb.fg3_pct,
                    tbb.ftm, tbb.fta, tbb.ft_pct,
                    tbb.oreb, tbb.dreb, tbb.reb,
                    tbb.ast, tbb.tov, tbb.stl,
                    tbb.blk, tbb.blka, tbb.pf,
                    tbb.pfd, tbb.pts, tbb.plus_minus
                FROM team_boxscore tb
                JOIN team_boxscore_base tbb ON tb.boxscore_id = tbb.boxscore_id
                JOIN game g ON tb.game_id = g.game_id
                JOIN team home ON g.home_team_id = home.team_id
                JOIN team away ON g.away_team_id = away.team_id
                JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
                JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
                JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
                JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
                WHERE tb.team_id = %s 
                AND tb.season_year = %s
                ORDER BY g.date DESC
            """
            boxscore_base = db.fetch_dataframe(query, (team_id, selected_season))

            if not boxscore_base.empty:
                boxscore_base["date"] = pd.to_datetime(
                    boxscore_base["date"]
                ).dt.strftime("%d/%m/%Y")

                boxscore_base["Game"] = boxscore_base.apply(
                    lambda x: f"{x['location']} {x['opponent']} ({x['date']})", axis=1
                )

                boxscore_base["Result"] = boxscore_base.apply(
                    lambda x: f"{x['team_score']} - {x['opponent_score']}", axis=1
                )

                column_renames = {
                    "fgm": "Field Goals Made",
                    "fga": "Field Goals Attempted",
                    "fg_pct": "Field Goal %",
                    "fg3m": "3-Point Field Goals Made",
                    "fg3a": "3-Point Field Goals Attempted",
                    "fg3_pct": "3-Point Field Goal %",
                    "ftm": "Free Throws Made",
                    "fta": "Free Throws Attempted",
                    "ft_pct": "Free Throw %",
                    "oreb": "Offensive Rebounds",
                    "dreb": "Defensive Rebounds",
                    "reb": "Total Rebounds",
                    "ast": "Assists",
                    "tov": "Turnovers",
                    "stl": "Steals",
                    "blk": "Blocks",
                    "blka": "Blocked Attempts",
                    "pf": "Personal Fouls",
                    "pfd": "Personal Fouls Drawn",
                    "pts": "Points",
                    "plus_minus": "Plus/Minus",
                }

                boxscore_base = boxscore_base.rename(columns=column_renames)

                stat_columns = [
                    col
                    for col in boxscore_base.columns
                    if col
                    not in [
                        "location",
                        "opponent",
                        "date",
                        "Game",
                        "Result",
                        "team_score",
                        "opponent_score",
                    ]
                ]
                selected_columns = st.multiselect(
                    "Select columns to display",
                    options=stat_columns,
                    default=[
                        "Points",
                        "Total Rebounds",
                        "Assists",
                        "Field Goal %",
                        "3-Point Field Goal %",
                    ],
                )

                if selected_columns:
                    display_columns = ["Game", "Result"] + selected_columns
                    st.dataframe(
                        boxscore_base[display_columns],
                        use_container_width=True,
                        hide_index=True,
                    )

                    with st.expander("Explanation of Base Stats"):
                        st.markdown(
                            """
                        - **Field Goals Made/Attempted (FGM/FGA):** Number of field goals made and attempted
                        - **Field Goal % (FG%):** Percentage of field goals made
                        - **3-Point Field Goals Made/Attempted (3PM/3PA):** Number of three-pointers made and attempted
                        - **3-Point Field Goal % (3P%):** Percentage of three-pointers made
                        - **Free Throws Made/Attempted (FTM/FTA):** Number of free throws made and attempted
                        - **Free Throw % (FT%):** Percentage of free throws made
                        - **Offensive/Defensive/Total Rebounds (OREB/DREB/REB):** Number of rebounds collected
                        - **Assists (AST):** Number of passes leading directly to made baskets
                        - **Turnovers (TOV):** Number of times the ball was lost to the opposing team
                        - **Steals (STL):** Number of times the ball was stolen from the opposing team
                        - **Blocks (BLK):** Number of opponent shots blocked
                        - **Blocked Attempts (BLKA):** Number of times player's shots were blocked
                        - **Personal Fouls (PF):** Number of fouls committed
                        - **Personal Fouls Drawn (PFD):** Number of fouls drawn
                        - **Points (PTS):** Total points scored
                        - **Plus/Minus (+/-):** Team's point differential while player was on court
                        """
                        )
            else:
                st.info("No base statistics available for this team and season.")

        with tab_advanced:
            query = """
                SELECT 
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN 'vs'
                        ELSE '@'
                    END as location,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away.name
                        ELSE home.name
                    END as opponent,
                    g.date,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN home_tb.pts
                        ELSE away_tb.pts
                    END as team_score,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away_tb.pts
                        ELSE home_tb.pts
                    END as opponent_score,
                    tba.off_rating, tba.def_rating, tba.net_rating,
                    tba.ast_pct, tba.ast_to, tba.ast_ratio,
                    tba.oreb_pct, tba.dreb_pct, tba.reb_pct,
                    tba.tm_tov_pct, tba.efg_pct, tba.ts_pct,
                    tba.pace, tba.pie
                FROM team_boxscore tb
                JOIN team_boxscore_advanced tba ON tb.boxscore_id = tba.boxscore_id
                JOIN game g ON tb.game_id = g.game_id
                JOIN team home ON g.home_team_id = home.team_id
                JOIN team away ON g.away_team_id = away.team_id
                JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
                JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
                JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
                JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
                WHERE tb.team_id = %s 
                AND tb.season_year = %s
                ORDER BY g.date DESC
            """
            boxscore_advanced = db.fetch_dataframe(query, (team_id, selected_season))

            if not boxscore_advanced.empty:
                boxscore_advanced["date"] = pd.to_datetime(
                    boxscore_advanced["date"]
                ).dt.strftime("%d/%m/%Y")

                boxscore_advanced["Game"] = boxscore_advanced.apply(
                    lambda x: f"{x['location']} {x['opponent']} ({x['date']})", axis=1
                )

                boxscore_advanced["Result"] = boxscore_advanced.apply(
                    lambda x: f"{x['team_score']} - {x['opponent_score']}", axis=1
                )

                column_renames = {
                    "off_rating": "Offensive Rating",
                    "def_rating": "Defensive Rating",
                    "net_rating": "Net Rating",
                    "ast_pct": "Assist %",
                    "ast_to": "Assist to Turnover",
                    "ast_ratio": "Assist Ratio",
                    "oreb_pct": "Offensive Rebound %",
                    "dreb_pct": "Defensive Rebound %",
                    "reb_pct": "Rebound %",
                    "tm_tov_pct": "Turnover %",
                    "efg_pct": "Effective FG %",
                    "ts_pct": "True Shooting %",
                    "pace": "Pace",
                    "pie": "PIE",
                }

                boxscore_advanced = boxscore_advanced.rename(columns=column_renames)

                stat_columns = [
                    col
                    for col in boxscore_advanced.columns
                    if col
                    not in [
                        "location",
                        "opponent",
                        "date",
                        "Game",
                        "Result",
                        "team_score",
                        "opponent_score",
                    ]
                ]
                selected_columns = st.multiselect(
                    "Select columns to display",
                    options=stat_columns,
                    default=[
                        "Offensive Rating",
                        "Defensive Rating",
                        "Net Rating",
                        "Pace",
                        "PIE",
                    ],
                )

                if selected_columns:
                    display_columns = ["Game", "Result"] + selected_columns
                    st.dataframe(
                        boxscore_advanced[display_columns],
                        use_container_width=True,
                        hide_index=True,
                    )

                    with st.expander("Explanation of Advanced Stats"):
                        st.markdown(
                            """
                        - **Offensive Rating:** Points scored per 100 possessions
                        - **Defensive Rating:** Points allowed per 100 possessions
                        - **Net Rating:** Difference between offensive and defensive rating
                        - **Assist %:** Percentage of field goals that were assisted
                        - **Assist to Turnover:** Ratio of assists to turnovers
                        - **Assist Ratio:** Percentage of possessions that end with an assist
                        - **Offensive Rebound %:** Percentage of available offensive rebounds obtained
                        - **Defensive Rebound %:** Percentage of available defensive rebounds obtained
                        - **Rebound %:** Percentage of available total rebounds obtained
                        - **Turnover %:** Percentage of possessions that end in a turnover
                        - **Effective FG %:** Field goal percentage adjusted for three-pointers
                        - **True Shooting %:** Shooting percentage adjusted for three-pointers and free throws
                        - **Pace:** Number of possessions per 48 minutes
                        - **PIE (Player Impact Estimate):** Measure of a player's overall statistical contribution
                        """
                        )
            else:
                st.info("No advanced statistics available for this team and season.")

        with tab_four_factors:
            query = """
                SELECT 
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN 'vs'
                        ELSE '@'
                    END as location,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away.name
                        ELSE home.name
                    END as opponent,
                    g.date,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN home_tb.pts
                        ELSE away_tb.pts
                    END as team_score,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away_tb.pts
                        ELSE home_tb.pts
                    END as opponent_score,
                    tbf.efg_pct, tbf.fta_rate,
                    tbf.tm_tov_pct, tbf.oreb_pct,
                    tbf.opp_efg_pct, tbf.opp_fta_rate,
                    tbf.opp_tov_pct, tbf.opp_oreb_pct
                FROM team_boxscore tb
                JOIN team_boxscore_four_factors tbf ON tb.boxscore_id = tbf.boxscore_id
                JOIN game g ON tb.game_id = g.game_id
                JOIN team home ON g.home_team_id = home.team_id
                JOIN team away ON g.away_team_id = away.team_id
                JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
                JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
                JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
                JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
                WHERE tb.team_id = %s 
                AND tb.season_year = %s
                ORDER BY g.date DESC
            """
            boxscore_four_factors = db.fetch_dataframe(
                query, (team_id, selected_season)
            )

            if not boxscore_four_factors.empty:
                boxscore_four_factors["date"] = pd.to_datetime(
                    boxscore_four_factors["date"]
                ).dt.strftime("%d/%m/%Y")

                boxscore_four_factors["Game"] = boxscore_four_factors.apply(
                    lambda x: f"{x['location']} {x['opponent']} ({x['date']})", axis=1
                )

                boxscore_four_factors["Result"] = boxscore_four_factors.apply(
                    lambda x: f"{x['team_score']} - {x['opponent_score']}", axis=1
                )

                column_renames = {
                    "efg_pct": "Effective FG%",
                    "fta_rate": "Free Throw Rate",
                    "tm_tov_pct": "Turnover %",
                    "oreb_pct": "Offensive Rebound %",
                    "opp_efg_pct": "Opponent eFG%",
                    "opp_fta_rate": "Opponent FT Rate",
                    "opp_tov_pct": "Opponent TOV%",
                    "opp_oreb_pct": "Opponent OREB%",
                }

                boxscore_four_factors = boxscore_four_factors.rename(
                    columns=column_renames
                )

                stat_columns = [
                    col
                    for col in boxscore_four_factors.columns
                    if col
                    not in [
                        "location",
                        "opponent",
                        "date",
                        "Game",
                        "Result",
                        "team_score",
                        "opponent_score",
                    ]
                ]
                selected_columns = st.multiselect(
                    "Select columns to display",
                    options=stat_columns,
                    default=[
                        "Effective FG%",
                        "Free Throw Rate",
                        "Turnover %",
                        "Offensive Rebound %",
                    ],
                )

                if selected_columns:
                    display_columns = ["Game", "Result"] + selected_columns
                    st.dataframe(
                        boxscore_four_factors[display_columns],
                        use_container_width=True,
                        hide_index=True,
                    )

                    with st.expander("Explanation of Four Factors"):
                        st.markdown(
                            """
                        The Four Factors are the four most important statistical categories that determine a team's success:

                        **Team Factors:**
                        - **Effective FG%:** (FGM + 0.5 * 3PM) / FGA - Measures shooting efficiency
                        - **Free Throw Rate:** FTA / FGA - Measures ability to get to the free throw line
                        - **Turnover %:** Turnovers / (FGA + 0.44 * FTA + TOV) - Measures ball security
                        - **Offensive Rebound %:** OREB / (OREB + Opp DREB) - Measures offensive rebounding

                        **Opponent Factors:**
                        - **Opponent eFG%:** Opponent's shooting efficiency
                        - **Opponent FT Rate:** Opponent's free throw rate
                        - **Opponent TOV%:** Opponent's turnover percentage
                        - **Opponent OREB%:** Opponent's offensive rebounding percentage

                        These factors are weighted in order of importance:
                        1. Shooting (40%)
                        2. Turnovers (25%)
                        3. Rebounding (20%)
                        4. Free Throws (15%)
                        """
                        )
            else:
                st.info(
                    "No four factors statistics available for this team and season."
                )

        with tab_misc:
            query = """
                SELECT 
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN 'vs'
                        ELSE '@'
                    END as location,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away.name
                        ELSE home.name
                    END as opponent,
                    g.date,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN home_tb.pts
                        ELSE away_tb.pts
                    END as team_score,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away_tb.pts
                        ELSE home_tb.pts
                    END as opponent_score,
                    tbm.pts_paint, tbm.pts_2nd_chance,
                    tbm.pts_fb, tbm.pts_off_tov,
                    tbm.opp_pts_paint, tbm.opp_pts_2nd_chance,
                    tbm.opp_pts_fb, tbm.opp_pts_off_tov
                FROM team_boxscore tb
                JOIN team_boxscore_misc tbm ON tb.boxscore_id = tbm.boxscore_id
                JOIN game g ON tb.game_id = g.game_id
                JOIN team home ON g.home_team_id = home.team_id
                JOIN team away ON g.away_team_id = away.team_id
                JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
                JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
                JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
                JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
                WHERE tb.team_id = %s 
                AND tb.season_year = %s
                ORDER BY g.date DESC
            """
            boxscore_misc = db.fetch_dataframe(query, (team_id, selected_season))

            if not boxscore_misc.empty:
                boxscore_misc["date"] = pd.to_datetime(
                    boxscore_misc["date"]
                ).dt.strftime("%d/%m/%Y")

                boxscore_misc["Game"] = boxscore_misc.apply(
                    lambda x: f"{x['location']} {x['opponent']} ({x['date']})", axis=1
                )

                boxscore_misc["Result"] = boxscore_misc.apply(
                    lambda x: f"{x['team_score']} - {x['opponent_score']}", axis=1
                )

                column_renames = {
                    "pts_paint": "Points in Paint",
                    "pts_2nd_chance": "Second Chance Points",
                    "pts_fb": "Fast Break Points",
                    "pts_off_tov": "Points off Turnovers",
                    "opp_pts_paint": "Opp Points in Paint",
                    "opp_pts_2nd_chance": "Opp Second Chance Points",
                    "opp_pts_fb": "Opp Fast Break Points",
                    "opp_pts_off_tov": "Opp Points off Turnovers",
                }

                boxscore_misc = boxscore_misc.rename(columns=column_renames)

                stat_columns = [
                    col
                    for col in boxscore_misc.columns
                    if col
                    not in [
                        "location",
                        "opponent",
                        "date",
                        "Game",
                        "Result",
                        "team_score",
                        "opponent_score",
                    ]
                ]
                selected_columns = st.multiselect(
                    "Select columns to display",
                    options=stat_columns,
                    default=[
                        "Points in Paint",
                        "Fast Break Points",
                        "Points off Turnovers",
                    ],
                )

                if selected_columns:
                    display_columns = ["Game", "Result"] + selected_columns
                    st.dataframe(
                        boxscore_misc[display_columns],
                        use_container_width=True,
                        hide_index=True,
                    )

                    with st.expander("Explanation of Misc Stats"):
                        st.markdown(
                            """
                        **Team Stats:**
                        - **Points in Paint:** Points scored in the painted area near the basket
                        - **Second Chance Points:** Points scored after offensive rebounds
                        - **Fast Break Points:** Points scored on fast break opportunities
                        - **Points off Turnovers:** Points scored following opponent turnovers

                        **Opponent Stats:**
                        - **Opp Points in Paint:** Points allowed in the painted area
                        - **Opp Second Chance Points:** Points allowed after offensive rebounds
                        - **Opp Fast Break Points:** Points allowed on fast breaks
                        - **Opp Points off Turnovers:** Points allowed following team turnovers
                        """
                        )
            else:
                st.info(
                    "No miscellaneous statistics available for this team and season."
                )

        with tab_scoring:
            query = """
                SELECT 
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN 'vs'
                        ELSE '@'
                    END as location,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away.name
                        ELSE home.name
                    END as opponent,
                    g.date,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN home_tb.pts
                        ELSE away_tb.pts
                    END as team_score,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away_tb.pts
                        ELSE home_tb.pts
                    END as opponent_score,
                    tbs.pct_fga_2pt, tbs.pct_fga_3pt,
                    tbs.pct_pts_2pt, tbs.pct_pts_2pt_mr,
                    tbs.pct_pts_3pt, tbs.pct_pts_fb,
                    tbs.pct_pts_ft, tbs.pct_pts_paint,
                    tbs.pct_ast_2pm, tbs.pct_uast_2pm,
                    tbs.pct_ast_3pm, tbs.pct_uast_3pm
                FROM team_boxscore tb
                JOIN team_boxscore_scoring tbs ON tb.boxscore_id = tbs.boxscore_id
                JOIN game g ON tb.game_id = g.game_id
                JOIN team home ON g.home_team_id = home.team_id
                JOIN team away ON g.away_team_id = away.team_id
                JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
                JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
                JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
                JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
                WHERE tb.team_id = %s 
                AND tb.season_year = %s
                ORDER BY g.date DESC
            """
            boxscore_scoring = db.fetch_dataframe(query, (team_id, selected_season))

            if not boxscore_scoring.empty:
                boxscore_scoring["date"] = pd.to_datetime(
                    boxscore_scoring["date"]
                ).dt.strftime("%d/%m/%Y")

                boxscore_scoring["Game"] = boxscore_scoring.apply(
                    lambda x: f"{x['location']} {x['opponent']} ({x['date']})", axis=1
                )

                boxscore_scoring["Result"] = boxscore_scoring.apply(
                    lambda x: f"{x['team_score']} - {x['opponent_score']}", axis=1
                )

                column_renames = {
                    "pct_fga_2pt": "% FGA 2PT",
                    "pct_fga_3pt": "% FGA 3PT",
                    "pct_pts_2pt": "% PTS 2PT",
                    "pct_pts_2pt_mr": "% PTS Mid-Range",
                    "pct_pts_3pt": "% PTS 3PT",
                    "pct_pts_fb": "% PTS Fast Break",
                    "pct_pts_ft": "% PTS Free Throws",
                    "pct_pts_paint": "% PTS Paint",
                    "pct_ast_2pm": "% Assisted 2PM",
                    "pct_uast_2pm": "% Unassisted 2PM",
                    "pct_ast_3pm": "% Assisted 3PM",
                    "pct_uast_3pm": "% Unassisted 3PM",
                }

                boxscore_scoring = boxscore_scoring.rename(columns=column_renames)

                stat_columns = [
                    col
                    for col in boxscore_scoring.columns
                    if col
                    not in [
                        "location",
                        "opponent",
                        "date",
                        "Game",
                        "Result",
                        "team_score",
                        "opponent_score",
                    ]
                ]
                selected_columns = st.multiselect(
                    "Select columns to display",
                    options=stat_columns,
                    default=[
                        "% PTS Paint",
                        "% PTS 3PT",
                        "% PTS Fast Break",
                        "% PTS Free Throws",
                    ],
                )

                if selected_columns:
                    display_columns = ["Game", "Result"] + selected_columns
                    st.dataframe(
                        boxscore_scoring[display_columns],
                        use_container_width=True,
                        hide_index=True,
                    )

                    with st.expander("Explanation of Scoring Stats"):
                        st.markdown(
                            """
                        **Shot Distribution:**
                        - **% FGA 2PT/3PT:** Percentage of field goal attempts from 2-point/3-point range
                        - **% PTS 2PT:** Percentage of points from 2-point field goals
                        - **% PTS Mid-Range:** Percentage of points from mid-range shots
                        - **% PTS 3PT:** Percentage of points from 3-point field goals
                        - **% PTS Fast Break:** Percentage of points from fast breaks
                        - **% PTS Free Throws:** Percentage of points from free throws
                        - **% PTS Paint:** Percentage of points in the paint

                        **Assist Distribution:**
                        - **% Assisted 2PM:** Percentage of made 2-pointers that were assisted
                        - **% Unassisted 2PM:** Percentage of made 2-pointers that were unassisted
                        - **% Assisted 3PM:** Percentage of made 3-pointers that were assisted
                        - **% Unassisted 3PM:** Percentage of made 3-pointers that were unassisted
                        """
                        )
            else:
                st.info("No scoring statistics available for this team and season.")

    with tab_stats:
        st.markdown("### Season Statistics")

        tab_overview, tab_charts = st.tabs(["Overview", "Charts"])

        with tab_overview:
            query_avg_stats = """
                WITH TeamStats AS (
                    SELECT 
                        t.team_id,
                        t.name as team_name,
                        ROUND(AVG(CASE 
                            WHEN g.home_team_id = tb.team_id THEN home_tb.pts
                            ELSE away_tb.pts
                        END), 1) as pts_scored,
                        ROUND(AVG(CASE 
                            WHEN g.home_team_id = tb.team_id THEN away_tb.pts
                            ELSE home_tb.pts
                        END), 1) as pts_allowed,
                        ROUND(AVG(tbb.reb), 1) as avg_rebounds,
                        ROUND(AVG(tbb.ast), 1) as avg_assists,
                        ROUND(AVG(tbb.fg_pct) * 100, 1) as avg_fg_pct,
                        ROUND(AVG(tbb.fg3_pct) * 100, 1) as avg_fg3_pct
                    FROM team_boxscore tb
                    JOIN team_boxscore_base tbb ON tb.boxscore_id = tbb.boxscore_id
                    JOIN team t ON tb.team_id = t.team_id
                    JOIN game g ON tb.game_id = g.game_id
                    JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
                    JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
                    JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
                    JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
                    WHERE tb.season_year = %s
                    GROUP BY t.team_id, t.name
                ),
                TeamRanks AS (
                    SELECT 
                        *,
                        RANK() OVER (ORDER BY pts_scored DESC) as points_rank,
                        RANK() OVER (ORDER BY pts_allowed ASC) as points_allowed_rank,
                        RANK() OVER (ORDER BY avg_rebounds DESC) as rebounds_rank,
                        RANK() OVER (ORDER BY avg_assists DESC) as assists_rank,
                        RANK() OVER (ORDER BY avg_fg_pct DESC) as fg_pct_rank,
                        RANK() OVER (ORDER BY avg_fg3_pct DESC) as fg3_pct_rank
                    FROM TeamStats
                )
                SELECT * FROM TeamRanks
                WHERE team_id = %s
            """
            avg_stats = db.fetch_dataframe(query_avg_stats, (selected_season, team_id))

            query_record = """
                WITH TeamRecord AS (
                    SELECT 
                        t.team_id,
                        t.name as team_name,
                        COUNT(*) as total_games,
                        SUM(CASE 
                            WHEN (g.home_team_id = tb.team_id AND home_tb.pts > away_tb.pts) OR
                                 (g.away_team_id = tb.team_id AND away_tb.pts > home_tb.pts) THEN 1
                            ELSE 0
                        END) as wins
                    FROM team_boxscore tb
                    JOIN game g ON tb.game_id = g.game_id
                    JOIN team t ON tb.team_id = t.team_id
                    JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
                    JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
                    JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
                    JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
                    WHERE tb.season_year = %s
                    GROUP BY t.team_id, t.name
                ),
                RecordRanks AS (
                    SELECT 
                        *,
                        total_games - wins as losses,
                        ROUND(100.0 * wins / total_games, 1) as win_pct,
                        RANK() OVER (ORDER BY (1.0 * wins / total_games) DESC) as win_pct_rank
                    FROM TeamRecord
                )
                SELECT * FROM RecordRanks
                WHERE team_id = %s
            """
            record = db.fetch_dataframe(query_record, (selected_season, team_id))

            if not avg_stats.empty and not record.empty:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("#### Scoring")
                    st.markdown(
                        f"""
                        **Points Scored:** {avg_stats['pts_scored'].iloc[0]} ({avg_stats['points_rank'].iloc[0]}/30)  
                        **Points Allowed:** {avg_stats['pts_allowed'].iloc[0]} ({avg_stats['points_allowed_rank'].iloc[0]}/30)  
                        **Field Goal %:** {avg_stats['avg_fg_pct'].iloc[0]}% ({avg_stats['fg_pct_rank'].iloc[0]}/30)  
                        **3-Point %:** {avg_stats['avg_fg3_pct'].iloc[0]}% ({avg_stats['fg3_pct_rank'].iloc[0]}/30)
                    """
                    )

                with col2:
                    st.markdown("#### Other Stats")
                    st.markdown(
                        f"""
                        **Rebounds per Game:** {avg_stats['avg_rebounds'].iloc[0]} ({avg_stats['rebounds_rank'].iloc[0]}/30)  
                        **Assists per Game:** {avg_stats['avg_assists'].iloc[0]} ({avg_stats['assists_rank'].iloc[0]}/30)
                    """
                    )

                with col3:
                    st.markdown("#### Season Record")
                    wins = record["wins"].iloc[0]
                    losses = record["losses"].iloc[0]
                    win_pct = record["win_pct"].iloc[0]
                    win_pct_rank = record["win_pct_rank"].iloc[0]

                    st.markdown(
                        f"""
                        **Win-Loss Record:** {wins}-{losses} ({win_pct_rank}/30)  
                        **Win Percentage:** {win_pct}% ({win_pct_rank}/30)
                    """
                    )

            else:
                st.info("No statistics available for this team and season.")
        with tab_charts:
            query_scoring_trend = """
                SELECT 
                    g.date,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN home_tb.pts
                        ELSE away_tb.pts
                    END as points_scored,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN away_tb.pts
                        ELSE home_tb.pts
                    END as points_allowed,
                    CASE 
                        WHEN g.home_team_id = tb.team_id THEN 'Home'
                        ELSE 'Away'
                    END as location
                FROM team_boxscore tb
                JOIN game g ON tb.game_id = g.game_id
                JOIN team_boxscore htb ON g.game_id = htb.game_id AND g.home_team_id = htb.team_id
                JOIN team_boxscore atb ON g.game_id = atb.game_id AND g.away_team_id = atb.team_id
                JOIN team_boxscore_base home_tb ON htb.boxscore_id = home_tb.boxscore_id
                JOIN team_boxscore_base away_tb ON atb.boxscore_id = away_tb.boxscore_id
                WHERE tb.team_id = %s 
                AND tb.season_year = %s
                ORDER BY g.date
            """
            scoring_trend = db.fetch_dataframe(
                query_scoring_trend, (team_id, selected_season)
            )

            if not scoring_trend.empty:
                col1, col2 = st.columns(2)

                with col1:
                    scoring_trend["date"] = pd.to_datetime(scoring_trend["date"])

                    scoring_trend["month"] = scoring_trend["date"].dt.strftime("%Y-%m")
                    monthly_avg = scoring_trend.groupby("month").agg({
                        "points_scored": "mean",
                        "points_allowed": "mean"
                    }).round(1)
                    monthly_avg.index = pd.to_datetime(monthly_avg.index + "-01")

                    fig_scoring = go.Figure()

                    fig_scoring.add_trace(
                        go.Scatter(
                            x=scoring_trend["date"],
                            y=scoring_trend["points_scored"],
                            name="Points Scored",
                            line=dict(color="#00ff00", width=1),
                            opacity=0.5
                        )
                    )
                    fig_scoring.add_trace(
                        go.Scatter(
                            x=scoring_trend["date"],
                            y=scoring_trend["points_allowed"],
                            name="Points Allowed",
                            line=dict(color="#ff0000", width=1),
                            opacity=0.5
                        )
                    )

                    fig_scoring.add_trace(
                        go.Scatter(
                            x=monthly_avg.index,
                            y=monthly_avg["points_scored"],
                            name="Monthly Avg Scored",
                            line=dict(color="#00ff00", width=3),
                            mode='lines+markers'
                        )
                    )
                    fig_scoring.add_trace(
                        go.Scatter(
                            x=monthly_avg.index,
                            y=monthly_avg["points_allowed"],
                            name="Monthly Avg Allowed",
                            line=dict(color="#ff0000", width=3),
                            mode='lines+markers'
                        )
                    )

                    fig_scoring.update_layout(
                        title="Points Scored vs Allowed Trend (with Monthly Averages)",
                        xaxis_title="Date",
                        yaxis_title="Points",
                        hovermode="x unified"
                    )

                    st.plotly_chart(fig_scoring, use_container_width=True)

                with col2:
                    home_away_stats = (
                        scoring_trend.groupby("location")
                        .agg({"points_scored": "mean", "points_allowed": "mean"})
                        .round(1)
                    )

                    fig_home_away = px.bar(
                        home_away_stats,
                        barmode="group",
                        title="Home vs Away Scoring Comparison",
                        labels={
                            "value": "Points",
                            "variable": "Type",
                            "location": "Location",
                        },
                    )
                    st.plotly_chart(fig_home_away, use_container_width=True)

                scoring_trend["margin"] = (
                    scoring_trend["points_scored"] - scoring_trend["points_allowed"]
                )
                fig_margins = px.histogram(
                    scoring_trend,
                    x="margin",
                    title="Distribution of Win/Loss Margins",
                    labels={"margin": "Point Differential", "count": "Number of Games"},
                    color_discrete_sequence=["blue"],
                    nbins=int(
                        (scoring_trend["margin"].max() - scoring_trend["margin"].min())
                        / 4
                    ),
                )
                fig_margins.add_vline(x=0, line_dash="dash", line_color="red")
                st.plotly_chart(fig_margins, use_container_width=True)

                query_shooting_trend = """
                SELECT 
                    g.date,
                    ROUND(tbb.fg_pct * 100, 1) as fg_pct,
                    ROUND(tbb.fg3_pct * 100, 1) as fg3_pct
                FROM team_boxscore tb
                JOIN team_boxscore_base tbb ON tb.boxscore_id = tbb.boxscore_id
                JOIN game g ON tb.game_id = g.game_id
                WHERE tb.team_id = %s 
                AND tb.season_year = %s
                ORDER BY g.date
            """
            shooting_trend = db.fetch_dataframe(
                query_shooting_trend, (team_id, selected_season)
            )

            if not shooting_trend.empty:
                shooting_trend["date"] = pd.to_datetime(shooting_trend["date"])

                shooting_trend["fg_pct_ma"] = (
                    shooting_trend["fg_pct"].rolling(window=5, min_periods=1).mean()
                )
                shooting_trend["fg3_pct_ma"] = (
                    shooting_trend["fg3_pct"].rolling(window=5, min_periods=1).mean()
                )

                fig_shooting = go.Figure()

                fig_shooting.add_trace(
                    go.Scatter(
                        x=shooting_trend["date"],
                        y=shooting_trend["fg_pct"],
                        mode="markers",
                        name="FG%",
                        marker=dict(color="blue", size=6, opacity=0.3),
                        showlegend=False,
                    )
                )

                fig_shooting.add_trace(
                    go.Scatter(
                        x=shooting_trend["date"],
                        y=shooting_trend["fg3_pct"],
                        mode="markers",
                        name="3P%",
                        marker=dict(color="red", size=6, opacity=0.3),
                        showlegend=False,
                    )
                )

                fig_shooting.add_trace(
                    go.Scatter(
                        x=shooting_trend["date"],
                        y=shooting_trend["fg_pct_ma"],
                        mode="lines",
                        name="FG% (5-game avg)",
                        line=dict(color="blue", width=2),
                    )
                )

                fig_shooting.add_trace(
                    go.Scatter(
                        x=shooting_trend["date"],
                        y=shooting_trend["fg3_pct_ma"],
                        mode="lines",
                        name="3P% (5-game avg)",
                        line=dict(color="red", width=2),
                    )
                )

                fig_shooting.update_layout(
                    title="Shooting Efficiency Trend",
                    xaxis_title="Date",
                    yaxis_title="Percentage",
                    hovermode="x unified",
                    yaxis=dict(
                        ticksuffix="%",
                        range=[
                            0,
                            max(
                                shooting_trend["fg_pct"].max(),
                                shooting_trend["fg3_pct"].max(),
                            )
                            + 5,
                        ],
                    ),
                )

                st.plotly_chart(fig_shooting, use_container_width=True)

            else:
                st.info("No data available for charts.")
