import os
import pandas as pd
import streamlit as st
from db.DB import DB

from utils.pages_utils import *
from utils.utils import fetch_seasons, fetch_games_by_season, go_to_previous_page, go_to_next_page

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

    if selected_season:
        matches = fetch_games_by_season(db, selected_season)
        if matches.empty:
            st.info(f"No matches found for season {selected_season}.")
        else:
            total_matches = len(matches)
            matches_per_page = st.session_state["matches_per_page"]
            total_pages = (total_matches + matches_per_page - 1) // matches_per_page

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
                    unsafe_allow_html=True
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
                                unsafe_allow_html=True
                            )
                            
                        with cols[1]:
                            st.markdown(
                                f"""
                                <div style="background-color: {'#f8f9fa' if idx % 2 == 0 else '#ffffff'}; 
                                          padding: 10px; border-radius: 5px;">
                                    {match['home_team_name']} vs {match['away_team_name']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                        with cols[2]:
                            st.markdown(
                                f"""
                                <div style="background-color: {'#f8f9fa' if idx % 2 == 0 else '#ffffff'}; 
                                          padding: 10px; border-radius: 5px; text-align: center;">
                                    {match['home_team_score']} - {match['away_team_score']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                        with cols[3]:
                            st.button("View Details", key=f"view_{match['game_id']}", use_container_width=True,
                                      on_click=lambda game_id=match['game_id']: navigate_to_game_page(game_id))

               
            st.divider()
            pagination_cols = st.columns([1, 3, 1, 2])
            with pagination_cols[0]:
                if st.session_state["current_page"] > 1:
                    st.button("", help="Previous Page", icon=":material/arrow_back_ios:",
                              on_click=go_to_previous_page)
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
                    st.button("", help="Next Page", icon=":material/arrow_forward_ios:", on_click=go_to_next_page)
            with pagination_cols[3]:
                st.write(
                    f"Page {st.session_state['current_page']} / {total_pages} "
                    f"(Matches {start_idx + 1} to {end_idx} of {total_matches})"
                )
