import os
import pandas as pd
import streamlit as st
from app import ROOT_DIR
from db.DB import DB

from utils.utils import (
    fetch_seasons,
    fetch_games_by_season,
    go_to_previous_page,
    go_to_next_page,
)


st.title("NBA Games")

if "current_page" not in st.session_state:
    st.session_state["current_page"] = 1
if "matches_per_page" not in st.session_state:
    st.session_state["matches_per_page"] = 10

db = st.session_state["db_instance"]


def update_page():
    st.session_state["current_page"] = st.session_state["slider_page"]


seasons = fetch_seasons(db)
if isinstance(seasons, pd.DataFrame) and seasons.empty:
    st.warning("No seasons found.")
else:
    season_col = st.columns([2, 6, 2])
    with season_col[0]:
        selected_season = st.selectbox("Choose a season:", options=seasons)
    with season_col[2]:
        matches_per_page = st.selectbox(
            "Matches per page:",
            [5, 10, 20, 50],
            index=[5, 10, 20, 50].index(st.session_state["matches_per_page"]),
        )
        if matches_per_page != st.session_state["matches_per_page"]:
            st.session_state["matches_per_page"] = matches_per_page
            st.session_state["current_page"] = 1

    with st.container():
        filter_cols = st.columns([1, 1, 1, 1])
        
        with filter_cols[0]:
            teams_query = "SELECT DISTINCT name FROM team ORDER BY name"
            teams_df = db.fetch_dataframe(teams_query)
            teams = [None] + teams_df['name'].tolist()
            selected_team = st.selectbox("Team:", options=teams)
        
        with filter_cols[1]:
            min_date = st.date_input("From date:", value=None)
        
        with filter_cols[2]:
            max_date = st.date_input("To date:", value=None)

    if selected_season:
        query = """
        SELECT 
            g.game_id,
            g.date,
            ht.name as home_team_name,
            at.name as away_team_name,
            htb.pts as home_team_score,
            atb.pts as away_team_score
        FROM game g
        JOIN team ht ON g.home_team_id = ht.team_id
        JOIN team at ON g.away_team_id = at.team_id
        JOIN team_boxscore tb_home ON g.game_id = tb_home.game_id AND g.home_team_id = tb_home.team_id
        JOIN team_boxscore tb_away ON g.game_id = tb_away.game_id AND g.away_team_id = tb_away.team_id
        JOIN team_boxscore_base htb ON tb_home.boxscore_id = htb.boxscore_id
        JOIN team_boxscore_base atb ON tb_away.boxscore_id = atb.boxscore_id
        WHERE g.season_year = %(season)s
        """
        params = {"season": selected_season}
        
        if selected_team:
            query += " AND (ht.name = %(team)s OR at.name = %(team)s)"
            params["team"] = selected_team
        
        if min_date:
            query += " AND g.date >= %(min_date)s"
            params["min_date"] = min_date
        
        if max_date:
            query += " AND g.date <= %(max_date)s"
            params["max_date"] = max_date
        
        query += " ORDER BY g.date DESC"
        
        matches = db.fetch_dataframe(query, params=params)
        if matches.empty:
            st.info(f"No matches found for season {selected_season}.")
        else:
            total_matches = len(matches)
            matches_per_page = st.session_state["matches_per_page"]
            total_pages = max(1, (total_matches + matches_per_page - 1) // matches_per_page)

            st.divider()

            start_idx = (st.session_state["current_page"] - 1) * matches_per_page
            end_idx = min(start_idx + matches_per_page, total_matches)
            paginated_matches = matches.iloc[start_idx:end_idx]
            with st.container():
                st.markdown(
                    """
                    <div style="background-color: #f0f2f6; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1; font-weight: bold; color: #0e1117;">Date</div>
                            <div style="flex: 2; font-weight: bold; color: #0e1117;">Teams</div>
                            <div style="flex: 1; font-weight: bold; text-align: center; color: #0e1117;">Result</div>
                            <div style="flex: 1; font-weight: bold; text-align: center; color: #0e1117;">Details</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                for idx, match in paginated_matches.iterrows():
                    with st.container():
                        cols = st.columns([1, 2, 1, 1])

                        with cols[0]:
                            st.markdown(
                                f"""
                                <div style="background-color: {'#f8f9fa' if idx % 2 == 0 else '#ffffff'}; 
                                          padding: 10px; border-radius: 5px;">
                                    {match['date'].strftime('%Y-%m-%d')}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        with cols[1]:
                            st.markdown(
                                f"""
                                <div style="background-color: {'#f8f9fa' if idx % 2 == 0 else '#ffffff'}; 
                                          padding: 10px; border-radius: 5px;">
                                    {match['home_team_name']} vs {match['away_team_name']}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        with cols[2]:
                            st.markdown(
                                f"""
                                <div style="background-color: {'#f8f9fa' if idx % 2 == 0 else '#ffffff'}; 
                                          padding: 10px; border-radius: 5px; text-align: center;">
                                    {match['home_team_score']} - {match['away_team_score']}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        with cols[3]:
                            if st.button(
                                "View Details",
                                key=f"view_{match['game_id']}",
                                use_container_width=True,
                            ):
                                st.session_state["selected_game_id"] = match["game_id"]
                                st.switch_page(f"{ROOT_DIR}/app_pages/game.py")

            st.divider()
            pagination_cols = st.columns([1, 3, 1, 2])
            
            if total_pages > 1:
                with pagination_cols[0]:
                    if st.session_state["current_page"] > 1:
                        st.button(
                            "",
                            help="Previous Page",
                            icon=":material/arrow_back_ios:",
                            on_click=go_to_previous_page,
                        )
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
                    if st.session_state["current_page"] < total_pages:
                        st.button(
                            "",
                            help="Next Page",
                            icon=":material/arrow_forward_ios:",
                            on_click=go_to_next_page,
                        )
            
            with pagination_cols[3]:
                st.write(
                    f"Page {st.session_state['current_page']} / {total_pages} "
                    f"(Matches {start_idx + 1} to {end_idx} of {total_matches})"
                )
