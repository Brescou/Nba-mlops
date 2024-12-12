import pandas as pd
import streamlit as st
from db.DB import DB
from utils.utils import (
    analyze_timeouts,
    draw_court,
    fetch_game_details,
    fetch_play_by_play,
)
import matplotlib.pyplot as plt
import logging
import time
import plotly.express as px
import plotly.graph_objects as go
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

st.title("Game Details")

game_id = st.session_state.get("selected_game_id")

if not game_id:
    st.warning("No game selected. Please select a game from the games list.")

else:
    db = st.session_state["db_instance"]
    game_details = fetch_game_details(db, game_id)

    if game_details.empty:
        st.error("Game not found.")
    else:

        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h2 style="text-align: center; margin-bottom: 10px;">
                        {game_details['home_team_name'].iloc[0]} vs {game_details['away_team_name'].iloc[0]}
                    </h2>
                    <p style="text-align: center; font-size: 1.2em;">
                        {game_details['date'].iloc[0].strftime('%B %d, %Y')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        score_cols = st.columns([2, 1, 2])
        with score_cols[0]:
            st.markdown(
                f"""
                <div style="text-align: right; padding: 20px;">
                    <h3>{game_details['home_team_name'].iloc[0]}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with score_cols[1]:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 20px;">
                    <h2>{game_details['home_team_score'].iloc[0]} - {game_details['away_team_score'].iloc[0]}</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with score_cols[2]:
            st.markdown(
                f"""
                <div style="text-align: left; padding: 20px;">
                    <h3>{game_details['away_team_name'].iloc[0]}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

        tab1, tab2, tab3, tab4 = st.tabs(
            ["Game Summary", "Team Stats", "Player Stats", "Shot Chart"]
        )

        with tab1:
            summary_tabs = st.tabs(["Play by Play", "Analysis", "Timeouts"])

            with summary_tabs[0]:
                logger.debug("Rendering Game Summary tab")
                st.markdown("### Game Summary")

                play_by_play = fetch_play_by_play(db, game_id)

                with st.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        action_types = sorted(
                            play_by_play["action_type"].dropna().unique().tolist()
                        )
                        play_type_filters = st.multiselect(
                            "Filter by Play Type",
                            options=action_types,
                        )
                    with col2:
                        team_filters = st.multiselect(
                            "Filter by Team",
                            options=[
                                game_details["home_team_name"].iloc[0],
                                game_details["away_team_name"].iloc[0],
                            ],
                        )
                    with col3:
                        all_players = (
                            play_by_play[
                                play_by_play["player_name"].notna()
                                & (play_by_play["player_name"].str.strip() != "")
                            ]["player_name"]
                            .str.strip()
                            .unique()
                            .tolist()
                        )

                        all_players = sorted(
                            [p for p in all_players if p and not p.isspace()]
                        )

                        player_filters = st.multiselect(
                            f"Filter by Player (All Players: {len(all_players)})",
                            options=["All Players"] + all_players,
                            default=["All Players"],
                        )

                if not play_by_play.empty:
                    filtered_plays = play_by_play.copy()

                    if play_type_filters:
                        filtered_plays = filtered_plays[
                            filtered_plays["action_type"].isin(play_type_filters)
                        ]

                    if team_filters:
                        filtered_plays = filtered_plays[
                            filtered_plays["team_name"].isin(team_filters)
                        ]

                    if player_filters and "All Players" not in player_filters:
                        filtered_plays = filtered_plays[
                            filtered_plays["player_name"].isin(player_filters)
                        ]

                    if not filtered_plays.empty:
                        periods: list[int | str] = list(range(1, 5))
                        max_period = int(filtered_plays["period"].max())
                        if max_period > 4:
                            for ot in range(1, max_period - 3):
                                periods.append(f"OT{ot}")
                        period_labels = [
                            f"Quarter {p}" if isinstance(p, int) else p for p in periods
                        ]
                        period_tabs = st.tabs(period_labels)

                        for period, tab in zip(periods, period_tabs):
                            with tab:
                                period_plays = filtered_plays[
                                    filtered_plays["period"] == period
                                ].sort_values("clock", ascending=False)

                                st.markdown(
                                    """
                                    <div style="display: flex; align-items: center; padding: 10px; background-color: #e9ecef; font-weight: bold; border-radius: 5px; margin-bottom: 10px;">
                                        <div style="width: 80px; text-align: center;">Time</div>
                                        <div style="width: 120px; text-align: center;">Team</div>
                                        <div style="width: 120px; text-align: center;">Play Type</div>
                                        <div style="flex-grow: 1;">Play Description</div>
                                        <div style="width: 100px; text-align: center;">Score</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                                for i, (idx, play) in enumerate(
                                    period_plays.iterrows()
                                ):
                                    team_name = (
                                        play["team_name"]
                                        if pd.notna(play["team_name"])
                                        else ""
                                    )
                                    player_name = (
                                        play["player_name"]
                                        if pd.notna(play["player_name"])
                                        else ""
                                    )
                                    action_type = (
                                        str(play["action_type"]).title()
                                        if pd.notna(play["action_type"])
                                        else ""
                                    )
                                    score_home = (
                                        int(play["score_home"])
                                        if pd.notna(play["score_home"])
                                        else ""
                                    )
                                    score_away = (
                                        int(play["score_away"])
                                        if pd.notna(play["score_away"])
                                        else ""
                                    )

                                    st.markdown(
                                        f"""
                                        <div style="display: flex; align-items: center; padding: 5px; background-color: {'#f8f9fa' if i % 2 == 0 else '#ffffff'};">
                                            <div style="width: 80px; text-align: center;">{play['clock']}</div>
                                            <div style="width: 120px; text-align: center;">{team_name}</div>
                                            <div style="width: 120px; text-align: center;">{action_type}</div>
                                            <div style="flex-grow: 1;">{play['description']}</div>
                                            <div style="width: 100px; text-align: center;">{score_home}-{score_away}</div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )

            with summary_tabs[1]:
                analysis_cols = st.columns([1, 1])

                with analysis_cols[0]:
                    st.markdown("### Score Evolution")

                    score_data = play_by_play[
                        ["clock", "period", "score_home", "score_away"]
                    ].copy()
                    score_data["game_time"] = score_data.apply(
                        lambda x: f"Q{x['period']} {x['clock'].strftime('%H:%M')}",
                        axis=1,
                    )

                    score_data["score_diff"] = abs(
                        score_data["score_home"] - score_data["score_away"]
                    )

                    fig = px.line(
                        score_data,
                        x="game_time",
                        y=["score_home", "score_away"],
                        title=f"""{game_details['home_team_name'].iloc[0]} vs {
                            game_details['away_team_name'].iloc[0]} Score Evolution""",
                        labels={"value": "Score", "game_time": "Game Time"},
                        color_discrete_map={
                            "score_home": "#1f77b4",
                            "score_away": "#ff7f0e",
                        },
                        custom_data=[score_data["score_diff"]],
                    )

                    for trace in fig.data:
                        trace.update(
                            mode="lines",
                            line=dict(shape="linear", width=2),
                            connectgaps=True,
                            hovertemplate=(
                                "Score: %{y}<br>"
                                + "Diff: %{customdata:d}<br>"
                                + "<extra></extra>"
                            ),
                        )

                    fig.data[0].name = game_details["home_team_name"].iloc[0]
                    fig.data[1].name = game_details["away_team_name"].iloc[0]

                    quarter_ends = ["Q1 00:00", "Q2 00:00", "Q3 00:00"]
                    for quarter_end in quarter_ends:
                        if quarter_end in score_data["game_time"].values:
                            fig.add_vline(
                                x=quarter_end,
                                line_dash="solid",
                                line_color="gray",
                                opacity=0.3,
                            )

                    fig.update_layout(
                        hovermode="x unified",
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=False),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Arial",
                            align="left",
                        ),
                    )

                    st.plotly_chart(fig, use_container_width=True)

                with analysis_cols[1]:
                    st.markdown("### Team Stats Comparison")

                    default_stats = [
                        "Points",
                        "2 Points",
                        "3 Points",
                        "Assists",
                        "Rebounds",
                        "Turnovers",
                        "Fouls",
                        "Blocks",
                        "Steals",
                    ]

                    selected_stats = st.multiselect(
                        "Select Stats to Compare", default_stats, default=default_stats
                    )

                    home_team = game_details["home_team_name"].iloc[0]
                    away_team = game_details["away_team_name"].iloc[0]
                    home_team_id = int(game_details["home_team_id"].iloc[0])
                    away_team_id = int(game_details["away_team_id"].iloc[0])

                    home_plays = play_by_play[play_by_play["team_id"] == home_team_id]
                    away_plays = play_by_play[play_by_play["team_id"] == away_team_id]

                    max_period = play_by_play["period"].max()
                    has_ot = max_period > 4
                    ot_periods = (
                        [f"OT{i}" for i in range(1, max_period - 4 + 1)]
                        if has_ot
                        else []
                    )

                    period_choices = [
                        "Full Game",
                        "1st Half",
                        "2nd Half",
                        "Q1",
                        "Q2",
                        "Q3",
                        "Q4",
                    ] + ot_periods

                    period_choice = st.selectbox("Select Period", period_choices)

                    if period_choice == "Full Game":
                        filtered_plays = play_by_play  # Toutes les périodes
                    elif period_choice == "1st Half":
                        filtered_plays = play_by_play[
                            play_by_play["period"].isin([1, 2])
                        ]  # Périodes 1 et 2
                    elif period_choice == "2nd Half":
                        filtered_plays = play_by_play[
                            play_by_play["period"].isin([3, 4])
                        ]  # Périodes 3 et 4
                    elif period_choice.startswith("Q"):
                        quarter = int(period_choice[1])  # Q1->1, Q2->2, Q3->3, Q4->4
                        filtered_plays = play_by_play[play_by_play["period"] == quarter]
                    elif period_choice.startswith("OT"):
                        ot_number = int(period_choice[2])  # OT1->1, OT2->2, etc.
                        filtered_plays = play_by_play[
                            play_by_play["period"] == (4 + ot_number)
                        ]

                    period_scores = filtered_plays[
                        filtered_plays["action_type"] == "period"
                    ]

                    if period_choice == "Full Game":
                        start_scores = pd.DataFrame(
                            {"score_home": [0], "score_away": [0]}
                        )
                        end_scores = period_scores[
                            period_scores["period"] == max_period
                        ]
                    elif period_choice == "1st Half":
                        start_scores = pd.DataFrame(
                            {"score_home": [0], "score_away": [0]}
                        )
                        end_scores = period_scores[period_scores["period"] == 2]
                    elif period_choice == "2nd Half":
                        start_scores = play_by_play[
                            (play_by_play["action_type"] == "period")
                            & (play_by_play["period"] == 2)
                        ]
                        end_scores = period_scores[period_scores["period"] == 4]
                    elif period_choice.startswith("Q"):
                        quarter = int(period_choice[1])
                        start_scores = (
                            pd.DataFrame({"score_home": [0], "score_away": [0]})
                            if quarter == 1
                            else play_by_play[
                                (play_by_play["action_type"] == "period")
                                & (play_by_play["period"] == quarter - 1)
                            ]
                        )
                        end_scores = period_scores[period_scores["period"] == quarter]
                    elif period_choice.startswith("OT"):
                        ot_number = int(period_choice[2])
                        period = 4 + ot_number
                        start_scores = play_by_play[
                            (play_by_play["action_type"] == "period")
                            & (play_by_play["period"] == period - 1)
                        ]
                        end_scores = period_scores[period_scores["period"] == period]

                    team_stats = {
                        home_team: {
                            "Points": (
                                int(
                                    end_scores["score_home"].iloc[-1]
                                    - start_scores["score_home"].iloc[-1]
                                )
                                if not end_scores.empty and not start_scores.empty
                                else 0
                            ),
                            "2 Points": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == home_team_id)
                                    & (filtered_plays["action_type"] == "Made Shot")
                                    & (filtered_plays["shot_value"] == 2)
                                ]
                            ),
                            "3 Points": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == home_team_id)
                                    & (filtered_plays["action_type"] == "Made Shot")
                                    & (filtered_plays["shot_value"] == 3)
                                ]
                            ),
                            "Assists": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == home_team_id)
                                    & (filtered_plays["action_type"] == "Made Shot")
                                    & (
                                        filtered_plays["description"].str.contains(
                                            "AST"
                                        )
                                    )
                                ]
                            ),
                            "Rebounds": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == home_team_id)
                                    & (filtered_plays["action_type"] == "Rebound")
                                    & ~(
                                        filtered_plays["description"].str.contains(
                                            f"{team_name.upper()} Rebound", na=False
                                        )
                                    )
                                ]
                            ),
                            "Turnovers": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == home_team_id)
                                    & (filtered_plays["action_type"] == "Turnover")
                                ]
                            ),
                            "Fouls": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == home_team_id)
                                    & (filtered_plays["action_type"] == "Foul")
                                ]
                            ),
                            "Blocks": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == home_team_id)
                                    & (
                                        filtered_plays["description"].str.contains(
                                            "BLOCK", na=False
                                        )
                                    )
                                ]
                            ),
                            "Steals": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == home_team_id)
                                    & (
                                        filtered_plays["description"].str.contains(
                                            "STEAL", na=False
                                        )
                                    )
                                ]
                            ),
                        },
                        away_team: {
                            "Points": (
                                int(
                                    end_scores["score_away"].iloc[-1]
                                    - start_scores["score_away"].iloc[-1]
                                )
                                if not end_scores.empty and not start_scores.empty
                                else 0
                            ),
                            "2 Points": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == away_team_id)
                                    & (filtered_plays["action_type"] == "Made Shot")
                                    & (filtered_plays["shot_value"] == 2)
                                ]
                            ),
                            "3 Points": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == away_team_id)
                                    & (filtered_plays["action_type"] == "Made Shot")
                                    & (filtered_plays["shot_value"] == 3)
                                ]
                            ),
                            "Assists": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == away_team_id)
                                    & (filtered_plays["action_type"] == "Made Shot")
                                    & (
                                        filtered_plays["description"].str.contains(
                                            "AST", na=False
                                        )
                                    )
                                ]
                            ),
                            "Rebounds": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == away_team_id)
                                    & (filtered_plays["action_type"] == "Rebound")
                                    & ~(
                                        filtered_plays["description"].str.contains(
                                            f"{team_name.upper()} Rebound", na=False
                                        )
                                    )
                                ]
                            ),
                            "Turnovers": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == away_team_id)
                                    & (filtered_plays["action_type"] == "Turnover")
                                ]
                            ),
                            "Fouls": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == away_team_id)
                                    & (filtered_plays["action_type"] == "Foul")
                                ]
                            ),
                            "Blocks": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == away_team_id)
                                    & (
                                        filtered_plays["description"].str.contains(
                                            "BLOCK", na=False
                                        )
                                    )
                                ]
                            ),
                            "Steals": len(
                                filtered_plays[
                                    (filtered_plays["team_id"] == away_team_id)
                                    & (
                                        filtered_plays["description"].str.contains(
                                            "STEAL", na=False
                                        )
                                    )
                                ]
                            ),
                        },
                    }

                    fig = go.Figure()

                    fig.add_trace(
                        go.Bar(
                            name=home_team,
                            y=selected_stats,
                            x=[-team_stats[home_team][stat] for stat in selected_stats],
                            orientation="h",
                            marker_color="#1f77b4",
                            text=[
                                team_stats[home_team][stat] for stat in selected_stats
                            ],
                            textposition="outside",
                            textfont=dict(color="#1f77b4"),
                            hovertemplate=f"{home_team}: %{{x:.0f}}<extra></extra>",
                        )
                    )

                    fig.add_trace(
                        go.Bar(
                            name=away_team,
                            y=selected_stats,
                            x=[team_stats[away_team][stat] for stat in selected_stats],
                            orientation="h",
                            marker_color="#ff7f0e",
                            text=[
                                team_stats[away_team][stat] for stat in selected_stats
                            ],
                            textposition="outside",
                            textfont=dict(color="#ff7f0e"),
                            hovertemplate=f"{away_team}: %{{x:.0f}}<extra></extra>",
                        )
                    )

                    fig.update_layout(
                        barmode="relative",
                        title=dict(
                            text="Team Stats Comparison", x=0.5, xanchor="center"
                        ),
                        yaxis=dict(
                            title=None,
                            tickfont=dict(size=12),
                        ),
                        xaxis=dict(
                            title=None,
                            tickmode="linear",
                            tickformat="d",
                            zeroline=True,
                            zerolinewidth=2,
                            zerolinecolor="black",
                            showticklabels=False,
                        ),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                        ),
                        xaxis_range=[
                            -max(
                                [team_stats[home_team][stat] for stat in selected_stats]
                            )
                            * 1.2,
                            max(
                                [team_stats[away_team][stat] for stat in selected_stats]
                            )
                            * 1.2,
                        ],
                        plot_bgcolor="white",
                        bargap=0.3,
                    )

                    fig.add_vline(x=0, line_width=1, line_color="black")

                    st.plotly_chart(fig, use_container_width=True)
            with summary_tabs[2]:

                timeout_cols = st.columns([2, 1])

                with timeout_cols[0]:
                    timeout_data = analyze_timeouts(play_by_play)

                    if not timeout_data.empty:

                        st.markdown("#### Timeout Details")
                        formatted_timeout_data = timeout_data.copy()
                        formatted_timeout_data[
                            "effectiveness"
                        ] = formatted_timeout_data["impact"].apply(
                            lambda x: (
                                "✅ Positive"
                                if x > 0
                                else "❌ Negative" if x < 0 else "➖ Neutral"
                            )
                        )

                        st.dataframe(
                            formatted_timeout_data[
                                [
                                    "period",
                                    "time",
                                    "team",
                                    "points_before_team",
                                    "points_before_opp",
                                    "points_after_team",
                                    "points_after_opp",
                                    "effectiveness",
                                ]
                            ].rename(
                                columns={
                                    "period": "Period",
                                    "time": "Time",
                                    "team": "Team",
                                    "points_before_team": "Points Before (Team)",
                                    "points_before_opp": "Points Before (Opp)",
                                    "points_after_team": "Points After (Team)",
                                    "points_after_opp": "Points After (Opp)",
                                }
                            ),
                            use_container_width=True,
                        )

                with timeout_cols[1]:
                    # Global timeout statistics
                    st.markdown("#### Timeout Statistics")

                    total_timeouts = len(timeout_data)

                    st.metric("Total Timeouts", total_timeouts)

        with tab2:
            logger.debug("Rendering Team Stats tab")
            st.markdown("### Team Statistics")

            home_team_id = int(game_details["home_team_id"].iloc[0])
            away_team_id = int(game_details["away_team_id"].iloc[0])

            stat_tabs = st.tabs(
                [
                    "Base Stats",
                    "Advanced Stats",
                    "Four Factors",
                    "Misc Stats",
                    "Scoring Stats",
                ]
            )

            with stat_tabs[0]:
                query = """
                    SELECT 
                        t.name as team_name,
                        tb.*
                    FROM team_boxscore_base tb
                    JOIN team_boxscore tbs ON tb.boxscore_id = tbs.boxscore_id
                    JOIN team t ON tbs.team_id = t.team_id
                    WHERE tbs.game_id = %s AND tbs.team_id IN (%s, %s)
                """
                base_stats = db.fetch_dataframe(
                    query, (game_id, home_team_id, away_team_id)
                )
                if not base_stats.empty:
                    base_stats = base_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "team_name": "Team",
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

                    base_stats = base_stats.rename(columns=column_renames)

                    all_columns = [col for col in base_stats.columns if col != "Team"]
                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=all_columns,
                    )

                    if "Team" in base_stats.columns:
                        st.dataframe(
                            base_stats[["Team"] + selected_columns].set_index("Team"),
                            use_container_width=True,
                        )
                    else:
                        st.error("Team column not found in the data.")

            with stat_tabs[1]:
                query = """
                    SELECT 
                        t.name as team_name,
                        tba.off_rating,
                        tba.def_rating,
                        tba.net_rating,
                        tba.ast_pct,
                        tba.ast_to,
                        tba.ast_ratio,
                        tba.oreb_pct,
                        tba.dreb_pct,
                        tba.reb_pct,
                        tba.tm_tov_pct,
                        tba.efg_pct,
                        tba.ts_pct,
                        tba.pace,
                        tba.pie
                    FROM team_boxscore_advanced tba
                    JOIN team_boxscore tbs ON tba.boxscore_id = tbs.boxscore_id
                    JOIN team t ON tbs.team_id = t.team_id
                    WHERE tbs.game_id = %s AND tbs.team_id IN (%s, %s)
                """

                advanced_stats = db.fetch_dataframe(
                    query, (game_id, home_team_id, away_team_id)
                )

                if advanced_stats.empty:
                    st.info("No advanced statistics available for this game.")
                    logging.warning(
                        f"No team advanced stats found for game_id: {game_id}"
                    )
                else:
                    if "boxscore_id" in advanced_stats.columns:
                        advanced_stats = advanced_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "team_name": "Team",
                        "off_rating": "Offensive Rating",
                        "def_rating": "Defensive Rating",
                        "net_rating": "Net Rating",
                        "ast_pct": "Assist %",
                        "ast_to": "Assist/Turnover Ratio",
                        "ast_ratio": "Assist Ratio",
                        "oreb_pct": "Offensive Rebound %",
                        "dreb_pct": "Defensive Rebound %",
                        "reb_pct": "Total Rebound %",
                        "tm_tov_pct": "Turnover %",
                        "efg_pct": "Effective FG %",
                        "ts_pct": "True Shooting %",
                        "pace": "Pace",
                        "pie": "Player Impact Estimate",
                    }

                    advanced_stats = advanced_stats.rename(columns=column_renames)

                    all_columns = [
                        col for col in advanced_stats.columns if col != "Team"
                    ]
                    default_columns = [
                        "Offensive Rating",
                        "Defensive Rating",
                        "Net Rating",
                        "Pace",
                    ]
                    default_columns = [
                        col for col in default_columns if col in all_columns
                    ]

                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=default_columns,
                        key=f"team_advanced_stats_columns_tab2_{game_id}",
                    )

                    if "Team" in advanced_stats.columns:
                        st.dataframe(
                            advanced_stats[["Team"] + selected_columns].set_index(
                                "Team"
                            ),
                            use_container_width=True,
                        )
                    else:
                        st.error("Team column not found in the data.")

            with stat_tabs[2]:
                query = """
                    SELECT 
                        t.name as team_name,
                        tf.*
                    FROM team_boxscore_four_factors tf
                    JOIN team_boxscore tbs ON tf.boxscore_id = tbs.boxscore_id
                    JOIN team t ON tbs.team_id = t.team_id
                    WHERE tbs.game_id = %s AND tbs.team_id IN (%s, %s)
                """
                four_factors = db.fetch_dataframe(
                    query, (game_id, home_team_id, away_team_id)
                )
                if not four_factors.empty:
                    four_factors = four_factors.drop("boxscore_id", axis=1)

                    column_renames = {
                        "team_name": "Team",
                        "efg_pct": "Effective FG %",
                        "fta_rate": "Free Throw Attempt Rate",
                        "tm_tov_pct": "Turnover %",
                        "oreb_pct": "Offensive Rebound %",
                        "opp_efg_pct": "Opponent Effective FG %",
                        "opp_fta_rate": "Opponent Free Throw Attempt Rate",
                        "opp_tov_pct": "Opponent Turnover %",
                        "opp_oreb_pct": "Opponent Offensive Rebound %",
                    }

                    four_factors = four_factors.rename(columns=column_renames)

                    all_columns = [col for col in four_factors.columns if col != "Team"]
                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=all_columns,
                    )

                    if "Team" in four_factors.columns:
                        st.dataframe(
                            four_factors[["Team"] + selected_columns].set_index("Team"),
                            use_container_width=True,
                        )
                    else:
                        st.error("Team column not found in the data.")

                with st.expander("Explanation of Four Factors"):
                    st.markdown(
                        """
                    - **Effective FG % (eFG%):** Adjusts FG% to account for 3-point field goals being worth more.
                    - **Free Throw Attempt Rate (FTA Rate):** Ratio of free throw attempts to field goal attempts.
                    - **Turnover % (TOV%):** Turnovers per 100 plays.
                    - **Offensive Rebound % (OREB%):** Percentage of available offensive rebounds a player grabbed.
                    - **Opponent Effective FG % (Opp eFG%):** Opponent's effective field goal percentage.
                    - **Opponent Free Throw Attempt Rate (Opp FTA Rate):** Opponent's ratio of free throw attempts to field goal attempts.
                    - **Opponent Turnover % (Opp TOV%):** Opponent's turnovers per 100 plays.
                    - **Opponent Offensive Rebound % (Opp OREB%):** Opponent's percentage of available offensive rebounds grabbed.
                    """
                    )

            with stat_tabs[3]:
                query = """
                    SELECT 
                        t.name as team_name,
                        tm.*
                    FROM team_boxscore_misc tm
                    JOIN team_boxscore tbs ON tm.boxscore_id = tbs.boxscore_id
                    JOIN team t ON tbs.team_id = t.team_id
                    WHERE tbs.game_id = %s AND tbs.team_id IN (%s, %s)
                """
                misc_stats = db.fetch_dataframe(
                    query, (game_id, home_team_id, away_team_id)
                )
                if not misc_stats.empty:
                    misc_stats = misc_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "team_name": "Team",
                        "pts_off_tov": "Points Off Turnovers",
                        "pts_2nd_chance": "Second Chance Points",
                        "pts_fb": "Fast Break Points",
                        "pts_paint": "Points in the Paint",
                        "opp_pts_off_tov": "Opponent Points Off Turnovers",
                        "opp_pts_2nd_chance": "Opponent Second Chance Points",
                        "opp_pts_fb": "Opponent Fast Break Points",
                        "opp_pts_paint": "Opponent Points in the Paint",
                    }

                    misc_stats = misc_stats.rename(columns=column_renames)

                    all_columns = [col for col in misc_stats.columns if col != "Team"]
                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=all_columns,
                    )

                    if "Team" in misc_stats.columns:
                        st.dataframe(
                            misc_stats[["Team"] + selected_columns].set_index("Team"),
                            use_container_width=True,
                        )
                    else:
                        st.error("Team column not found in the data.")

                with st.expander("Explanation of Misc Stats"):
                    st.markdown(
                        """
                    - **Points Off Turnovers (PTS Off TOV):** Points scored off opponent turnovers.
                    - **Second Chance Points (PTS 2nd Chance):** Points scored on a second chance after an offensive rebound.
                    - **Fast Break Points (PTS FB):** Points scored on fast breaks.
                    - **Points in the Paint (PTS Paint):** Points scored in the paint area.
                    - **Opponent Points Off Turnovers (Opp PTS Off TOV):** Points opponent scored off turnovers.
                    - **Opponent Second Chance Points (Opp PTS 2nd Chance):** Points opponent scored on a second chance after an offensive rebound.
                    - **Opponent Fast Break Points (Opp PTS FB):** Points opponent scored on fast breaks.
                    - **Opponent Points in the Paint (Opp PTS Paint):** Points opponent scored in the paint area.
                    """
                    )

            with stat_tabs[4]:
                query = """
                    SELECT 
                        t.name as team_name,
                        ts.*
                    FROM team_boxscore_scoring ts
                    JOIN team_boxscore tbs ON ts.boxscore_id = tbs.boxscore_id
                    JOIN team t ON tbs.team_id = t.team_id
                    WHERE tbs.game_id = %s AND tbs.team_id IN (%s, %s)
                """
                scoring_stats = db.fetch_dataframe(
                    query, (game_id, home_team_id, away_team_id)
                )
                if not scoring_stats.empty:
                    scoring_stats = scoring_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "team_name": "Team",
                        "pct_fga_2pt": "% FGA 2PT",
                        "pct_fga_3pt": "% FGA 3PT",
                        "pct_pts_2pt": "% Points 2PT",
                        "pct_pts_2pt_mr": "% Points 2PT Mid-Range",
                        "pct_pts_3pt": "% Points 3PT",
                        "pct_pts_fb": "% Points Fast Break",
                        "pct_pts_ft": "% Points Free Throw",
                        "pct_pts_off_tov": "% Points Off Turnovers",
                        "pct_pts_paint": "% Points in the Paint",
                        "pct_ast_2pm": "% Assisted 2PM",
                        "pct_uast_2pm": "% Unassisted 2PM",
                        "pct_ast_3pm": "% Assisted 3PM",
                        "pct_uast_3pm": "% Unassisted 3PM",
                        "pct_ast_fgm": "% Assisted FGM",
                        "pct_uast_fgm": "% Unassisted FGM",
                    }

                    scoring_stats = scoring_stats.rename(columns=column_renames)

                    all_columns = [
                        col for col in scoring_stats.columns if col != "Team"
                    ]
                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=all_columns,
                    )

                    if "Team" in scoring_stats.columns:
                        st.dataframe(
                            scoring_stats[["Team"] + selected_columns].set_index(
                                "Team"
                            ),
                            use_container_width=True,
                        )
                    else:
                        st.error("Team column not found in the data.")

                with st.expander("Explanation of Scoring Stats"):
                    st.markdown(
                        """
                    - **% FGA 2PT:** Percentage of field goal attempts that are 2-pointers.
                    - **% FGA 3PT:** Percentage of field goal attempts that are 3-pointers.
                    - **% Points 2PT:** Percentage of total points scored from 2-pointers.
                    - **% Points 2PT Mid-Range:** Percentage of total points scored from mid-range 2-pointers.
                    - **% Points 3PT:** Percentage of total points scored from 3-pointers.
                    - **% Points Fast Break:** Percentage of total points scored on fast breaks.
                    - **% Points Free Throw:** Percentage of total points scored from free throws.
                    - **% Points Off Turnovers:** Percentage of total points scored off turnovers.
                    - **% Points in the Paint:** Percentage of total points scored in the paint.
                    - **% Assisted 2PM:** Percentage of 2-point field goals made that were assisted.
                    - **% Unassisted 2PM:** Percentage of 2-point field goals made that were unassisted.
                    - **% Assisted 3PM:** Percentage of 3-point field goals made that were assisted.
                    - **% Unassisted 3PM:** Percentage of 3-point field goals made that were unassisted.
                    - **% Assisted FGM:** Percentage of field goals made that were assisted.
                    - **% Unassisted FGM:** Percentage of field goals made that were unassisted.
                    """
                    )

        with tab3:
            st.markdown("### Player Statistics")
            stat_tabs = st.tabs(
                [
                    "Base Stats",
                    "Advanced Stats",
                    "Misc Stats",
                    "Scoring Stats",
                    "Usage Stats",
                ]
            )

            with stat_tabs[0]:
                query = """
                    SELECT 
                        CONCAT(p.firstname, ' ', p.lastname) as player_name,
                        t.name as team_name,
                        pbs.*
                    FROM player_boxscore_base pbs
                    JOIN player_boxscore pb ON pbs.boxscore_id = pb.boxscore_id
                    JOIN team t ON pb.team_id = t.team_id
                    LEFT JOIN player p ON p.player_id = CAST(SPLIT_PART(pb.boxscore_id, '-', 1) AS INTEGER)
                    WHERE pb.game_id = %s
                    ORDER BY t.name, player_name
                """
                base_stats = db.fetch_dataframe(query, (game_id,))

                if base_stats.empty:
                    st.info("No base statistics available for this game.")
                    logging.warning(f"No base stats found for game_id: {game_id}")
                else:
                    base_stats = base_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "player_name": "Player",
                        "team_name": "Team",
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
                        "min_sec": "Minutes",
                    }

                    base_stats = base_stats.rename(columns=column_renames)

                    all_columns = [
                        col
                        for col in base_stats.columns
                        if col not in ["Player", "Team"]
                    ]
                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=["Minutes", "Points", "Total Rebounds", "Assists"],
                    )

                    st.dataframe(
                        base_stats[["Player", "Team"] + selected_columns].set_index(
                            ["Team", "Player"]
                        ),
                        use_container_width=True,
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

            with stat_tabs[1]:
                query = """
                    SELECT 
                        CONCAT(p.firstname, ' ', p.lastname) as player_name,
                        t.name as team_name,
                        pba.*
                    FROM player_boxscore_advanced pba
                    JOIN player_boxscore pb ON pba.boxscore_id = pb.boxscore_id
                    JOIN team t ON pb.team_id = t.team_id
                    LEFT JOIN player p ON p.player_id = CAST(SPLIT_PART(pb.boxscore_id, '-', 1) AS INTEGER)
                    WHERE pb.game_id = %s
                    ORDER BY t.name, player_name
                """
                advanced_stats = db.fetch_dataframe(query, (game_id,))

                if advanced_stats.empty:
                    st.info("No advanced statistics available for this game.")
                    logging.warning(f"No advanced stats found for game_id: {game_id}")
                else:
                    if "boxscore_id" in advanced_stats.columns:
                        advanced_stats = advanced_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "player_name": "Player",
                        "team_name": "Team",
                        "off_rating": "Offensive Rating",
                        "def_rating": "Defensive Rating",
                        "net_rating": "Net Rating",
                        "ast_pct": "Assist %",
                        "ast_to": "Assist/Turnover Ratio",
                        "ast_ratio": "Assist Ratio",
                        "oreb_pct": "Offensive Rebound %",
                        "dreb_pct": "Defensive Rebound %",
                        "reb_pct": "Total Rebound %",
                        "tm_tov_pct": "Turnover %",
                        "efg_pct": "Effective FG %",
                        "ts_pct": "True Shooting %",
                        "usg_pct": "Usage %",
                        "pace": "Pace",
                        "pie": "Player Impact Estimate",
                    }

                    advanced_stats = advanced_stats.rename(columns=column_renames)

                    all_columns = [
                        col
                        for col in advanced_stats.columns
                        if col not in ["Player", "Team"]
                    ]
                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=[
                            "Offensive Rating",
                            "Defensive Rating",
                            "Net Rating",
                            "Usage %",
                        ],
                    )

                    st.dataframe(
                        advanced_stats[["Player", "Team"] + selected_columns].set_index(
                            ["Team", "Player"]
                        ),
                        use_container_width=True,
                    )

                    with st.expander("Explanation of Advanced Stats"):
                        st.markdown(
                            """
                        - **Offensive Rating:** Points produced per 100 possessions
                        - **Defensive Rating:** Points allowed per 100 possessions
                        - **Net Rating:** Difference between offensive and defensive rating
                        - **Assist % (AST%):** Percentage of teammate field goals a player assisted
                        - **Assist/Turnover Ratio (AST/TO):** Ratio of assists to turnovers
                        - **Assist Ratio:** Percentage of possessions ending with an assist
                        - **Offensive/Defensive/Total Rebound % (OREB%/DREB%/REB%):** Percentage of available rebounds obtained
                        - **Turnover % (TOV%):** Turnovers per 100 plays
                        - **Effective FG % (eFG%):** Field goal percentage adjusted for three-pointers
                        - **True Shooting % (TS%):** Shooting percentage adjusted for three-pointers and free throws
                        - **Usage % (USG%):** Percentage of team plays used by player
                        - **Pace:** Number of possessions per 48 minutes
                        - **Player Impact Estimate (PIE):** Measure of player's overall statistical contribution
                        """
                        )

            with stat_tabs[2]:
                query = """
                    SELECT 
                        CONCAT(p.firstname, ' ', p.lastname) as player_name,
                        t.name as team_name,
                        pbm.*
                    FROM player_boxscore_misc pbm
                    JOIN player_boxscore pb ON pbm.boxscore_id = pb.boxscore_id
                    JOIN team t ON pb.team_id = t.team_id
                    LEFT JOIN player p ON p.player_id = CAST(SPLIT_PART(pb.boxscore_id, '-', 1) AS INTEGER)
                    WHERE pb.game_id = %s
                    ORDER BY t.name, player_name
                """
                misc_stats = db.fetch_dataframe(query, (game_id,))
                if not misc_stats.empty:
                    misc_stats = misc_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "player_name": "Player",
                        "team_name": "Team",
                        "pts_off_tov": "Points Off Turnovers",
                        "pts_2nd_chance": "Second Chance Points",
                        "pts_fb": "Fast Break Points",
                        "pts_paint": "Points in the Paint",
                        "opp_pts_off_tov": "Opponent Points Off Turnovers",
                        "opp_pts_2nd_chance": "Opponent Second Chance Points",
                        "opp_pts_fb": "Opponent Fast Break Points",
                        "opp_pts_paint": "Opponent Points in the Paint",
                        "min_sec": "Minutes",
                    }

                    misc_stats = misc_stats.rename(columns=column_renames)

                    all_columns = [
                        col
                        for col in misc_stats.columns
                        if col not in ["Player", "Team"]
                    ]
                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=[
                            "Points Off Turnovers",
                            "Fast Break Points",
                            "Points in the Paint",
                        ],
                    )

                    st.dataframe(
                        misc_stats[["Player", "Team"] + selected_columns].set_index(
                            ["Team", "Player"]
                        ),
                        use_container_width=True,
                    )

                    with st.expander("Explanation of Misc Stats"):
                        st.markdown(
                            """
                        - **Points Off Turnovers:** Points scored following opponent turnovers
                        - **Second Chance Points:** Points scored after offensive rebounds
                        - **Fast Break Points:** Points scored on fast break opportunities
                        - **Points in the Paint:** Points scored in the painted area
                        - **Opponent Points Off Turnovers:** Points allowed following team turnovers
                        - **Opponent Second Chance Points:** Points allowed after opponent offensive rebounds
                        - **Opponent Fast Break Points:** Points allowed on opponent fast breaks
                        - **Opponent Points in the Paint:** Points allowed in the painted area
                        """
                        )

            with stat_tabs[3]:
                query = """
                    SELECT 
                        CONCAT(p.firstname, ' ', p.lastname) as player_name,
                        t.name as team_name,
                        pbs.*
                    FROM player_boxscore_scoring pbs
                    JOIN player_boxscore pb ON pbs.boxscore_id = pb.boxscore_id
                    JOIN team t ON pb.team_id = t.team_id
                    LEFT JOIN player p ON p.player_id = CAST(SPLIT_PART(pb.boxscore_id, '-', 1) AS INTEGER)
                    WHERE pb.game_id = %s
                    ORDER BY t.name, player_name
                """
                scoring_stats = db.fetch_dataframe(query, (game_id,))
                if not scoring_stats.empty:
                    scoring_stats = scoring_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "player_name": "Player",
                        "team_name": "Team",
                        "pct_fga_2pt": "% FGA 2PT",
                        "pct_fga_3pt": "% FGA 3PT",
                        "pct_pts_2pt": "% Points 2PT",
                        "pct_pts_2pt_mr": "% Points 2PT Mid-Range",
                        "pct_pts_3pt": "% Points 3PT",
                        "pct_pts_fb": "% Points Fast Break",
                        "pct_pts_ft": "% Points Free Throw",
                        "pct_pts_off_tov": "% Points Off Turnovers",
                        "pct_pts_paint": "% Points in the Paint",
                        "pct_ast_2pm": "% Assisted 2PM",
                        "pct_uast_2pm": "% Unassisted 2PM",
                        "pct_ast_3pm": "% Assisted 3PM",
                        "pct_uast_3pm": "% Unassisted 3PM",
                        "pct_ast_fgm": "% Assisted FGM",
                        "pct_uast_fgm": "% Unassisted FGM",
                        "min_sec": "Minutes",
                    }

                    scoring_stats = scoring_stats.rename(columns=column_renames)

                    all_columns = [
                        col
                        for col in scoring_stats.columns
                        if col not in ["Player", "Team"]
                    ]
                    default_columns = [
                        "% Points 2PT",
                        "% Points 3PT",
                        "% Points in the Paint",
                    ]
                    default_columns = [
                        col for col in default_columns if col in all_columns
                    ]

                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=default_columns,
                    )

                    st.dataframe(
                        scoring_stats[["Player", "Team"] + selected_columns].set_index(
                            ["Team", "Player"]
                        ),
                        use_container_width=True,
                    )

                    with st.expander("Explanation of Scoring Stats"):
                        st.markdown(
                            """
                        - **% FGA 2PT/3PT:** Percentage of field goal attempts from 2-point/3-point range
                        - **% Points 2PT:** Percentage of points scored on 2-point shots
                        - **% Points 2PT Mid-Range:** Percentage of points from mid-range shots
                        - **% Points 3PT:** Percentage of points scored on 3-point shots
                        - **% Points Fast Break:** Percentage of points scored in transition
                        - **% Points Free Throw:** Percentage of points scored from free throws
                        - **% Points Off Turnovers:** Percentage of points scored after turnovers
                        - **% Points in the Paint:** Percentage of points scored in the painted area
                        - **% Assisted/Unassisted 2PM:** Percentage of made 2-pointers that were assisted/unassisted
                        - **% Assisted/Unassisted 3PM:** Percentage of made 3-pointers that were assisted/unassisted
                        - **% Assisted/Unassisted FGM:** Percentage of all field goals that were assisted/unassisted
                        """
                        )

            with stat_tabs[4]:
                query = """
                    SELECT 
                        CONCAT(p.firstname, ' ', p.lastname) as player_name,
                        t.name as team_name,
                        pbu.*
                    FROM player_boxscore_usage pbu
                    JOIN player_boxscore pb ON pbu.boxscore_id = pb.boxscore_id
                    JOIN team t ON pb.team_id = t.team_id
                    LEFT JOIN player p ON p.player_id = CAST(SPLIT_PART(pb.boxscore_id, '-', 1) AS INTEGER)
                    WHERE pb.game_id = %s
                    ORDER BY t.name, player_name
                """
                usage_stats = db.fetch_dataframe(query, (game_id,))
                if not usage_stats.empty:
                    usage_stats = usage_stats.drop("boxscore_id", axis=1)

                    column_renames = {
                        "player_name": "Player",
                        "team_name": "Team",
                        "usg_pct": "Usage %",
                        "pct_fgm": "% of Team FGM",
                        "pct_fga": "% of Team FGA",
                        "pct_fg3m": "% of Team 3PM",
                        "pct_fg3a": "% of Team 3PA",
                        "pct_ftm": "% of Team FTM",
                        "pct_fta": "% of Team FTA",
                        "pct_oreb": "% of Team OREB",
                        "pct_dreb": "% of Team DREB",
                        "pct_reb": "% of Team REB",
                        "pct_ast": "% of Team AST",
                        "pct_tov": "% of Team TOV",
                        "pct_stl": "% of Team STL",
                        "pct_blk": "% of Team BLK",
                        "pct_blka": "% of Team BLKA",
                        "pct_pf": "% of Team PF",
                        "pct_pfd": "% of Team PFD",
                        "pct_pts": "% of Team PTS",
                        "min_sec": "Minutes",
                    }

                    usage_stats = usage_stats.rename(columns=column_renames)

                    all_columns = [
                        col
                        for col in usage_stats.columns
                        if col not in ["Player", "Team"]
                    ]
                    default_columns = [
                        "Usage %",
                        "% of Team Points",
                        "% of Team Rebounds",
                        "% of Team Assists",
                    ]
                    default_columns = [
                        col for col in default_columns if col in all_columns
                    ]

                    selected_columns = st.multiselect(
                        "Select columns to display",
                        options=all_columns,
                        default=default_columns,
                    )

                    st.dataframe(
                        usage_stats[["Player", "Team"] + selected_columns].set_index(
                            ["Team", "Player"]
                        ),
                        use_container_width=True,
                    )

                    with st.expander("Explanation of Usage Stats"):
                        st.markdown(
                            """
                        - **Usage % (USG%):** Percentage of team plays used by player while on court
                        - **% FGM/FGA:** Percentage of team's made/attempted field goals
                        - **% 3PM/3PA:** Percentage of team's made/attempted three-pointers
                        - **% FTM/FTA:** Percentage of team's made/attempted free throws
                        - **% OREB/DREB/REB:** Percentage of team's offensive/defensive/total rebounds
                        - **% AST:** Percentage of team's assists
                        - **% TOV:** Percentage of team's turnovers
                        - **% STL:** Percentage of team's steals
                        - **% BLK:** Percentage of team's blocks
                        - **% BLKA:** Percentage of team's blocked attempts
                        - **% PF/PFD:** Percentage of team's fouls committed/drawn
                        - **% PTS:** Percentage of team's total points
                        """
                        )

        with tab4:
            st.markdown("### Shot Chart")

            shot_chart_col1, shot_chart_col2, shot_chart_col3 = st.columns([1, 1, 2])

            with shot_chart_col1:
                selected_team = st.radio(
                    "Select Team",
                    [
                        game_details["home_team_name"].iloc[0],
                        game_details["away_team_name"].iloc[0],
                    ],
                )

                team_id = (
                    int(game_details["home_team_id"].iloc[0])
                    if selected_team == game_details["home_team_name"].iloc[0]
                    else int(game_details["away_team_id"].iloc[0])
                )

                player_query = """
                    SELECT DISTINCT p.player_id, p.firstname, p.lastname
                    FROM play_by_play pb
                    JOIN player p ON pb.player_id = p.player_id
                    WHERE pb.game_id = %s 
                    AND pb.team_id = %s
                    AND pb.action_type IN ('Made Shot', 'Missed Shot')
                    ORDER BY p.lastname, p.firstname
                """
                players = db.fetch_dataframe(player_query, (game_id, team_id))

                if not players.empty:
                    players["full_name"] = (
                        players["firstname"] + " " + players["lastname"]
                    )
                    selected_player = st.selectbox(
                        "Filter by Player",
                        options=["All Players"] + players["full_name"].tolist(),
                    )

                periods: list[int | str] = list(range(1, 5))
                max_period = int(filtered_plays["period"].max())
                if max_period > 4:
                    for ot in range(1, max_period - 3):
                        periods.append(f"OT{ot}")
                period_labels = [
                    f"Quarter {p}" if isinstance(p, int) else p for p in periods
                ]
                selected_periods = st.multiselect(
                    "Filter by Period",
                    options=periods,
                    default=periods,
                )

            with shot_chart_col2:
                shot_types = st.multiselect(
                    "Filter by Shot Type",
                    options=["2PT", "3PT"],
                    default=["2PT", "3PT"],
                )

            with shot_chart_col3:
                fig, ax = plt.subplots(figsize=(12, 11))
                draw_court(ax, outer_lines=True)

                query = """
                    SELECT 
                        x_legacy, 
                        y_legacy,
                        shot_distance,
                        action_type = 'Made Shot' as made_flag,
                        shot_value,
                        period,
                        player_id
                    FROM play_by_play
                    WHERE game_id = %s 
                    AND team_id = %s 
                    AND action_type IN ('Made Shot', 'Missed Shot')
                    AND x_legacy != 0 
                    AND y_legacy != 0
                """
                shots = db.fetch_dataframe(query, (game_id, team_id))

                if shots.empty:
                    st.info("No shots found for this team in this game.")
                else:
                    filtered_shots = shots.copy()

                    if selected_player != "All Players":
                        selected_player_id = players[
                            players["full_name"] == selected_player
                        ]["player_id"].iloc[0]
                        filtered_shots = filtered_shots[
                            filtered_shots["player_id"] == selected_player_id
                        ]

                    if selected_periods != periods:
                        period_filter = [
                            p if isinstance(p, int) else 5 for p in selected_periods
                        ]
                        filtered_shots = filtered_shots[
                            filtered_shots["period"].isin(period_filter)
                        ]

                    if shot_types:
                        if "2PT" in shot_types and "3PT" not in shot_types:
                            filtered_shots = filtered_shots[
                                filtered_shots["shot_value"] == 2
                            ]
                        elif "3PT" in shot_types and "2PT" not in shot_types:
                            filtered_shots = filtered_shots[
                                filtered_shots["shot_value"] == 3
                            ]

                    made_shots = filtered_shots[filtered_shots["made_flag"]]
                    ax.scatter(
                        made_shots["x_legacy"],
                        made_shots["y_legacy"],
                        c="green",
                        alpha=0.6,
                        s=50,
                        label="Made Shots",
                    )

                    missed_shots = filtered_shots[~filtered_shots["made_flag"]]
                    ax.scatter(
                        missed_shots["x_legacy"],
                        missed_shots["y_legacy"],
                        c="red",
                        alpha=0.6,
                        s=50,
                        label="Missed Shots",
                    )

                    shot_success_rate = (
                        len(made_shots) / len(filtered_shots) * 100
                        if len(filtered_shots) > 0
                        else 0
                    )
                    ax.text(
                        -200,
                        400,
                        f"FG: {len(made_shots)}/{len(filtered_shots)} ({shot_success_rate:.1f}%)",
                        fontsize=10,
                        bbox=dict(facecolor="white", alpha=0.7),
                    )

                ax.set_xlim(-250, 250)
                ax.set_ylim(422.5, -47.5)

                ax.set_xlabel("")
                ax.set_ylabel("")
                ax.set_xticks([])
                ax.set_yticks([])

                ax.legend(loc="lower right")

                st.pyplot(fig)
